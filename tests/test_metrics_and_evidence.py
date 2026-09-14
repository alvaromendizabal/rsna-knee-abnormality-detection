import json
import zipfile
import numpy as np
import pandas as pd
import pytest
from rsna_knee.schema import ContractError,LABELS,STUDY
from rsna_knee.metrics import binary_auc,macro_auc_12,validate_submission
from rsna_knee.downloads import prepare_csv
from rsna_knee.runtime import StageCache,atomic_json,digest,sha256

@pytest.mark.parametrize('pred,expected',[([0,1],1),([1,0],0),([.5,.5],.5)])
def test_auc_basic(pred,expected): assert binary_auc([0,1],pred)==expected

@pytest.mark.parametrize('seed',range(5))
def test_auc_matches_pairwise_definition(seed):
    rng=np.random.default_rng(seed); y=np.array([0]*5+[1]*7); p=rng.integers(0,5,len(y))/4
    pairs=[float(a>b)+.5*float(a==b) for a in p[y==1] for b in p[y==0]]
    assert binary_auc(y,p)==pytest.approx(np.mean(pairs))

@pytest.mark.parametrize('y,p',[([0,0],[.1,.2]),([0,1],[np.nan,.2]),([0,1],[-.1,.2]),([0,2],[.1,.2])])
def test_auc_invalid(y,p):
    with pytest.raises(ContractError): binary_auc(y,p)

def test_macro_exact12_and_alignment():
    truth=pd.DataFrame({x:[0,1] for x in LABELS},index=['a','b'])
    scores=pd.DataFrame({x:[.1,.9] for x in LABELS},index=truth.index)
    assert macro_auc_12(truth,scores)['macro_auc_12']==1
    with pytest.raises(ContractError): macro_auc_12(truth,scores.iloc[::-1])
    with pytest.raises(ContractError): macro_auc_12(truth.iloc[:,:-1],scores.iloc[:,:-1])

def test_submission_template_contract(tables):
    sample=tables['sample_submission.csv']; validate_submission(sample,sample)
    bad=sample.copy(); bad.loc[0,'ACL']='inf'
    with pytest.raises(ContractError): validate_submission(bad,sample)
    bad=sample.copy(); bad.loc[0,STUDY]='different'
    with pytest.raises(ContractError): validate_submission(bad,sample)

def test_cache_reuse_tamper_and_context(tmp_path):
    key=digest({'context':1}); cache=StageCache(tmp_path,key)
    assert cache.reuse('schema') is False
    p=tmp_path/'summary.json'; atomic_json(p,{'n':2}); cache.commit('schema',[p])
    assert StageCache(tmp_path,key).reuse('schema') is True
    with pytest.raises(RuntimeError): StageCache(tmp_path,'different').reuse('schema')
    atomic_json(p,{'n':3})
    with pytest.raises(RuntimeError): cache.reuse('schema')

def test_partial_stage_not_reused(tmp_path):
    atomic_json(tmp_path/'unfinished.json',{'partial':True})
    assert StageCache(tmp_path,'key').reuse('schema') is False

@pytest.mark.parametrize('name',['../train.csv','nested/train.csv','train.csv/'])
def test_zip_paths_rejected(tmp_path,name):
    archive=tmp_path/'input.zip'
    with zipfile.ZipFile(archive,'w') as z: z.writestr(name,'not data')
    with pytest.raises(ContractError): prepare_csv(archive,tmp_path/'output.csv','train.csv')
    assert not (tmp_path/'output.csv').exists()

def test_download_unknown_filename(tmp_path):
    p=tmp_path/'x'; p.write_text('x')
    with pytest.raises(ContractError): prepare_csv(p,tmp_path/'output.csv','all-images.zip')

def test_single_file_zip_and_no_overwrite(tables,tmp_path):
    archive=tmp_path/'input.zip'
    with zipfile.ZipFile(archive,'w') as z: z.writestr('train.csv',tables['train.csv'].to_csv(index=False))
    dest=tmp_path/'train.csv'; prepare_csv(archive,dest,'train.csv'); original=sha256(dest)
    with pytest.raises(ContractError): prepare_csv(archive,dest,'train.csv')
    assert sha256(dest)==original
