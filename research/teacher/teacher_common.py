"""Independent, additive teacher pilot. Importing this module performs no work."""
from __future__ import annotations
import contextlib, datetime, hashlib, importlib.metadata, json, os, sys, tempfile, time
from pathlib import Path

STAGE=Path(__file__).resolve().parent
ROOT=STAGE.parent.parent
WORK=ROOT/'artifacts/teacher'
NB=ROOT/'notebooks/05_multilingual_teacher_pilot.ipynb'
LABELS=['ACL','MCL','Medial Meniscus','Lateral Meniscus','Medial OA','Lateral OA','PF OA','Effusion','Synovitis',"Baker's",'Contusion','Fracture']
STATES=['positive','negative','uncertain','conflict','context_only','unmentioned']
ARMS=['minimal_contract','domain_contract']
SOURCE_NAMES=['teacher_common.py','teacher_contract.py','teacher_runtime.py','teacher_pipeline.py','teacher_plots.py','run.py','tests.py','protocol.json','MODEL_PROVENANCE.json']
class Stop(RuntimeError): pass

def utc():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode()).hexdigest()
def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda:f.read(4*1024**2),b''):h.update(block)
    return h.hexdigest()
def read_json(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def atomic(path,data):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    if path.is_symlink():raise Stop('SYMLINK_DESTINATION_REJECTED')
    fd,tmp=tempfile.mkstemp(prefix='.'+path.name+'.',dir=path.parent)
    try:
        with os.fdopen(fd,'wb') as f:f.write(data);f.flush();os.fsync(f.fileno())
        os.chmod(tmp,0o600);os.replace(tmp,path)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
def save_json(path,value):atomic(path,json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False).encode())
def safe_path(base,relative):
    base=Path(base).resolve();rel=Path(relative)
    if rel.is_absolute() or '..' in rel.parts:raise Stop('UNSAFE_RELATIVE_PATH')
    p=base/rel
    if not p.resolve().is_relative_to(base):raise Stop('PATH_ESCAPES_BASE')
    for ancestor in [p,*p.parents]:
        if ancestor==base:break
        if ancestor.is_symlink():raise Stop('SYMLINK_PATH_REJECTED')
    return p

def source_map():return {name:sha(STAGE/name) for name in SOURCE_NAMES}
def notebook_source(nb):return digest([(c['cell_type'],''.join(c.get('source',[]))) for c in nb['cells']])
def environment():
    return {'python':sys.version.split()[0],**{n:importlib.metadata.version(n) for n in ('numpy','pandas','plotly','psutil','matplotlib','Pillow','ipykernel','nbformat')}}
def require_environment():
    expected=read_json(STAGE/'protocol.json')['environment']
    if Path(sys.prefix).resolve()!=(ROOT/'.venv').resolve():raise Stop('SELECT_EXISTING_RSNA_AUDIT_ENVIRONMENT')
    current=environment()
    if current!=expected:raise Stop('ENVIRONMENT_CHANGED_NO_AUTOMATIC_REPLACEMENT')
    return current

def require_tests():
    r=read_json(WORK/'tests.json')
    if r.get('status')!='passed' or not r.get('tests') or any(r.get(x)!=0 for x in ('failures','errors','skipped')):raise Stop('CURRENT_TEACHER_TESTS_REQUIRED')
    if r['source']!=source_map() or r['environment']!=environment():raise Stop('TEACHER_TEST_LINEAGE_CHANGED')
    return r

@contextlib.contextmanager
def lock(name):
    import fcntl
    WORK.mkdir(parents=True,exist_ok=True)
    with (WORK/(name+'.lock')).open('a') as f:
        try:fcntl.flock(f.fileno(),fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:raise Stop('ANOTHER_TEACHER_OPERATION_IS_RUNNING') from None
        try:yield
        finally:fcntl.flock(f.fileno(),fcntl.LOCK_UN)

class Progress:
    def __init__(self):self.started=time.monotonic()
    def log(self,event,**values):
        import psutil
        r={'utc':utc(),'event':event,'elapsed_seconds':round(time.monotonic()-self.started,3),'rss_gib':round(psutil.Process().memory_info().rss/1024**3,3),**values}
        WORK.mkdir(parents=True,exist_ok=True)
        with (WORK/'progress.jsonl').open('a') as f:f.write(json.dumps(r,allow_nan=False)+'\n')
        print(json.dumps(r,allow_nan=False),flush=True)

def previous():
    """Validate bytes already returned by the user; never rerun the prior study."""
    cfg=read_json(STAGE/'protocol.json');p=cfg['previous']
    old=ROOT/'research/supervision'
    for n,h in p['supervision_source'].items():
        if sha(safe_path(old,n))!=h:raise Stop('PREVIOUS_SUPERVISION_SOURCE_CHANGED')
    latest=read_json(ROOT/'artifacts/supervision/latest.json')
    if latest.get('key')!=p['key'] or latest.get('status')!='complete':raise Stop('PREVIOUS_SUPERVISION_NOT_COMPLETE')
    directory=safe_path(ROOT,latest['directory'])
    if not directory.is_relative_to(ROOT/'artifacts/supervision/runs'):raise Stop('PREVIOUS_RUN_DIRECTORY')
    checkpoint=read_json(directory/'CHECKPOINT.json')
    if checkpoint.get('key')!=p['key'] or checkpoint.get('files')!=p['checkpoint_files']:raise Stop('PREVIOUS_CHECKPOINT_CHANGED')
    for n,h in p['checkpoint_files'].items():
        if sha(safe_path(directory,n))!=h:raise Stop('PREVIOUS_CHECKPOINT_BYTES_CHANGED')
    for n,h in p['metadata_sha256'].items():
        if sha(safe_path(ROOT/'data/raw/metadata',n))!=h:raise Stop('METADATA_BYTES_CHANGED')
    evidence=read_json(ROOT/'artifacts/supervision/tests.json')
    if evidence.get('status')!='passed' or evidence.get('tests')!=80 or evidence.get('source')!=p['supervision_source']:raise Stop('PREVIOUS_TEST_RECEIPT_MISMATCH')
    if any(evidence.get(n)!=0 for n in ('errors','failures','skipped')):raise Stop('PREVIOUS_TEST_FAILURE')
    return directory,read_json(directory/'summary.json')
