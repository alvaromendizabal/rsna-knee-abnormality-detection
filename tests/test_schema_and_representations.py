import numpy as np
import pandas as pd
import pytest
from rsna_knee.schema import ContractError,LABELS,STUDY,SERIES,load_tables,validate_tables
from rsna_knee.representations import acquisition_features

def test_missing_is_unknown_and_input_immutable(tables):
    result=validate_tables(tables)
    assert result['train.csv'].loc[1,LABELS].isna().all()
    assert (tables['train.csv'].loc[1,LABELS]=='').all()

@pytest.mark.parametrize('bad',['-1','2','NaN','not binary','inf'])
def test_bad_labels_rejected(tables,bad):
    tables['train.csv'].loc[0,'ACL']=bad
    with pytest.raises(ContractError): validate_tables(tables)

@pytest.mark.parametrize('filename,column', [('train.csv',STUDY),('train_series.csv',SERIES)])
def test_duplicate_ids(tables,filename,column):
    tables[filename].loc[1,column]=tables[filename].loc[0,column]
    with pytest.raises(ContractError): validate_tables(tables)

def test_orphan_series(tables):
    tables['train_series.csv'].loc[0,STUDY]='not-a-study'
    with pytest.raises(ContractError): validate_tables(tables)

def test_missing_series(tables):
    tables['train_series.csv']=tables['train_series.csv'].iloc[:2].copy()
    with pytest.raises(ContractError): validate_tables(tables)

def test_unknown_plane(tables):
    tables['train_series.csv'].loc[0,'Anatomical_Plane']='oblique'
    with pytest.raises(ContractError): validate_tables(tables)

def test_multiline_csv_is_not_multiple_studies(tables,tmp_path):
    for name,frame in tables.items(): frame.to_csv(tmp_path/name,index=False)
    result=load_tables(tmp_path)
    assert len(result['train.csv'])==2 and '\n' in result['train.csv'].loc[0,'Report']

def test_duplicate_header(tables,tmp_path):
    for name,frame in tables.items(): frame.to_csv(tmp_path/name,index=False)
    p=tmp_path/'train.csv'; p.write_text(p.read_text().replace(',ACL,',',Report,',1))
    with pytest.raises(ContractError): load_tables(tmp_path)

def test_fluid_and_fat_are_distinct(tables):
    t=validate_tables(tables); f=acquisition_features(t['train.csv'],t['train_series.csv'])
    assert f.shape==(2,65)
    assert f.loc['a','fluid1_fat0_count']==1 and f.loc['a','fluid0_fat1_count']==1
    assert f.loc['a','fluid_fat_disagreement_count']==2
    assert f.loc['a','axial_present']==0 and f.loc['a','planes_available']==2
    assert f.loc['b','axial_fluid1_fat1_fraction']==1
    assert np.isfinite(f.to_numpy()).all()

def test_report_and_labels_do_not_enter_features(tables):
    t=validate_tables(tables)
    before=acquisition_features(t['train.csv'],t['train_series.csv'])
    altered=t['train.csv'].copy(); altered['Report']='CHANGED'; altered[LABELS]=1
    pd.testing.assert_frame_equal(before,acquisition_features(altered,t['train_series.csv']))
    pd.testing.assert_frame_equal(before,acquisition_features(altered[[STUDY]],t['train_series.csv']))

def test_series_shuffle_invariant(tables):
    t=validate_tables(tables); a=acquisition_features(t['train.csv'],t['train_series.csv'])
    b=acquisition_features(t['train.csv'],t['train_series.csv'].sample(frac=1,random_state=42))
    pd.testing.assert_frame_equal(a,b)

def test_train_and_example_feature_schema(tables):
    t=validate_tables(tables)
    assert list(acquisition_features(t['train.csv'],t['train_series.csv']).columns)==list(
        acquisition_features(t['test.csv'],t['test_series.csv']).columns)

def test_example_overlap_does_not_claim_independent_validation(tables):
    tables['test.csv'][STUDY]='a'
    tables['test_series.csv'][STUDY]='a'
    tables['sample_submission.csv'][STUDY]='a'
    assert len(validate_tables(tables)['test.csv'])==1
