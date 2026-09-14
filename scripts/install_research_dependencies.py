#!/usr/bin/env python3
"""User-only: install the single optional image-reader pin into the existing venv."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_knee.runtime import run_bounded
if Path(sys.prefix).resolve()!=(ROOT/'.venv').resolve():
    raise SystemExit('Activate this project .venv first; the base environment will not be modified.')
run_bounded([sys.executable,'-m','pip','install','--disable-pip-version-check','--timeout','20',
             '--retries','0','-r','requirements-research.txt'],ROOT,seconds=180,rss_gib=2,
             log_path=ROOT/'logs/private/research_dependency_install.log')
print('Dependency step finished. Next run scripts/run_tests.py. No project tests were run by this installer.')
