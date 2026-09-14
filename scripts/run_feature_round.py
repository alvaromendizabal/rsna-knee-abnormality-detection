#!/usr/bin/env python3
"""Explicit user-run, local-only feature construction. No model fitting."""
from pathlib import Path
import argparse
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_research.workflow import round1,round2
from rsna_knee.runtime import atomic_json,utc
from rsna_knee.schema import ContractError
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--round',type=int,choices=[1,2],required=True)
p.add_argument('--pause-after',choices=['construction'])
p.add_argument('--series-limit',type=int,default=1)
a=p.parse_args()
try:
    result=round1(ROOT,a.pause_after) if a.round==1 else round2(ROOT,a.series_limit)
    print(json.dumps(result,indent=2))
except (KeyboardInterrupt,Exception) as exc:
    atomic_json(ROOT/f'artifacts/round{a.round}_failure.json',{'utc':utc(),'status':'STOP','exception_type':type(exc).__name__})
    # Clinical text/UIDs and raw DICOM exceptions must not be emitted into notebooks.
    print('STOP: '+str(exc) if isinstance(exc,ContractError) else 'STOP: unexpected local failure; inspect privately.')
    raise SystemExit(1)
