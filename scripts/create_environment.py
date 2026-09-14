#!/usr/bin/env python3
"""User-invoked setup: project-owned venv only, bounded to 600 seconds total."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time
ROOT=Path(__file__).resolve().parents[1]
if sys.version_info[:2] not in ((3,11),(3,12)):
    raise SystemExit('STOP: use a SageMaker Python 3.11/3.12 terminal; do not replace the base environment.')
VENV=ROOT/'.venv'; MARKER=ROOT/'.environment-owner.json'; REQUIREMENTS=ROOT/'requirements-audit.txt'
expected=hashlib.sha256(REQUIREMENTS.read_bytes()).hexdigest()
if VENV.exists():
    if not MARKER.exists() or json.loads(MARKER.read_text()).get('requirements_sha256')!=expected:
        raise SystemExit('STOP: existing .venv is not owned by this exact starter. Nothing replaced.')
else:
    if MARKER.exists(): raise SystemExit('STOP: setup marker exists without environment; inspect manually.')
started=time.monotonic()
logdir=ROOT/'logs/private'; logdir.mkdir(parents=True,exist_ok=True)
logpath=logdir/'environment_install.log'
with logpath.open('w',encoding='utf-8') as log:
    def command(args):
        remaining=600-(time.monotonic()-started)
        if remaining<=0: raise TimeoutError('Environment setup budget exhausted.')
        result=subprocess.run(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT,timeout=remaining)
        if result.returncode: raise RuntimeError('Dependency installation failed. Inspect private install log locally.')
    try:
        if not VENV.exists():
            command([sys.executable,'-m','venv',str(VENV)])
            MARKER.write_text(json.dumps({'requirements_sha256':expected,'project':'rsna-knee-abnormality-detection'}))
        py=str(VENV/'bin/python')
        print('Installing CPU audit dependencies into project .venv only; maximum total 600 seconds.',flush=True)
        command([py,'-m','pip','install','--disable-pip-version-check','--timeout','30','--retries','1',
                 '-r',str(REQUIREMENTS)])
        command([py,'-m','pip','check'])
        command([py,'-m','ipykernel','install','--user','--name','rsna-knee-audit',
                 '--display-name','RSNA Knee - audit'])
    except (RuntimeError,TimeoutError,subprocess.TimeoutExpired) as exc:
        print(type(exc).__name__+': STOP; see logs/private/environment_install.log locally. No tests or data downloads ran.')
        raise SystemExit(1)
print('Environment ready. Next: source .venv/bin/activate && python scripts/run_tests.py')
print('Direct versions are pinned; this is not a validated cross-platform transitive lock.')
