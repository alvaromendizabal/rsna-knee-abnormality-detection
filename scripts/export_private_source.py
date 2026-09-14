#!/usr/bin/env python3
"""User-run local source snapshot; strips notebook outputs, never uses Git/network."""
from pathlib import Path
import argparse
import json
import re
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_knee.runtime import require_tests,sha256,atomic_json,utc
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=Path.home()/'rsna-knee-abnormality-detection-private-export')
a=p.parse_args(); require_tests(ROOT)
out=a.output.expanduser().absolute()
if out.exists() or out.is_relative_to(ROOT): raise SystemExit('STOP: choose a new, separate snapshot directory; never overwrite the workspace.')
allowed=[]
for folder,extensions in {'src':{'.py'},'scripts':{'.py'},'tests':{'.py'},'configs':{'.json','.csv'},'docs':{'.md'},'notebooks':{'.ipynb'}}.items():
    for path in (ROOT/folder).rglob('*'):
        if path.is_file() and path.suffix in extensions and '__pycache__' not in path.parts: allowed.append(path)
for name in ('requirements-audit.txt','requirements-research.txt','pytest.ini','README.md','NEXT_STEPS.md',
             'ARTIFACT_MANIFEST.json','RESEARCH_ARTIFACT_MANIFEST.json','RESEARCH_STATIC_REVIEW.json'):
    path=ROOT/name
    if path.is_file(): allowed.append(path)
prepared={}
for path in allowed:
    if path.is_symlink() or path.stat().st_size>10*1024**2: raise SystemExit('STOP: unsafe/oversized source file.')
    text=path.read_text(encoding='utf-8')
    if path.suffix=='.ipynb':
        doc=json.loads(text)
        for cell in doc['cells']:
            if cell['cell_type']=='code': cell['outputs']=[]; cell['execution_count']=None
            cell.pop('attachments',None)
        # Keep only standard kernel/language metadata; strip widget/output state.
        doc['metadata']={k:v for k,v in doc['metadata'].items() if k in {'kernelspec','language_info'}}
        text=json.dumps(doc,indent=1,ensure_ascii=False)+'\n'
    if re.search(r'(?:AKIA[0-9A-Z]{16}|gh[pousr]_[A-Za-z0-9]{20,}|-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|X-(?:Amz|Goog)-Signature=[0-9a-fA-F]{24,})',text):
        raise SystemExit('STOP: possible embedded secret in source; inspect locally before snapshotting.')
    prepared[str(path.relative_to(ROOT))]=text
# Publication templates are intentional source inputs, not private runtime artifacts.
for path in (ROOT/'portfolio').rglob('*'):
    if path.is_file() and (path.suffix=='.md' or path.name=='.gitignore'):
        if path.is_symlink(): raise SystemExit('STOP: unsafe template.')
        prepared[str(path.relative_to(ROOT))]=path.read_text()
prepared['.gitignore']='''data/\nartifacts/\nlogs/\nreturns/\n.venv/\n__pycache__/\n.pytest_cache/\n.ipynb_checkpoints/\n*.pyc\n.env\nkaggle.json\n*.dcm\n*.pkl\n*.pt\n*.pth\n'''
out.mkdir(parents=True)
for relative,text in prepared.items():
    dest=out/relative; dest.parent.mkdir(parents=True,exist_ok=True); dest.write_text(text,encoding='utf-8')
atomic_json(out/'PRIVATE_SNAPSHOT.json',{'utc':utc(),'files':{n:sha256(out/n) for n in sorted(prepared)},
    'purpose':'private source only','notebook_outputs_stripped':True,'raw_data_included':False,
    'git_history_included':False,'remote_visibility_verified':False,'uploaded':False,
    'review_required':'Review code cells, markdown, configs and licenses for proprietary third-party content and secrets.'})
print('PRIVATE_SOURCE_SNAPSHOT_READY. Read every staged file; do not push until the destination is verified Private.')
print(str(out))
