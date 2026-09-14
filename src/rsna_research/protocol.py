"""Round 1: fixed MRI acquisition representations and label-blind sample design."""
from __future__ import annotations
from itertools import combinations
import re
import unicodedata
import numpy as np
import pandas as pd
from rsna_knee.schema import STUDY, SERIES, LABELS, PLANES, ContractError
from rsna_knee.representations import acquisition_features
from rsna_knee.runtime import digest

FAMILIES = {
 'within_plane_contrast':'Conditional contrast proportions within each available plane.',
 'plane_diversity':'Within-plane entropy and concentration of contrast combinations.',
 'contrast_balance':'Matched contrast-pair balance rather than unqualified extra series.',
 'cross_plane_agreement':'Complementarity and overlap of contrasts across imaging planes.',
 'cross_plane_imbalance':'Contrast-specific imbalance between complementary planes.',
 'protocol_diversity':'Global effective diversity and concentration of acquisition slots.',
 'selection_efficiency':'Nonredundant coverage under a one-series-per-plane view budget.',
 'fluid_view_context':'Availability of paired fluid-sensitive views and fat suppression.',
}


def protocol_features(studies: pd.DataFrame, series: pd.DataFrame):
    base=acquisition_features(studies[[STUDY]],series)
    features={}; rows=[]
    def add(name,values,family):
        name='r1__'+name
        if name in features: raise ContractError('Duplicate engineered feature name.')
        features[name]=np.asarray(values,dtype=float)
        rows.append({'feature':name,'family':family,'available_at_inference':True,
            'uses_report_or_label':False,'learned_on_dataset':False,
            'predictive_status':'not_evaluated','mechanism':FAMILIES[family]})
    counts={p:np.column_stack([base[f'{p.lower()}_fluid{f}_fat{a}_count'].values
                      for f in (0,1) for a in (0,1)]) for p in PLANES}
    present={p:counts[p]>0 for p in PLANES}
    for p in PLANES:
        key=p.lower(); c=counts[p]; n=c.sum(axis=1); den=np.maximum(n,1)
        q=c/den[:,None]
        for k,(fluid,fat) in enumerate([(0,0),(0,1),(1,0),(1,1)]):
            add(f'{key}_conditional_f{fluid}_s{fat}',q[:,k],'within_plane_contrast')
        entropy=-(q*np.log(np.clip(q,1e-12,None))).sum(axis=1)
        add(f'{key}_contrast_entropy',entropy,'plane_diversity')
        add(f'{key}_contrast_concentration',(q*q).sum(axis=1),'plane_diversity')
        for stem,i,j in [('fluid_fat_pair',2,3),('nonfluid_fat_pair',0,1)]:
            add(f'{key}_{stem}_balance',2*np.minimum(c[:,i],c[:,j])/np.maximum(c[:,i]+c[:,j],1),'contrast_balance')
        unique=present[p].sum(axis=1)
        add(f'{key}_series_per_occupied_contrast',n/np.maximum(unique,1),'selection_efficiency')
        add(f'{key}_nonredundant_fraction',unique/den,'selection_efficiency')
        add(f'{key}_fluid_fat_fraction_given_fluid',c[:,3]/np.maximum(c[:,2]+c[:,3],1),'fluid_view_context')
    for a,b in combinations(PLANES,2):
        key=f'{a.lower()}_{b.lower()}'; pa,pb=present[a],present[b]
        joint=(pa&pb).sum(axis=1); union=(pa|pb).sum(axis=1)
        add(key+'_shared_contrasts',joint,'cross_plane_agreement')
        add(key+'_contrast_jaccard',joint/np.maximum(union,1),'cross_plane_agreement')
        add(key+'_complementary_contrasts',(pa^pb).sum(axis=1),'cross_plane_agreement')
        for k in range(4):
            ca,cb=counts[a][:,k],counts[b][:,k]
            add(f'{key}_contrast{k}_imbalance',np.abs(ca-cb)/np.maximum(ca+cb,1),'cross_plane_imbalance')
        fa=counts[a][:,2:].sum(axis=1); fb=counts[b][:,2:].sum(axis=1)
        add(key+'_fluid_pair_available',((fa>0)&(fb>0)).astype(float),'fluid_view_context')
        add(key+'_fluid_fat_pair_available',(pa[:,3]&pb[:,3]).astype(float),'fluid_view_context')
    all_counts=np.concatenate([counts[p] for p in PLANES],axis=1)
    q=all_counts/all_counts.sum(axis=1,keepdims=True)
    entropy=-(q*np.log(np.clip(q,1e-12,None))).sum(axis=1)
    for key,val in [('slot_entropy',entropy),('effective_slots',np.exp(entropy)),
                    ('slot_concentration',(q*q).sum(axis=1)),('dominant_slot_share',q.max(axis=1)),
                    ('redundant_series_fraction',1-(all_counts>0).sum(axis=1)/all_counts.sum(axis=1))]:
        add(key,val,'protocol_diversity')
    extra=pd.DataFrame(features,index=base.index)
    if not np.isfinite(extra.to_numpy()).all(): raise ContractError('Non-finite protocol feature.')
    registry=pd.DataFrame(rows)
    if set(registry.family)!=set(FAMILIES): raise ContractError('A planned protocol family is missing.')
    # Baseline descriptors are preserved, not miscounted as new features.
    return pd.concat([base,extra],axis=1),registry


def development_pool(train: pd.DataFrame):
    """Preserve all expert-labeled exams and report-exact duplicates for later design.

    This is a conservative development exclusion, NOT a patient identity model,
    a validated disease split, or proof that patients/sites are disjoint.
    """
    observed=train[LABELS].notna().any(axis=1)
    def normalized_hash(text):
        text=re.sub(r'\s+',' ',unicodedata.normalize('NFKC',str(text))).strip()
        return digest(text) if text else None
    report_hash=train['Report'].map(normalized_hash)
    protected=set(report_hash[observed].dropna())
    duplicate_guard=report_hash.isin(protected)
    usable=~observed & ~duplicate_guard
    info={'expert_labeled_studies_reserved':int(observed.sum()),
          'unlabeled_exact_report_duplicates_reserved':int((~observed & duplicate_guard).sum()),
          'unlabeled_development_studies':int(usable.sum()),
          'expert_label_values_inspected':False,'patient_disjointness_verified':False,
          'site_disjointness_verified':False,'supervised_validation_design':'pending',
          'model_fits':0,'official_score':None}
    if not usable.any(): raise ContractError('No unlabeled development studies remain; stop before sampling.')
    return train.loc[usable,[STUDY]].copy(),info


def sample_plan(studies: pd.DataFrame, series: pd.DataFrame, *, n_studies=2, seed=20260912):
    """Fixed hash sampling; one preferred series per available anatomical plane.

    Preferences are predeclared, not estimated from labels. UIDs identify rows,
    never enter a model feature matrix. A different archive layout must be
    inspected rather than guessed by the download code.
    """
    ids=sorted(studies[STUDY].astype(str),key=lambda x:digest([seed,x]))[:n_studies]
    selected=[]
    for study in ids:
        for plane in PLANES:
            candidates=series.loc[series[STUDY].eq(study)&series['Anatomical_Plane'].eq(plane)].copy()
            if candidates.empty: continue
            candidates['_priority']=2*candidates['Fluid_Sensitive']+candidates['Fat_Suppression']
            candidates['_tie']=candidates[SERIES].map(lambda x:digest([seed,str(x)]))
            row=candidates.sort_values(['_priority','_tie'],ascending=[False,True]).iloc[0]
            selected.append({STUDY:study,SERIES:str(row[SERIES]),'Anatomical_Plane':plane,
                'Fluid_Sensitive':int(row['Fluid_Sensitive']),'Fat_Suppression':int(row['Fat_Suppression']),
                'selection':'fixed_priority_then_hash','pilot_only':True})
    if not selected: raise ContractError('No pilot image series selected.')
    return pd.DataFrame(selected)
