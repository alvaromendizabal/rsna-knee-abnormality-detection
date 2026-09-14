#!/usr/bin/env python3
"""Run synthetic tests on the user's explicit invocation. No remote operations."""
import json
from pathlib import Path
import sys
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_knee.runtime import atomic_json,digest,run_bounded,sha256,source_hash,utc,versions
(ROOT/'artifacts').mkdir(exist_ok=True)
receipt=dict(utc=utc(),returncode=1,tests=0,failures=0,errors=0,skipped=0,
             source_hash=source_hash(ROOT),environment_hash=digest(versions()),status='started')
atomic_json(ROOT/'artifacts/test_receipt.json',receipt)
try:
    run_bounded([sys.executable,'-m','pytest','-q','--junitxml=artifacts/tests.xml'],ROOT,
                seconds=120,rss_gib=2,log_path=ROOT/'logs/tests.log')
    xml=ET.parse(ROOT/'artifacts/tests.xml').getroot()
    suites=[xml] if xml.tag=='testsuite' else list(xml.iter('testsuite'))
    for key in ('tests','failures','errors','skipped'):
        receipt[key]=sum(int(x.attrib.get(key,0)) for x in suites)
    if receipt['tests']<=0 or any(receipt[k] for k in ('failures','errors','skipped')):
        raise RuntimeError('Test receipt is incomplete.')
    receipt.update(returncode=0,status='passed',junit_sha256=sha256(ROOT/'artifacts/tests.xml'))
except Exception as exc:
    receipt.update(status='failed',exception_type=type(exc).__name__)
finally:
    receipt['utc']=utc(); atomic_json(ROOT/'artifacts/test_receipt.json',receipt)
print(json.dumps(receipt,indent=2))
raise SystemExit(receipt['returncode'])
