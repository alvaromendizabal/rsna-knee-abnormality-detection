#!/usr/bin/env python3
from pathlib import Path
import json, math, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'reports/aws_residual_frontier/results.json').read_text())
H=D['historical_public']; A=D['aws_training_boundary']; S70=D['stage70']; S71=D['stage71']; S72=D['stage72']

assert H['reference_auc']==0.933
assert set(H)=={'reference_auc','internal_metrics_directly_comparable'}
assert H['internal_metrics_directly_comparable'] is False

assert A['canonical_cache_studies']==4407
assert A['canonical_cache_layout']=='NCHW'
assert A['grouped_non_gold_rows']==4349 and A['gold_audit_rows']==58 and A['gold_optimizer_rows']==0

assert D['stage67']['status']=='SOURCE_BLOCKED' and D['stage67']['model_fits']==0
assert D['stage68']['status']=='EXECUTION_FAILURE' and D['stage68']['model_fits']==0
assert D['stage69']['status']=='EXECUTION_FAILURE' and D['stage69']['model_fits']==0

assert S70['status']=='SCREEN_PROMOTED_TO_CONFIRMATION'
assert S70['promote_to_confirmation_folds'] is True
assert math.isclose(S70['mean_fold_blend_delta'],0.0013285202826023301,abs_tol=1e-15)

assert S71['status']=='SCIENTIFIC_NEGATIVE_CONFIRMATION'
assert S71['promoted'] is False
assert S71['gates']['all_confirmation_folds_nonnegative'] is False
assert sum(not v for v in S71['gates'].values())==1
assert math.isclose(S71['mean_fold_blend_delta'],0.0024371589736764676,abs_tol=1e-15)
assert min(S71['fold_deltas'].values())<0

assert S72['status']=='SUBMISSION_BOUNDARY_HARDENED_NOT_SCORED'
assert S72['new_official_score_claimed'] is False
assert S72['official_best_remains']==0.933

nb=json.loads((ROOT/'notebooks/11_residual_confirmation_and_submission_boundary.ipynb').read_text())
code=[c for c in nb['cells'] if c['cell_type']=='code']
assert [c.get('execution_count') for c in code]==[1,2,3]
outs=[o for c in code for o in c.get('outputs',[])]
assert not any(o.get('output_type')=='error' for o in outs)
assert sum('application/vnd.plotly.v1+json' in (o.get('data') or {}) for o in outs)==3
assert any('RESIDUAL_CONFIRMATION_PUBLICATION_COMPLETE' in ''.join(o.get('text',[])) for o in outs if o.get('output_type')=='stream')

paths=[
    'README.md',
    'docs/PROJECT_STATUS.md',
    'docs/TRAINING_FRONTIER.md',
    'docs/SCORED_REFERENCE_FRONTIER.md',
    'docs/AWS_RESIDUAL_FRONTIER.md',
    'reports/aws_residual_frontier/results.json',
    'notebooks/11_residual_confirmation_and_submission_boundary.ipynb',
]
patterns=[
    r'1\.2\.826\.0\.1\.3680043',
    r'AKIA[A-Z0-9]{16}',
    r'ASIA[A-Z0-9]{16}',
    r'gh[pousr]_[A-Za-z0-9]{20,}',
    r'X-Amz-(?:Signature|Credential)=',
    r'arn:aws:',
    r'/home/sagemaker-user/',
]
for name in paths:
    txt=(ROOT/name).read_text()
    for p in patterns:
        assert not re.search(p,txt), f'private-content pattern in {name}'

subprocess.run([
    sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),
    '-p','test_aws_residual_frontier.py'
],check=True)
print('AWS_RESIDUAL_FRONTIER_PUBLICATION_PASSED')
