import pandas as pd
import pytest
from rsna_knee.schema import LABELS, STUDY, SERIES, SERIES_COLUMNS

@pytest.fixture
def tables():
    train=pd.DataFrame([{STUDY:'a','Report':'No tear.\nSecond line.',**{x:'1' if i%2 else '0' for i,x in enumerate(LABELS)}},
                        {STUDY:'b','Report':'Synthetic text only.',**{x:'' for x in LABELS}}])
    train_series=pd.DataFrame([
        ['a','sa1','1','0','Sagittal'],['a','sa2','0','1','Coronal'],['b','sb1','1','1','Axial']],columns=SERIES_COLUMNS)
    test=pd.DataFrame({STUDY:['c']})
    test_series=pd.DataFrame([['c','sc1','1','1','Sagittal']],columns=SERIES_COLUMNS)
    sample=pd.DataFrame([{STUDY:'c',**{x:'0.5' for x in LABELS}}])
    return {'train.csv':train,'train_series.csv':train_series,'test.csv':test,
            'test_series.csv':test_series,'sample_submission.csv':sample}
