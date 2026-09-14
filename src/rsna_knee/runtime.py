"""Local-only evidence, safe writes, and bounded subprocesses; no cloud SDK calls."""
from __future__ import annotations
import contextlib
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import platform
import selectors
import signal
import subprocess
import sys
import tempfile
import time
from datetime import datetime, timezone
import psutil

PACKAGES = ('numpy', 'pandas', 'plotly', 'psutil', 'pytest', 'ipykernel', 'nbformat', 'kaggle')

def utc() -> str:
    return datetime.now(timezone.utc).isoformat()

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()

def digest(value) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, ensure_ascii=True,
                                    allow_nan=False).encode()).hexdigest()

def atomic_json(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.pending-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(value, f, indent=2, ensure_ascii=True, allow_nan=False)
            f.write('\n'); f.flush(); os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)

def atomic_csv(path: Path, frame, *, index=False) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.pending-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='') as f:
            frame.to_csv(f, index=index); f.flush(); os.fsync(f.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)

def versions() -> dict:
    result = {'python': platform.python_version()}
    for name in PACKAGES:
        try: result[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError: result[name] = 'NOT_INSTALLED'
    return result

def source_hash(root: Path) -> str:
    paths = []
    for folder in ('src', 'scripts', 'tests', 'configs'):
        paths += [p for p in (root / folder).rglob('*') if p.is_file()
                  and p.suffix in ('.py', '.sh', '.json', '.csv') and '__pycache__' not in p.parts]
    paths += [root / 'requirements-audit.txt', root / 'pytest.ini']
    return digest({str(p.relative_to(root)): sha256(p) for p in sorted(paths)})

@contextlib.contextmanager
def exclusive_lock(path: Path):
    import fcntl
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('a') as f:
        try: fcntl.flock(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError as exc: raise RuntimeError('Another local run owns this milestone lock.') from exc
        try: yield
        finally: fcntl.flock(f, fcntl.LOCK_UN)

class Progress:
    def __init__(self, path: Path, seconds=120, rss_gib=4):
        self.path, self.seconds, self.rss_gib = path, seconds, rss_gib
        self.start = self.stage_start = time.monotonic(); self.stage = None
        path.parent.mkdir(parents=True, exist_ok=True)
    def log(self, stage: str, event: str, completed=0, total=0):
        now = time.monotonic()
        if stage != self.stage: self.stage, self.stage_start = stage, now
        rss = psutil.Process().memory_info().rss / 1024**3
        if now - self.start > self.seconds or rss > self.rss_gib:
            raise RuntimeError('Audit elapsed-time or memory limit reached; completed stages remain intact.')
        item = dict(utc=utc(), stage=stage, event=event, completed=int(completed), total=int(total),
                    total_elapsed_s=round(now-self.start, 3), stage_elapsed_s=round(now-self.stage_start, 3),
                    rss_gib=round(rss, 3))
        line = json.dumps(item); print(line, flush=True)
        with self.path.open('a', encoding='utf-8') as f: f.write(line+'\n')

class StageCache:
    def __init__(self, directory: Path, key: str):
        self.directory, self.key = directory, key
        directory.mkdir(parents=True, exist_ok=True)
    def reuse(self, stage: str) -> bool:
        path = self.directory / f'{stage}.manifest.json'
        if not path.exists(): return False
        value = json.loads(path.read_text())
        if value.get('key') != self.key or value.get('status') != 'complete' or not value.get('files'):
            raise RuntimeError('Stage provenance mismatch. Preserve files; do not reuse or silently refit.')
        for relative, expected in value['files'].items():
            p = self.directory / relative
            if p.is_symlink() or not p.is_file() or p.resolve().parent != self.directory.resolve() or sha256(p) != expected:
                raise RuntimeError('Checkpoint integrity failure. Preserve evidence and stop.')
        return True
    def commit(self, stage: str, paths: list[Path]):
        atomic_json(self.directory / f'{stage}.manifest.json', dict(key=self.key, status='complete',
            utc=utc(), files={p.name: sha256(p) for p in paths}))

def require_tests(root: Path) -> dict:
    path = root/'artifacts/test_receipt.json'
    if not path.is_file(): raise RuntimeError('First run: python scripts/run_tests.py')
    r = json.loads(path.read_text())
    if not (r.get('returncode') == 0 and r.get('tests', 0) > 0 and r.get('failures') == 0
            and r.get('errors') == 0 and r.get('skipped') == 0):
        raise RuntimeError('Tests did not pass completely. Stop and return the test output.')
    if r.get('source_hash') != source_hash(root) or r.get('environment_hash') != digest(versions()):
        raise RuntimeError('Code/configuration/environment changed since testing. Run tests again.')
    if r.get('junit_sha256') != sha256(root/'artifacts/tests.xml'):
        raise RuntimeError('Test evidence changed. Stop and inspect it.')
    return r

def _terminate(process):
    if process.poll() is not None: return
    try: os.killpg(process.pid, signal.SIGTERM)
    except ProcessLookupError: return
    try: process.wait(timeout=3)
    except subprocess.TimeoutExpired:
        try: os.killpg(process.pid, signal.SIGKILL)
        except ProcessLookupError: pass
        process.wait(timeout=3)

def run_bounded(command: list[str], root: Path, *, seconds=180, rss_gib=4,
                log_path: Path | None = None) -> int:
    """Run only when the user executes the calling cell/script. No detached jobs."""
    started = time.monotonic()
    if log_path: log_path.parent.mkdir(parents=True, exist_ok=True)
    with contextlib.ExitStack() as stack:
        log = stack.enter_context(log_path.open('w', encoding='utf-8')) if log_path else None
        p = subprocess.Popen(command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            start_new_session=True, env={**os.environ, 'PYTHONUNBUFFERED': '1'})
        selector = selectors.DefaultSelector(); selector.register(p.stdout, selectors.EVENT_READ)
        try:
            while selector.get_map():
                if time.monotonic()-started > seconds:
                    raise TimeoutError(f'Local worker exceeded {seconds} seconds; do not retry unchanged.')
                try:
                    parent = psutil.Process(p.pid)
                    processes = [parent, *parent.children(recursive=True)]
                    rss = 0
                    for child in processes:
                        try: rss += child.memory_info().rss
                        except psutil.Error: pass
                    if rss > rss_gib*1024**3: raise MemoryError('Local worker exceeded RSS cap.')
                except (psutil.NoSuchProcess, psutil.AccessDenied): pass
                for key, _ in selector.select(timeout=0.2):
                    chunk = os.read(key.fileobj.fileno(), 65536)
                    if not chunk: selector.unregister(key.fileobj); continue
                    text = chunk.decode('utf-8', errors='replace')
                    print(text, end='', flush=True)
                    if log: log.write(text); log.flush()
            code = p.wait(timeout=5)
            if code: raise RuntimeError(f'Local worker failed with exit code {code}; stop at this gate.')
            return code
        finally:
            selector.close(); _terminate(p)
            if p.stdout: p.stdout.close()

def inventory(root: Path) -> dict:
    disk = psutil.disk_usage(root); memory = psutil.virtual_memory()
    value = dict(utc=utc(), python=platform.python_version(), logical_cpus=psutil.cpu_count(),
        total_ram_gib=round(memory.total/1024**3, 2), available_ram_gib=round(memory.available/1024**3, 2),
        disk_total_gib=round(disk.total/1024**3, 2), disk_free_gib=round(disk.free/1024**3, 2),
        disk_used_gib=round(disk.used/1024**3, 2), versions=versions(), source_hash=source_hash(root),
        account_inspected=False, instance_name_verified=False, model_fits=0)
    if sys.version_info[:2] not in ((3,11), (3,12)):
        raise RuntimeError('This starter targets Python 3.11 or 3.12. Do not replace the base environment.')
    if disk.free < 5*1024**3 or memory.available < 2*1024**3:
        raise RuntimeError('Need at least 5 GiB free disk and 2 GiB available RAM for this audit.')
    atomic_json(root/'artifacts/preflight.json', value)
    return value
