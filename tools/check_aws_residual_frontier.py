#!/usr/bin/env python3
from pathlib import Path
import json, math, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'reports/aws_residual_frontier/results.json').read_text())
H=D['historical_public']; A=D['aws_training_boundary']; S=D['stage70']
assert H['reference_auc']==0.933 and H['leader_snapshot_auc']==0.961
assert math.isclose(H['gap'],0.028,abs_tol=1e-12)
assert H['internal_metrics_directly_comparable'] is False
assert A['canonical_cache_studies']==4407
assert A['canonical_cache_layout']=='NCHW'
assert A['grouped_non_gold_rows']==4349 and A['gold_audit_rows']==58 and A['gold_optimizer_rows']==0
assert D['stage67']['status']=='SOURCE_BLOCKED' and D['stage67']['model_fits']==0
assert D['stage68']['status']=='EXECUTION_FAILURE' and D['stage68']['model_fits']==0
assert D['stage69']['status']=='EXECUTION_FAILURE' and D['stage69']['model_fits']==0
assert S['status']=='PREPARED_NOT_EXECUTED' and S['model_fits_completed']==0
nb=json.loads((ROOT/'notebooks/10_aws_only_residual_frontier.ipynb').read_text())
code=[c for c in nb['cells'] if c['cell_type']=='code']
assert [c.get('execution_count') for c in code]==[1,2,3]
outs=[o for c in code for o in c.get('outputs',[])]
assert not any(o.get('output_type')=='error' for o in outs)
assert sum('application/vnd.plotly.v1+json' in (o.get('data') or {}) for o in outs)==3
assert any('AWS_RESIDUAL_FRONTIER_PUBLICATION_COMPLETE' in ''.join(o.get('text',[])) for o in outs if o.get('output_type')=='stream')
paths=['README.md','docs/PROJECT_STATUS.md','docs/TRAINING_FRONTIER.md','docs/SCORED_REFERENCE_FRONTIER.md','docs/AWS_RESIDUAL_FRONTIER.md','reports/aws_residual_frontier/results.json','notebooks/10_aws_only_residual_frontier.ipynb']
patterns=[r'1\.2\.826\.0\.1\.3680043',r'AKIA[A-Z0-9]{16}',r'ASIA[A-Z0-9]{16}',r'gh[pousr]_[A-Za-z0-9]{20,}',r'X-Amz-(?:Signature|Credential)=',r'arn:aws:',r'/home/sagemaker-user/']
for name in paths:
    txt=(ROOT/name).read_text()
    for p in patterns: assert not re.search(p,txt), f'private-content pattern in {name}'
subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_aws_residual_frontier.py'],check=True)
print('AWS_RESIDUAL_FRONTIER_PUBLICATION_PASSED')
