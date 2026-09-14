#!/usr/bin/env python3
"""User-run LOCAL Git inventory only. No fetch, clone, push, commit, merge, or edits."""
from pathlib import Path
import argparse
import json
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_knee.runtime import atomic_json,utc
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--directory',type=Path,default=ROOT)
a=p.parse_args(); directory=a.directory.expanduser().resolve()
def git(*args):
    r=subprocess.run(['git','-C',str(directory),*args],capture_output=True,text=True,timeout=30)
    return r.returncode,r.stdout
result={'utc':utc(),'scope':'local_only_remote_state_unverified','directory_name':directory.name,
        'account_operations':False,'history_scan_complete':False}
try:
    code,_=git('rev-parse','--git-dir')
    if code:
        result.update(is_git_repository=False,publication_action='Use a separate showcase clone; do not initialize/push the whole AWS workspace.')
    else:
        code,status=git('status','--porcelain=v1','--untracked-files=normal')
        result.update(is_git_repository=True,working_tree_dirty=bool(status.strip()),status_lines=status.splitlines())
        _,branch=git('branch','--show-current'); result['branch']=branch.strip()
        _,head=git('rev-parse','--verify','HEAD'); result['head']=head.strip() if len(head.strip())==40 else None
        # No remote URLs are read/printed: configured URLs can contain secrets.
        _,remotes=git('remote'); result['remote_names']=remotes.splitlines()
        r=subprocess.run(['git','-C',str(directory),'rev-list','--objects','--all'],capture_output=True,text=True,timeout=30)
        if r.returncode==0 and len(r.stdout)<=10*1024**2:
            suspicious=[]
            for line in r.stdout.splitlines():
                path=line.split(' ',1)[1] if ' ' in line else ''
                if path and (Path(path).suffix in {'.py','.ipynb','.dcm','.parquet','.pkl','.pt','.pth','.csv'}
                    or any(x in Path(path).parts for x in ('data','artifacts','.venv','src','checkpoints'))
                    or Path(path).name in {'.env','kaggle.json'}): suspicious.append(path)
            result.update(history_scan_complete=True,possible_private_history_paths=sorted(set(suspicious)),
                history_review_required=bool(suspicious),visibility_and_remote_history_unverified=True)
        else: result['history_review_required']=True
        result['license_review_required']=any((directory/n).exists() for n in ('LICENSE','LICENSE.md','LICENSE.txt','COPYING'))
except Exception as exc:
    result.update(status='STOP',exception_type=type(exc).__name__,history_review_required=True)
atomic_json(ROOT/'artifacts/publication_inventory.json',result)
print(json.dumps(result,indent=2))
print('No Git changes made. This is not a remote visibility/security audit.')
