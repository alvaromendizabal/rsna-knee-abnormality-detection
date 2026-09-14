import numpy as np
import pandas as pd
import pytest
from rsna_knee.schema import STUDY,LABELS,validate_tables,ContractError
from rsna_research.protocol import protocol_features,development_pool,sample_plan,FAMILIES


def test_round1_preserves_baseline_and_all_eight_families(tables):
    t=validate_tables(tables); x,r=protocol_features(t['train.csv'],t['train_series.csv'])
    assert x.shape==(2,130) and len(r)==65 and set(r.family)==set(FAMILIES)
    assert np.isfinite(x.to_numpy()).all() and not r.uses_report_or_label.any()

@pytest.mark.parametrize('seed',range(5))
def test_round1_order_invariance(tables,seed):
    t=validate_tables(tables)
    a,_=protocol_features(t['train.csv'],t['train_series.csv'])
    b,_=protocol_features(t['train.csv'],t['train_series.csv'].sample(frac=1,random_state=seed))
    pd.testing.assert_frame_equal(a,b)

def test_no_label_or_report_features(tables):
    t=validate_tables(tables); a,_=protocol_features(t['train.csv'],t['train_series.csv'])
    train=t['train.csv'].copy(); train['Report']='changed'; train[LABELS]=1
    b,_=protocol_features(train,t['train_series.csv']); pd.testing.assert_frame_equal(a,b)

def test_missing_plane_zero_conditional_and_presence(tables):
    t=validate_tables(tables); x,_=protocol_features(t['train.csv'],t['train_series.csv'])
    assert x.loc['b','sagittal_present']==0
    assert x.loc['b','r1__sagittal_conditional_f1_s1']==0
    assert x.loc['b','r1__axial_conditional_f1_s1']==1

def test_conditional_fractions_sum_one_for_present_planes(tables):
    t=validate_tables(tables); x,_=protocol_features(t['train.csv'],t['train_series.csv'])
    for plane in ('sagittal','coronal','axial'):
        cols=[c for c in x if c.startswith(f'r1__{plane}_conditional_')]
        assert np.allclose(x[cols].sum(axis=1),x[f'{plane}_present'])

def test_pool_reserves_expert_cases(tables):
    t=validate_tables(tables); pool,info=development_pool(t['train.csv'])
    assert pool[STUDY].tolist()==['b']; assert info['expert_labeled_studies_reserved']==1
    assert info['official_score'] is None and not info['patient_disjointness_verified']

def test_exact_report_duplicate_is_excluded_not_patient_claim(tables):
    t=validate_tables(tables); t['train.csv'].loc[1,'Report']=t['train.csv'].loc[0,'Report']
    with pytest.raises(ContractError): development_pool(t['train.csv'])

@pytest.mark.parametrize('seed',[0,20260912,42])
def test_sampler_repeatable_and_label_blind(tables,seed):
    t=validate_tables(tables); pool,_=development_pool(t['train.csv'])
    a=sample_plan(pool,t['train_series.csv'],seed=seed)
    b=sample_plan(pool,t['train_series.csv'].iloc[::-1],seed=seed)
    pd.testing.assert_frame_equal(a,b)
    assert not a.duplicated([STUDY,'Anatomical_Plane']).any()

def test_feature_schema_matches_example(tables):
    t=validate_tables(tables)
    a,_=protocol_features(t['train.csv'],t['train_series.csv'])
    b,_=protocol_features(t['test.csv'],t['test_series.csv'])
    assert list(a)==list(b)
