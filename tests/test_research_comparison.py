import numpy as np
import pandas as pd
import pytest
from rsna_knee.schema import LABELS,ContractError
from rsna_research.comparison import paired_holdout_auc

def data():
    y=np.tile([0,1],20); idx=[f'synthetic_{i}' for i in range(40)]
    truth=pd.DataFrame({k:y for k in LABELS},index=idx)
    baseline=pd.DataFrame(.5,index=idx,columns=LABELS)
    candidate=pd.DataFrame({k:.1+.8*y for k in LABELS},index=idx)
    return truth,baseline,candidate,pd.Series(idx,index=idx)

def test_paired_official_metric_direction():
    y,a,b,g=data(); r=paired_holdout_auc(y,a,b,g,resamples=100)
    assert r['delta_macro_auc_12']==.5 and r['candidate_macro_auc_12']==1
    assert r['bootstrap_valid']==100 and not r['adaptive_selection_adjusted']

def test_same_predictions_no_improvement():
    y,a,b,g=data(); r=paired_holdout_auc(y,b,b,g,resamples=100)
    assert r['delta_macro_auc_12']==0

def test_small_groups_blocks_interval():
    y,a,b,g=data(); g[:]='one'
    with pytest.raises(ContractError): paired_holdout_auc(y,a,b,g,resamples=100)

def test_misaligned_rows_block():
    y,a,b,g=data()
    with pytest.raises(ContractError): paired_holdout_auc(y,a,b.iloc[::-1],g,resamples=100)
