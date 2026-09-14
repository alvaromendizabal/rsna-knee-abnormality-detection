#!/usr/bin/env python3
"""Foreground, user-invoked CLI. Safe return ZIP on success or recoverable failure."""
from __future__ import annotations
import argparse, base64, collections, contextlib, importlib.metadata, io, json, os, signal
import subprocess, sys, tempfile, time, traceback, unittest, zipfile
from pathlib import Path
from common import (ROOT,STAGE,WORK,NB,Stop,sha,digest,read_json,save_json,atomic,utc,
                    environment,source_map,require_environment,require_tests,notebook_source)


def run_foreground(command,seconds,logname):
    """Bound a child and its process group; print completed progress as emitted."""
    import psutil
    WORK.mkdir(parents=True,exist_ok=True)
    logpath=WORK/logname;start=time.monotonic()
    with logpath.open('wb') as sink:
        proc=subprocess.Popen(command,cwd=ROOT,stdout=sink,stderr=subprocess.STDOUT,
            start_new_session=True,env={**os.environ,'PYTHONUNBUFFERED':'1','MPLBACKEND':'Agg'})
        offset=0
        try:
            while True:
                with logpath.open('rb') as source:
                    source.seek(offset);b=source.read();offset+=len(b)
                if b:print(b.decode('utf-8',errors='replace'),end='',flush=True)
                if proc.poll() is not None:break
                if time.monotonic()-start>seconds:raise Stop('FOREGROUND_CHILD_TIMEOUT')
                try:
                    parent=psutil.Process(proc.pid);total=0
                    for p in [parent,*parent.children(recursive=True)]:
                        try:total+=p.memory_info().rss
                        except psutil.Error:pass
                    if total>4*1024**3:raise Stop('FOREGROUND_CHILD_MEMORY_CAP')
                except psutil.NoSuchProcess:pass
                time.sleep(.2)
            with logpath.open('rb') as source:
                source.seek(offset);b=source.read()
                if b:print(b.decode('utf-8',errors='replace'),end='',flush=True)
            if proc.returncode:raise Stop('FOREGROUND_CHILD_FAILED_SEE_DIAGNOSTIC')
        finally:
            if proc.poll() is None:
                try:os.killpg(proc.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    try:os.killpg(proc.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    proc.wait(timeout=3)


def prepare():
    if Path(sys.prefix).resolve()!=(ROOT/'.venv').resolve():raise Stop('ACTIVATE_EXISTING_PROJECT_VENV')
    # Test and preserve old code BEFORE any optional rendering installation.
    from pipeline import checked_previous,core_source_hash
    _,protected=checked_previous();before=core_source_hash()
    try:mpl=importlib.metadata.version('matplotlib')
    except importlib.metadata.PackageNotFoundError:mpl=None
    if mpl not in (None,'3.10.6'):raise Stop('OTHER_MATPLOTLIB_VERSION_PRESENT_NO_AUTOMATIC_REPLACEMENT')
    if mpl is None:
        print('Installing only the pinned PNG companion renderer and its wheel dependencies into the existing .venv.',flush=True)
        run_foreground([sys.executable,'-m','pip','install','--disable-pip-version-check','--only-binary=:all:',
            '--timeout','30','--retries','0','-c',str(STAGE/'constraints.txt'),'matplotlib==3.10.6'],180,'dependency.private.log')
    require_environment()
    if before!=core_source_hash() or any(sha(ROOT/p)!=h for p,h in protected.items()):raise Stop('PRIOR_RESEARCH_CHANGED_DURING_PREPARATION')
    run_foreground([sys.executable,str(STAGE/'run.py'),'_tests'],90,'tests.log')
    require_tests()
    print('SUPERVISION_PREPARE_COMPLETE\nNext: open notebooks/04_supervision_and_validation.ipynb with RSNA Knee - audit.',flush=True)


def execute_tests():
    import tests as local_tests
    from unittest.mock import patch
    def forbidden(*a,**k):raise AssertionError('Network is forbidden in synthetic tests')
    env=require_environment();suite=unittest.defaultTestLoader.loadTestsFromModule(local_tests)
    with patch('socket.create_connection',side_effect=forbidden):
        result=unittest.TextTestRunner(verbosity=2,stream=sys.stdout).run(suite)
    r={'utc':utc(),'status':'passed' if result.wasSuccessful() and not result.skipped else 'failed',
       'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),
       'source':source_map(),'environment':env,'network_requests':0,'real_reports_processed':0,'model_fits':0}
    save_json(WORK/'tests.json',r)
    if r['status']!='passed':raise Stop('SYNTHETIC_TEST_FAILURE')
    print('SUPERVISION_TESTS_PASSED',flush=True)


def launch_analysis():
    require_tests()
    run_foreground([sys.executable,str(STAGE/'run.py'),'_analyze'],210,'analysis.log')
    return read_json(WORK/'latest.json')


def safe_failure(exc,action):
    # No report, identifier, row values, URLs, credentials, environment values,
    # source lines or raw exception messages enter an exported diagnostic.
    frames=[{'file':Path(t.filename).name,'line':t.lineno,'function':t.name}
            for t in traceback.extract_tb(exc.__traceback__)]
    record={'utc':utc(),'action':action,'status':'failed','type':type(exc).__name__,
            'code':str(exc) if isinstance(exc,Stop) and str(exc).replace('_','').isalnum() else 'UNEXPECTED_EXCEPTION',
            'frames':frames,'private_text_exported':False}
    save_json(WORK/'failure.json',record)
    print('STOP:',record['code'],'(',record['type'],')',flush=True)
    return record


def validate_notebook(directory):
    expected=read_json(STAGE/'DELIVERY_MANIFEST.json')['notebook_source_sha256']
    if not NB.is_file() or NB.is_symlink():raise Stop('SAVE_NEW_NOTEBOOK_FIRST')
    nb=json.loads(NB.read_text(encoding='utf-8'))
    if notebook_source(nb)!=expected:raise Stop('NOTEBOOK_SOURCE_CHANGED_PRESERVE_EDITS')
    cells=[c for c in nb['cells'] if c['cell_type']=='code']
    if [c.get('execution_count') for c in cells]!=list(range(1,len(cells)+1)):raise Stop('NOTEBOOK_NOT_SAVED_AFTER_CLEAN_EXECUTION')
    outputs=[o for c in cells for o in c.get('outputs',[])]
    if any(o.get('output_type')=='error' for o in outputs):raise Stop('NOTEBOOK_ERROR_PRESENT')
    text=''.join(''.join(o.get('text',[])) for o in outputs if o.get('output_type')=='stream')
    if 'SUPERVISION_MILESTONE_COMPLETE' not in text:raise Stop('NOTEBOOK_COMPLETION_MARKER_NOT_SAVED')
    figures=read_json(directory/'figures/FIGURES.json')
    expected_specs=collections.Counter(v['numeric_spec_sha256'] for v in figures['figures'].values())
    expected_png=collections.Counter(v['files'][stem+'.png'] for stem,v in figures['figures'].items())
    specs=[];pngs=[]
    for o in outputs:
        data=o.get('data',{})
        if 'application/vnd.plotly.v1+json' in data:
            pl=data['application/vnd.plotly.v1+json'];specs.append(pl.get('layout',{}).get('meta',{}).get('numeric_spec_sha256'))
        if 'image/png' in data:
            value=data['image/png'];value=''.join(value) if isinstance(value,list) else value
            import hashlib
            pngs.append(hashlib.sha256(base64.b64decode(''.join(value.split()),validate=True)).hexdigest())
    if collections.Counter(specs)!=expected_specs or len(specs)!=12:raise Stop('SAVED_PLOTLY_FIGURES_DO_NOT_MATCH')
    if collections.Counter(pngs)!=expected_png or len(pngs)!=12:raise Stop('SAVED_PNG_FIGURES_DO_NOT_MATCH')
    return nb


def collect(diagnostic_only=False):
    """Always try an allowlisted snapshot; complete status requires every gate."""
    WORK.mkdir(parents=True,exist_ok=True);issues=[];paths={};directory=None
    for name in ['tests.json','latest.json','notebook_ready.json','failure.json','progress.jsonl']:
        p=WORK/name
        if p.is_file() and not p.is_symlink():paths['evidence/'+name]=p
    if not diagnostic_only:
        try:
            from pipeline import current_run
            from plots import finalize_figures
            directory,_=current_run();finalize_figures();validate_notebook(directory)
            paths['notebooks/'+NB.name]=NB
        except Exception as exc:
            safe_failure(exc,'collect');issues.append(read_json(WORK/'failure.json'))
            paths['evidence/failure.json']=WORK/'failure.json'
    else:issues.append({'code':'DIAGNOSTIC_SNAPSHOT_REQUESTED'})
    if directory is not None:
        for name in ['summary.json','lineage.json','DECISION.json','CHECKPOINT.json']:
            p=directory/name
            if p.is_file() and not p.is_symlink():
                # A checkpoint lists hashes of private paths, not their content.
                paths['analysis/'+name]=p
        fdir=directory/'figures'
        if fdir.exists():
            for p in fdir.iterdir():
                if p.is_file() and not p.is_symlink() and p.suffix in ('.png','.json','.html','.js'):
                    paths['figures/'+p.name]=p
    # Include executable source for diagnosis; it contains only templates and
    # synthetic tests. Do not glob the private analysis directory.
    for n in list(source_map())+['DELIVERY_MANIFEST.json','README.md','SOURCES.md','LLM_ANNOTATION_CONTRACT.md']:
        p=STAGE/n
        if p.is_file() and not p.is_symlink():paths['source/'+n]=p
    if any('.private' in n or n.startswith(('data/','.venv/')) for n in paths):raise Stop('RETURN_ALLOWLIST_VIOLATION')
    if sum(p.stat().st_size for p in paths.values())>40*1024**2:raise Stop('RETURN_SIZE_CAP')
    complete=not issues and not diagnostic_only
    manifest={'utc':utc(),'status':'complete' if complete else 'partial','issues':issues,
              'model_fits':0,'official_auc':None,'private_reports_included':False,'expert_outcomes_included':False,
              'source':source_map(),'files':{n:sha(p) for n,p in paths.items()},
              'plotly_and_png_count':12 if complete else None,'front_end_visibility':'requires user confirmation',
              'note':'Partial is a diagnostic snapshot, never a passed scientific result.'}
    returns=ROOT/'returns';returns.mkdir(exist_ok=True)
    destination=returns/'rsna-knee-supervision-return.zip'
    fd,tmp=tempfile.mkstemp(prefix='.supervision-return-',suffix='.zip',dir=returns);os.close(fd)
    try:
        with zipfile.ZipFile(tmp,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
            for name,p in paths.items():z.write(p,name)
            z.writestr('RETURN_MANIFEST.json',json.dumps(manifest,indent=2,allow_nan=False))
        with zipfile.ZipFile(tmp) as z:
            if z.testzip() is not None:raise Stop('RETURN_ZIP_CRC_FAILURE')
        if destination.exists():
            history=returns/'history';history.mkdir(exist_ok=True)
            backup=history/('supervision-'+str(time.time_ns())+'.zip');os.replace(destination,backup)
        os.replace(tmp,destination)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    print(('SUPERVISION_RETURN_READY' if complete else 'SUPERVISION_RETURN_PARTIAL')+': '+str(destination),flush=True)
    print('Archive bytes:',destination.stat().st_size,'| SHA256:',sha(destination),flush=True)
    return destination,complete


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=['prepare','collect','diagnose','_tests','_analyze'])
    action=parser.parse_args().action
    if sys.platform.startswith('linux'):
        def timedout(*a):raise Stop('MILESTONE_HARD_WALL_TIME_CAP')
        signal.signal(signal.SIGALRM,timedout)
        signal.alarm({'prepare':300,'collect':90,'diagnose':30,'_tests':80,'_analyze':180}[action])
    try:
        if action=='prepare':prepare()
        elif action=='_tests':execute_tests()
        elif action=='_analyze':
            from pipeline import run_analysis
            run_analysis()
        elif action=='collect':
            _,ok=collect();return 0 if ok else 2
        elif action=='diagnose':collect(diagnostic_only=True)
        return 0
    except Exception as exc:
        if hasattr(signal,'alarm'):signal.alarm(0)
        safe_failure(exc,action)
        if not action.startswith('_'):
            try:collect(diagnostic_only=True)
            except Exception as secondary:
                print('RETURN_WRITE_FAILED:',type(secondary).__name__,'. Preserve artifacts/supervision/failure.json.',flush=True)
        return 1
    finally:
        if hasattr(signal,'alarm'):signal.alarm(0)

if __name__=='__main__':raise SystemExit(main())
