"""Synthetic integration coverage; runs only when the user invokes pytest."""
import json
from pathlib import Path
import shutil
from rsna_knee import audit
from rsna_knee.runtime import sha256

def test_toy_pipeline_pause_resume_and_raw_integrity(tables,tmp_path,monkeypatch):
    project=Path(__file__).resolve().parents[1]
    (tmp_path/'configs').mkdir()
    for name in ('requirements-audit.txt','pytest.ini'):
        shutil.copyfile(project/name,tmp_path/name)
    shutil.copyfile(project/'configs/milestone01.json',tmp_path/'configs/milestone01.json')
    raw=tmp_path/'data/raw/metadata'; raw.mkdir(parents=True)
    for name,frame in tables.items(): frame.to_csv(raw/name,index=False)
    hashes={p.name:sha256(p) for p in raw.glob('*.csv')}
    # Isolate the integration test from the real execution guard/receipt.
    monkeypatch.setattr(audit,'require_tests',lambda root: {'synthetic_test_guard':True})
    paused=audit.run(tmp_path,stop_after='schema')
    assert paused['status']=='paused_as_requested'
    complete=audit.run(tmp_path)
    assert complete['key']==paused['key'] and complete['stages']['schema']=='reused_verified'
    assert complete['raw_inputs_unchanged'] and complete['model_fits']==0
    again=audit.run(tmp_path)
    assert set(again['stages'].values())=={'reused_verified'}
    run=tmp_path/complete['run_directory']
    schema=json.loads((run/'schema_summary.json').read_text())
    assert schema['unknown_label_cells']==12
    rep=json.loads((run/'representation_summary.json').read_text())
    assert rep['candidate_columns']==65 and rep['predictive_utility']=='NOT_TESTED'
    assert hashes=={p.name:sha256(p) for p in raw.glob('*.csv')}
    for p in run.glob('*.json'):
        assert 'No tear.' not in p.read_text()
