"""Prepared paired holdout comparison; never trains or opens data on import.

Use only after a frozen, defensible evaluation plan and predictions exist.
Repeated feature searches require independent confirmation; this interval does
not correct adaptive model selection or establish leaderboard equivalence.
"""
import numpy as np
import pandas as pd
from rsna_knee.metrics import macro_auc_12
from rsna_knee.schema import ContractError


def paired_holdout_auc(truth,baseline,candidate,groups,*,resamples=1000,seed=20260912):
    a=macro_auc_12(truth,baseline); b=macro_auc_12(truth,candidate)
    if not isinstance(groups,pd.Series) or not groups.index.equals(truth.index):
        raise ContractError('Group IDs must have exactly the evaluation index/order.')
    if groups.isna().any() or groups.astype(str).str.strip().eq('').any():
        raise ContractError('Missing evaluation group ID.')
    if not 100<=resamples<=2000: raise ContractError('Use a bounded 100-2000 paired resamples.')
    labels=groups.astype(str).to_numpy(); unique=np.unique(labels)
    if len(unique)<10: raise ContractError('Fewer than 10 independent groups; uncertainty estimation stays blocked.')
    members={g:np.flatnonzero(labels==g) for g in unique}
    rng=np.random.default_rng(seed); deltas=[]
    for _ in range(resamples):
        idx=np.concatenate([members[g] for g in rng.choice(unique,size=len(unique),replace=True)])
        y=truth.iloc[idx].reset_index(drop=True)
        p=baseline.iloc[idx].reset_index(drop=True); q=candidate.iloc[idx].reset_index(drop=True)
        try:
            delta=macro_auc_12(y,q)['macro_auc_12']-macro_auc_12(y,p)['macro_auc_12']
        except ContractError: continue  # retain rejection counts; do not average fewer labels
        deltas.append(delta)
    valid=len(deltas); interval=None
    if valid>=max(100,int(.9*resamples)):
        interval=[float(x) for x in np.quantile(deltas,[.025,.975])]
    return {'baseline_macro_auc_12':a['macro_auc_12'],'candidate_macro_auc_12':b['macro_auc_12'],
        'delta_macro_auc_12':b['macro_auc_12']-a['macro_auc_12'],
        'per_label_delta':{k:b['per_label_auc'][k]-v for k,v in a['per_label_auc'].items()},
        'paired_group_bootstrap_interval_95':interval,'bootstrap_valid':valid,
        'bootstrap_rejected_missing_class':resamples-valid,'groups':len(unique),
        'setting':'single_frozen_local_holdout_not_leaderboard',
        'adaptive_selection_adjusted':False,'interval_available':interval is not None}
