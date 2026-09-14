#!/usr/bin/env python3
"""Prepare a small local public showcase. Does not touch any Git repository."""
from pathlib import Path
import argparse
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_knee.runtime import require_tests,atomic_json,sha256,utc
from rsna_research.workflow import checked_round1
p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--output',type=Path,default=Path.home()/'rsna-knee-abnormality-detection-portfolio-export')
a=p.parse_args(); out=a.output.expanduser().resolve()
if out.exists(): raise SystemExit('Output already exists. Preserve/review it; use another empty output directory instead of overwriting.')
if out.is_relative_to(ROOT): raise SystemExit('The showcase export must be outside the research workspace.')
tests=require_tests(ROOT); r1=checked_round1(ROOT)
status={'prepared_utc':utc(),'evidence_setting':'local_user_execution','tests_passed':True,
        'test_count':int(tests['tests']),'m01_metadata_audit':'complete','round1_feature_construction':'complete',
        'round2_image_pilot':'not_verified_for_publication','model_fits':0,'official_score':None,
        'predictive_feature_gains_established':False,'clinical_validation':False,
        'publication_mode':'showcase_only_private_implementation','github_updated_by_this_script':False,
        'private_source_fingerprint':tests['source_hash']}
# Round 2 needs its own checked evidence; default to unverified rather than copy an unvalidated score.
s=r1/'construction_summary.json'; summary=json.loads(s.read_text())
status.update(round1_new_feature_columns=int(summary['new_columns']),round1_feature_families=int(summary['new_families']))
out.mkdir(parents=True)
for name in ('README.md','RESEARCH_OVERVIEW.md','NOTICE.md','SECURITY.md','.gitignore'):
    (out/name).write_bytes((ROOT/'portfolio'/name).read_bytes())
(out/'RESULTS.md').write_text('# Results and verification\n\n'
    'Evidence setting: user-run local CPU pipeline.\n\n'
    f"Tests: {status['test_count']} passed with no reported failures, errors, or skips. "
    'The metadata audit and first representation-construction round completed. '
    f"Round 1 added {status['round1_new_feature_columns']} candidate columns across eight families; these are not proven predictors.\n\n"
    '**No model fitting or validated AUC improvement is established by this release.** '
    'Round 2 publication status remains unverified. No leaderboard position or clinical utility is claimed.\n\n'
    'See `reports/status.json` for the source fingerprint and constrained evidence record. '
    'The working implementation and private artifacts are intentionally not included.\n',encoding='utf-8')
atomic_json(out/'reports/status.json',status)
print('Local showcase prepared: '+str(out))
print('Read every file. Then follow docs/PUBLICATION_RUNBOOK.md. Nothing was committed or uploaded.')
