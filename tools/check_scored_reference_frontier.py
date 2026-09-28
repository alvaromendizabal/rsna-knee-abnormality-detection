#!/usr/bin/env python3
from pathlib import Path
import json, math, re, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'reports/scored_reference_frontier/results.json').read_text())
H=D['historical_public']; R=D['scored_reference']; O=D['runtime_optimization']; N=D['next_milestone']
assert H['reference_auc']==0.933 and H['leader_auc']==0.958
assert math.isclose(H['gap'],0.025,abs_tol=1e-12)
assert R['asset_paths']==36 and R['weight_files']==32
assert R['gpu_checkpoint_checks_passed']==32
assert R['stored_native_fingerprints_checked']==20
assert R['complete_real_image_forward_reproduced'] is False
assert R['submission_ready'] is False
assert O['baseline_head_calls']==20 and O['candidate_head_calls']==15
assert math.isclose(O['call_reduction_fraction'],0.25,abs_tol=1e-12)
assert O['trained_heads_loaded']==15 and O['trials']==3
assert O['final_csv_exact_all_trials'] is True
assert O['median_head_only_speed_ratio'] > 1.05
assert O['real_image_parity_verified'] is False and O['end_to_end_speedup_verified'] is False
assert N['stage']==64 and N['status']=='PREPARED_NOT_EXECUTED'
nb=json.loads((ROOT/'notebooks/09_scored_reference_recovery_and_runtime.ipynb').read_text())
code=[c for c in nb['cells'] if c['cell_type']=='code']
assert [c.get('execution_count') for c in code]==[1,2,3]
outs=[o for c in code for o in c.get('outputs',[])]
assert not any(o.get('output_type')=='error' for o in outs)
assert sum('application/vnd.plotly.v1+json' in (o.get('data') or {}) for o in outs) == 3
assert any('SCORED_REFERENCE_FRONTIER_PUBLICATION_COMPLETE' in ''.join(o.get('text',[])) for o in outs if o.get('output_type')=='stream')
paths=['README.md','docs/PROJECT_STATUS.md','docs/TRAINING_FRONTIER.md','docs/SCORED_REFERENCE_FRONTIER.md','reports/scored_reference_frontier/results.json','notebooks/09_scored_reference_recovery_and_runtime.ipynb']
patterns=[r'1\.2\.826\.0\.1\.3680043',r'AKIA[A-Z0-9]{16}',r'ASIA[A-Z0-9]{16}',r'gh[pousr]_[A-Za-z0-9]{20,}',r'X-Amz-(?:Signature|Credential)=',r'arn:aws:',r'/home/sagemaker-user/']
for name in paths:
    txt=(ROOT/name).read_text()
    for p in patterns: assert not re.search(p,txt), f'private-content pattern in {name}'
subprocess.run([sys.executable,'-m','unittest','discover','-s',str(ROOT/'tests'),'-p','test_scored_reference_frontier.py'],check=True)
print('SCORED_REFERENCE_FRONTIER_PUBLICATION_PASSED')
