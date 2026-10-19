import pytest
from rsna_knee.schema import ContractError,LABELS,STUDY,SERIES,load_tables,validate_tables

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

def test_example_overlap_does_not_claim_independent_validation(tables):
    tables['test.csv'][STUDY]='a'
    tables['test_series.csv'][STUDY]='a'
    tables['sample_submission.csv'][STUDY]='a'
    assert len(validate_tables(tables)['test.csv'])==1
