"""User entry point: prepare, analyze, collect, diagnose. No work on import."""
from __future__ import annotations
import base64,collections,json,os,signal,subprocess,sys,tempfile,time,traceback,unittest,zipfile
from pathlib import Path
from teacher_common import ROOT,STAGE,WORK,NB,Stop,atomic,save_json,read_json,sha,source_map,notebook_source,require_environment,require_tests,environment,previous,utc,lock


def failure(exc,action):
    code=str(exc) if isinstance(exc,Stop) and str(exc).replace('_','').isalnum() else 'UNEXPECTED_'+type(exc).__name__.upper()
    record={'utc':utc(),'status':'failed','action':action,'code':code,'type':type(exc).__name__,
            'frames':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(exc.__traceback__)],
            'private_text_exported':False}
    save_json(WORK/'failure.json',record);print('STOP:',code,flush=True);return record

def foreground(action,seconds,memory_gib=10):
    """One foreground subprocess group; kill all children on timeout or interruption."""
    import psutil
    from teacher_runtime import _death_signal
    WORK.mkdir(parents=True,exist_ok=True);log=WORK/(action.lstrip('_')+'.log');start=time.monotonic();offset=0
    with log.open('wb') as sink:
        proc=subprocess.Popen([sys.executable,str(STAGE/'run.py'),action],cwd=ROOT,stdout=sink,stderr=subprocess.STDOUT,
            start_new_session=True,preexec_fn=_death_signal,env={**os.environ,'PYTHONUNBUFFERED':'1','MPLBACKEND':'Agg'})
        try:
            while True:
                with log.open('rb') as f:f.seek(offset);b=f.read();offset+=len(b)
                if b:print(b.decode(errors='replace'),end='',flush=True)
                if proc.poll() is not None:break
                if time.monotonic()-start>seconds:raise Stop('FOREGROUND_WALL_TIME_LIMIT')
                try:
                    ps=psutil.Process(proc.pid);total=0
                    for child in [ps,*ps.children(recursive=True)]:
                        try:total+=child.memory_info().rss
                        except psutil.Error:pass
                    if total>memory_gib*1024**3:raise Stop('FOREGROUND_MEMORY_LIMIT')
                except psutil.NoSuchProcess:pass
                time.sleep(.25)
            with log.open('rb') as f:
                f.seek(offset);b=f.read()
                if b:print(b.decode(errors='replace'),end='',flush=True)
            if proc.returncode:raise Stop('WORKER_FAILED_DIAGNOSTIC_SAVED')
        finally:
            if proc.poll() is None:
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    proc.wait(timeout=5)

def execute_tests():
    import tests as suite_module
    from unittest.mock import patch
    def forbidden(*a,**k):raise AssertionError('External network and native inference are forbidden in synthetic tests')
    env=require_environment();suite=unittest.defaultTestLoader.loadTestsFromModule(suite_module)
    with patch('urllib.request.OpenerDirector.open',side_effect=forbidden),patch('subprocess.Popen',side_effect=forbidden):
        result=unittest.TextTestRunner(verbosity=2,stream=sys.stdout).run(suite)
    receipt={'utc':utc(),'status':'passed' if result.wasSuccessful() and not result.skipped else 'failed','tests':result.testsRun,
        'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'source':source_map(),'environment':env,
        'network_requests':0,'model_inference_calls':0,'real_reports_processed':0}
    save_json(WORK/'tests.json',receipt)
    if receipt['status']!='passed':raise Stop('TEACHER_SYNTHETIC_TEST_FAILURE')
    print('TEACHER_TESTS_PASSED',flush=True)

def prepare():
    require_environment();previous()
    foreground('_tests',90,4);require_tests()
    with lock('setup'):
        foreground('_assets',720,4)
    r=read_json(WORK/'prepared.json');r['source']=source_map();r['environment']=environment();save_json(WORK/'prepared.json',r)
    print('TEACHER_PREPARE_COMPLETE\nNext: notebook 05. No real report has been sent to a model during preparation.',flush=True)

def launch_analysis():
    require_environment();require_tests();previous()
    prepared=read_json(WORK/'prepared.json')
    if prepared.get('source')!=source_map() or prepared.get('environment')!=environment():raise Stop('CURRENT_MODEL_PREPARATION_REQUIRED')
    foreground('_analyze',900,10)
    return read_json(WORK/'latest.json')

def validate_notebook(directory):
    expected=read_json(STAGE/'DELIVERY_MANIFEST.json')['notebook_source_sha256']
    if NB.is_symlink() or not NB.is_file():raise Stop('SAVE_NOTEBOOK_05_FIRST')
    nb=read_json(NB)
    if notebook_source(nb)!=expected:raise Stop('NOTEBOOK_05_SOURCE_CHANGED')
    cells=[c for c in nb['cells'] if c['cell_type']=='code']
    if [c.get('execution_count') for c in cells]!=list(range(1,len(cells)+1)):raise Stop('SAVE_CLEAN_NOTEBOOK_EXECUTION')
    outputs=[o for c in cells for o in c.get('outputs',[])]
    if any(o.get('output_type')=='error' for o in outputs):raise Stop('NOTEBOOK_ERROR_PRESENT')
    text=''.join(''.join(o.get('text',[])) for o in outputs if o.get('output_type')=='stream')
    if 'TEACHER_PILOT_RECORDED' not in text:raise Stop('NOTEBOOK_COMPLETION_NOT_SAVED')
    figures=read_json(directory/'figures/FIGURES.json')
    expected_specs=collections.Counter(v['numeric_spec_sha256'] for v in figures['figures'].values())
    expected_pngs=collections.Counter(v['files'][k+'.png'] for k,v in figures['figures'].items());specs=[];pngs=[]
    import hashlib
    for o in outputs:
        data=o.get('data',{})
        if 'application/vnd.plotly.v1+json' in data:specs.append(data['application/vnd.plotly.v1+json'].get('layout',{}).get('meta',{}).get('numeric_spec_sha256'))
        if 'image/png' in data:
            x=data['image/png'];x=''.join(x) if isinstance(x,list) else x
            pngs.append(hashlib.sha256(base64.b64decode(''.join(x.split()),validate=True)).hexdigest())
    if len(specs)!=12 or collections.Counter(specs)!=expected_specs:raise Stop('SAVED_PLOTLY_MISMATCH')
    if len(pngs)!=12 or collections.Counter(pngs)!=expected_pngs:raise Stop('SAVED_PNG_MISMATCH')
    return nb

def collect(diagnostic=False):
    """Attempt one allowlisted ZIP even on blocked model/renderer/runtime results."""
    WORK.mkdir(parents=True,exist_ok=True);paths={};issues=[];directory=None;summary={}
    for n in ['tests.json','prepared.json','model.json','runtime.json','latest.json','failure.json','progress.jsonl']:
        p=WORK/n
        if p.is_file() and not p.is_symlink():paths['evidence/'+n]=p
    # No shell logs, model weights, inputs, model outputs, quotes or private selections.
    if not diagnostic:
        try:
            from teacher_pipeline import current_run
            from teacher_plots import finalize_figures
            directory,summary=current_run();finalize_figures();validate_notebook(directory)
            paths['notebooks/'+NB.name]=NB
        except Exception as exc:
            issues.append(failure(exc,'collect'));paths['evidence/failure.json']=WORK/'failure.json'
    else:issues.append({'code':'DIAGNOSTIC_SNAPSHOT_REQUESTED'})
    if directory is None and (WORK/'latest.json').exists():
        try:
            from teacher_common import safe_path
            candidate=safe_path(ROOT,read_json(WORK/'latest.json')['directory'])
            if candidate.is_relative_to(WORK/'runs'):directory=candidate
        except Exception:pass
    if directory is not None:
        for n in ['summary.json','lineage.json','DECISION.json','CHECKPOINT.json']:
            p=directory/n
            if p.is_file() and not p.is_symlink():paths['analysis/'+n]=p
        if not summary and (directory/'summary.json').is_file():summary=read_json(directory/'summary.json')
        figure_dir=directory/'figures'
        if figure_dir.exists():
            for p in figure_dir.iterdir():
                if p.is_file() and not p.is_symlink() and p.suffix in ('.png','.json','.html','.js'):paths['figures/'+p.name]=p
    for n in [*source_map(),'DELIVERY_MANIFEST.json','README.md','SOURCES.md','REVIEW_PROTOCOL.md']:
        p=STAGE/n
        if p.is_file() and not p.is_symlink():paths['source/'+n]=p
    if any('.private' in name for name in paths):raise Stop('PRIVATE_RETURN_PATH_REJECTED')
    if sum(p.stat().st_size for p in paths.values())>48*1024**2:raise Stop('RETURN_SIZE_CAP')
    manifest={'utc':utc(),'status':'complete' if not issues else 'partial','issues':issues,'pilot_outcome':summary.get('status','not_recorded'),
        'clinical_accuracy':None,'official_auc':None,'training_targets_approved':False,'raw_reports_included':False,'model_responses_included':False,
        'model_fits':0,'files':{n:sha(p) for n,p in paths.items()},'note':'Complete packaging is not proof of clinical accuracy or an improved model.'}
    returns=ROOT/'returns';returns.mkdir(exist_ok=True);destination=returns/'rsna-knee-teacher-return.zip'
    fd,tmp=tempfile.mkstemp(prefix='.teacher-return-',suffix='.zip',dir=returns);os.close(fd)
    try:
        with zipfile.ZipFile(tmp,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for n,p in paths.items():z.write(p,n)
            z.writestr('RETURN_MANIFEST.json',json.dumps(manifest,indent=2,allow_nan=False))
        with zipfile.ZipFile(tmp) as z:
            if z.testzip() is not None:raise Stop('RETURN_ZIP_CRC_FAILURE')
        if destination.exists():
            backup=returns/'history'/('teacher-'+sha(destination)[:16]+'.zip');backup.parent.mkdir(exist_ok=True)
            if not backup.exists():atomic(backup,destination.read_bytes())
        os.replace(tmp,destination)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print(('TEACHER_RETURN_READY' if not issues else 'TEACHER_RETURN_PARTIAL')+': '+str(destination),flush=True)
    print('Pilot outcome:',manifest['pilot_outcome'],'| No training-target approval or AUC claim.',flush=True)
    return manifest

def main():
    if len(sys.argv)!=2 or sys.argv[1] not in ('prepare','analyze','collect','diagnose','_tests','_assets','_analyze'):
        print('Usage: python research/teacher/run.py prepare|analyze|collect|diagnose');return 2
    action=sys.argv[1];WORK.mkdir(parents=True,exist_ok=True)
    # A second guard also bounds top-level command execution. Linux is required.
    cap={'prepare':850,'analyze':940,'collect':90,'diagnose':90,'_tests':85,'_assets':700,'_analyze':880}[action]
    def timed_out(*args):raise Stop('COMMAND_WALL_TIME_LIMIT')
    signal.signal(signal.SIGALRM,timed_out);signal.alarm(cap)
    try:
        if action=='prepare':prepare()
        elif action=='analyze':launch_analysis()
        elif action=='collect':collect()
        elif action=='diagnose':collect(True)
        elif action=='_tests':execute_tests()
        elif action=='_assets':
            from teacher_runtime import prepare_assets
            prepare_assets()
        else:
            from teacher_pipeline import analyze
            analyze()
        return 0
    except (Exception,KeyboardInterrupt) as exc:
        signal.alarm(0);failure(exc,action)
        if not action.startswith('_'):
            try:collect(True)
            except Exception as second:failure(second,'diagnostic_collection')
        return 1
    finally:signal.alarm(0)

if __name__=='__main__':raise SystemExit(main())
