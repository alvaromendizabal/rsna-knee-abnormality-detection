#!/usr/bin/env python3
"""User-run entry point; safe diagnostics contain no raw rows or report text."""
from pathlib import Path
import argparse
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_knee.audit import run
from rsna_knee.schema import ContractError
import traceback
from rsna_knee.runtime import atomic_json, utc
parser=argparse.ArgumentParser()
parser.add_argument('--stop-after',choices=['schema'])
args=parser.parse_args()
try:
    result=run(ROOT,args.stop_after)
    print(json.dumps(result,indent=2),flush=True)
except Exception as exc:
    # Never include exception payloads from CSV parsers, which can include report text.
    receipt={'utc':utc(),'status':'FAILED','exception_type':type(exc).__name__,
             'action':'Stop; inspect tests and whether all five metadata files exist. Do not retry unchanged.',
             'diagnostic':str(exc) if isinstance(exc,(ContractError,RuntimeError)) else 'Payload withheld to protect raw data.',
             'trace':[{'file':Path(f.filename).name,'line':f.lineno,'function':f.name} for f in traceback.extract_tb(exc.__traceback__)]}
    atomic_json(ROOT/'artifacts/m01_failure.json',receipt)
    print(json.dumps(receipt),flush=True)
    raise SystemExit(1)
