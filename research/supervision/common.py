"""Local-only evidence primitives for the independent supervision milestone."""
from __future__ import annotations
import contextlib, hashlib, importlib.metadata, json, os, platform, sys, tempfile, time
from pathlib import Path
from datetime import datetime, timezone

STAGE = Path(__file__).resolve().parent
ROOT = STAGE.parent.parent
WORK = ROOT / 'artifacts' / 'supervision'
NB = ROOT / 'notebooks' / '04_supervision_and_validation.ipynb'
LABELS = ['ACL','MCL','Medial Meniscus','Lateral Meniscus','Medial OA','Lateral OA',
          'PF OA','Effusion','Synovitis',"Baker's",'Contusion','Fracture']
STATES = ['positive','negative','uncertain','conflict','context_only','unmentioned']
ARMS = ['mention_only','joint_context','joint_no_negation','joint_no_uncertainty','joint_no_context_gate']

class Stop(RuntimeError):
    """Fixed, non-sensitive error messages only; never insert a report or UID."""

def utc(): return datetime.now(timezone.utc).isoformat()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024**2),b''): h.update(chunk)
    return h.hexdigest()
def digest(value):
    return hashlib.sha256(json.dumps(value,sort_keys=True,ensure_ascii=True,allow_nan=False).encode()).hexdigest()
def atomic(path, payload):
    path=Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink(): raise Stop('SYMLINK_OUTPUT_REFUSED')
    fd,tmp=tempfile.mkstemp(prefix='.pending-',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:
            f.write(payload);f.flush();os.fsync(f.fileno())
        os.replace(tmp,path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
def save_json(path,value):
    atomic(path,(json.dumps(value,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode())
def read_json(path):
    p=Path(path)
    if p.is_symlink() or not p.is_file() or p.stat().st_size>64*1024**2: raise Stop('JSON_INPUT_MISSING_OR_UNSAFE')
    return json.loads(p.read_text(encoding='utf-8'))
def source_map():
    names=['common.py','labels.py','pipeline.py','plots.py','run.py','tests.py','protocol.json','target_contract.json','constraints.txt']
    return {n:sha(STAGE/n) for n in names}
def environment():
    result={'python':platform.python_version()}
    for n in ['numpy','pandas','plotly','psutil','matplotlib','Pillow','ipykernel','nbformat']:
        try: result[n]=importlib.metadata.version(n)
        except importlib.metadata.PackageNotFoundError: result[n]='NOT_INSTALLED'
    return result
def notebook_source(nb):
    return digest([[c['cell_type'],''.join(c.get('source',[]))] for c in nb.get('cells',[])])
def require_environment():
    if Path(sys.prefix).resolve()!=(ROOT/'.venv').resolve(): raise Stop('SELECT_RSNA_KNEE_AUDIT_ENVIRONMENT')
    if sys.version_info[:2] not in [(3,11),(3,12)]: raise Stop('PYTHON_VERSION_UNSUPPORTED')
    e=environment()
    for n,v in [('numpy','2.2.6'),('pandas','2.3.3'),('plotly','6.3.0'),('matplotlib','3.10.6')]:
        if e.get(n)!=v: raise Stop('PINNED_DEPENDENCIES_NOT_READY_RUN_PREPARE')
    return e
def require_tests():
    e=require_environment();r=read_json(WORK/'tests.json')
    if r.get('status')!='passed' or r.get('tests',0)<1 or any(r.get(k)!=0 for k in ('failures','errors','skipped')):
        raise Stop('CURRENT_SUPERVISION_TESTS_REQUIRED')
    if r.get('source')!=source_map() or r.get('environment')!=e: raise Stop('SUPERVISION_TEST_LINEAGE_CHANGED')
    return r
@contextlib.contextmanager
def lock(name):
    import fcntl
    WORK.mkdir(parents=True,exist_ok=True)
    with (WORK/(name+'.lock')).open('a') as f:
        try: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError as exc: raise Stop('ANOTHER_MILESTONE_PROCESS_IS_RUNNING') from exc
        try:yield
        finally:fcntl.flock(f,fcntl.LOCK_UN)
class Progress:
    def __init__(self,seconds=180):
        self.start=self.stage_start=time.monotonic();self.stage=None;self.seconds=seconds
    def log(self,stage,completed,total,event='working'):
        import psutil
        now=time.monotonic()
        if self.stage!=stage:self.stage,self.stage_start=stage,now
        rss=psutil.Process().memory_info().rss
        if now-self.start>self.seconds:raise Stop('ANALYSIS_WALL_TIME_CAP')
        if rss>4*1024**3:raise Stop('ANALYSIS_MEMORY_CAP')
        record={'utc':utc(),'stage':stage,'event':event,'completed':int(completed),'total':int(total),
                'elapsed_seconds':round(now-self.start,3),'stage_seconds':round(now-self.stage_start,3),
                'rss_mib':round(rss/1024**2,1)}
        print(json.dumps(record),flush=True)
        WORK.mkdir(parents=True,exist_ok=True)
        with (WORK/'progress.jsonl').open('a',encoding='utf-8') as f:f.write(json.dumps(record)+'\n')
def checkpoint(directory,key):
    p=Path(directory)/'CHECKPOINT.json'
    if not p.exists():return False
    m=read_json(p)
    if m.get('key')!=key or m.get('status')!='complete' or not m.get('files'):raise Stop('CHECKPOINT_LINEAGE_MISMATCH')
    for name,expected in m['files'].items():
        rel=Path(name)
        if rel.is_absolute() or '..' in rel.parts:raise Stop('CHECKPOINT_PATH_INVALID')
        f=Path(directory)/rel
        if f.is_symlink() or not f.is_file() or sha(f)!=expected:raise Stop('CHECKPOINT_BYTES_CHANGED')
    return True
