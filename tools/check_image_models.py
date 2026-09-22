#!/usr/bin/env python3
"""Audit the curated image-model publication without private data or ML packages."""
from pathlib import Path
import json
import math
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / 'reports/image_models/results.json').read_text())
N = json.loads((ROOT / 'notebooks/06_image_models_and_replication.ipynb').read_text())
assert D['pilot_overlap'] == 0
assert D['primary_decision'] == 'STOP_FIXED_BLEND_DIRECTION'
base = D['replication'][D['baseline']]
candidate = D['replication'][D['primary_candidate']]
assert math.isclose(candidate['macro_auc'] - base['macro_auc'], D['primary_auc_delta'], abs_tol=1e-12)
assert math.isclose(candidate['brier'] - base['brier'], D['primary_brier_delta'], abs_tol=1e-12)
assert len(D['per_target']) == 12
assert all(r['positive'] > 0 and r['negative'] > 0 and r['positive'] + r['negative'] == 12 for r in D['per_target'])
assert math.isclose(sum(r['baseline_auc'] for r in D['per_target']) / 12, base['macro_auc'], abs_tol=1e-12)
assert math.isclose(sum(r['primary_auc'] for r in D['per_target']) / 12, candidate['macro_auc'], abs_tol=1e-12)
assert D['public_score_snapshot']['independent_model_public_score'] is None
cells = [c for c in N['cells'] if c['cell_type'] == 'code']
assert [c['execution_count'] for c in cells] == list(range(1, 8))
outputs = [o for c in cells for o in c.get('outputs', [])]
assert not any(o['output_type'] == 'error' for o in outputs)
plots = [o['data'] for o in outputs if 'application/vnd.plotly.v1+json' in o.get('data', {})]
assert len(plots) == 3 and all('image/svg+xml' in p for p in plots)
assert all(p['application/vnd.plotly.v1+json']['layout']['width'] >= 950 for p in plots)
assert any('RSNA_IMAGE_MODEL_PUBLICATION_COMPLETE' in ''.join(o.get('text', [])) for o in outputs)
# Scope the scan to the new publication, not unrelated historical files.
paths = ['README.md','docs/PROJECT_STATUS.md','docs/IMAGE_MODELS.md','configs/image_models.json',
         'reports/image_models/results.json','notebooks/06_image_models_and_replication.ipynb',
         'src/rsna_research/image_models.py','tests/test_image_models.py']
for name in paths:
    text = (ROOT / name).read_text()
    for pattern in [r'1\.2\.826\.0\.1\.3680043', r'AKIA[A-Z0-9]{16}', r'ASIA[A-Z0-9]{16}',
                    r'gh[pousr]_[A-Za-z0-9]{20,}', r'X-Amz-(?:Signature|Credential)=',
                    r'arn:aws:', r'/home/sagemaker-user/', r'-----BEGIN .*PRIVATE KEY-----']:
        assert not re.search(pattern, text), f'Private content pattern in {name}'
subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-p', 'test_image_models.py'], check=True)
print('IMAGE_MODEL_PUBLICATION_PASSED: aggregate metrics, saved figures, privacy scan, 24 synthetic tests')
