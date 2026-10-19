#!/usr/bin/env python3
"""Verify maintained source and final aggregate review without private inputs."""
from __future__ import annotations
import ast
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_review.evidence import verify_notebook

def main():
    names=subprocess.check_output(['git','-C',str(ROOT),'ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\0')
    checked=0
    for name in set(filter(None,names)):
        p=ROOT/name
        if p.is_file() and p.suffix=='.py':
            ast.parse(p.read_text(encoding='utf-8'),filename=name);checked+=1
    verify_notebook(ROOT)
    for name in ('test_image_models.py','test_current_frontier.py','test_employer_portfolio.py'):
        subprocess.run([sys.executable,'-S','-m','unittest','discover','-s','tests','-p',name,'-q'],cwd=ROOT,check=True,timeout=60)
    print('PUBLIC_QUALITY_PASSED',checked,'Python sources; final evidence and numerical contracts')
if __name__=='__main__':main()
