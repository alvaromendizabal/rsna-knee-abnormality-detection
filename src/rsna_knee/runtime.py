"""Atomic stage evidence and bounded memory telemetry for public integrity tests."""
from __future__ import annotations
import hashlib,json,os,tempfile,time
from pathlib import Path
from datetime import datetime,timezone
import psutil

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

def current_rss_bytes() -> int:
    """Read resident memory, including Linux sandboxes with remapped process IDs."""
    try:
        return psutil.Process().memory_info().rss
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        # /proc/self resolves in the kernel even when the visible PID namespace
        # disagrees with os.getpid(). Keep the memory gate active on that path.
        try:
            resident_pages = int(Path('/proc/self/statm').read_text().split()[1])
            page_size = os.sysconf('SC_PAGE_SIZE')
            if resident_pages < 0 or page_size <= 0:
                raise ValueError('Invalid resident memory measurement')
            return resident_pages * page_size
        except (OSError, ValueError, IndexError) as exc:
            raise RuntimeError('Resident memory telemetry is unavailable; audit stopped.') from exc

class Progress:
    def __init__(self, path: Path, seconds=120, rss_gib=4):
        self.path, self.seconds, self.rss_gib = path, seconds, rss_gib
        self.start = self.stage_start = time.monotonic(); self.stage = None
        path.parent.mkdir(parents=True, exist_ok=True)
    def log(self, stage: str, event: str, completed=0, total=0):
        now = time.monotonic()
        if stage != self.stage: self.stage, self.stage_start = stage, now
        rss = current_rss_bytes() / 1024**3
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
