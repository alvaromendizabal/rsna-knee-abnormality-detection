"""Bounded local stages. Importing this module never executes project work."""
from __future__ import annotations
import importlib.metadata
import json
from pathlib import Path
import numpy as np
import pandas as pd
from rsna_knee.schema import FILES, STUDY, SERIES, PLANES, load_tables, ContractError
from rsna_knee.runtime import (Progress, StageCache, atomic_json, atomic_csv, digest,
    exclusive_lock, require_tests, sha256, source_hash, utc, versions)
from .protocol import protocol_features, development_pool, sample_plan
from .pixels import load_volume, normalize, image_features


def current_environment():
    result=versions()
    result['pydicom']=importlib.metadata.version('pydicom')
    if result['pydicom']!='3.0.2': raise RuntimeError('Round package requires its recorded pydicom 3.0.2 pin.')
    return result


def checked_m01(root):
    require_tests(root)
    current_environment()
    latest=json.loads((root/'artifacts/m01_latest.json').read_text())
    if latest.get('status')!='complete' or not latest.get('raw_inputs_unchanged'):
        raise RuntimeError('Complete notebook 01 before feature rounds.')
    directory=root/latest['run_directory']
    if directory.resolve().parent!=(root/'artifacts/m01').resolve(): raise RuntimeError('Invalid M01 path.')
    cache=StageCache(directory,latest['key'])
    for stage in ('schema','supervision','representation'):
        if not cache.reuse(stage): raise RuntimeError('M01 stage is incomplete.')
    context=json.loads((directory/'context.json').read_text())
    if context['source_hash']!=source_hash(root): raise RuntimeError('Code changed after M01; rerun tests and notebook 01 before continuing.')
    raw=root/'data/raw/metadata'
    if any(sha256(raw/name)!=context['data_sha256'][name] for name in FILES):
        raise RuntimeError('Metadata bytes changed after M01.')
    return context['data_sha256']


def feature_profile(frame,registry):
    if frame.empty: raise ContractError('Cannot profile an empty feature panel.')
    p=pd.DataFrame({'feature':frame.columns,'minimum':frame.min().values,'maximum':frame.max().values,
        'mean':frame.mean().values,'std':frame.std(ddof=0).values,
        'distinct_values':frame.nunique().values,'zero_fraction':frame.eq(0).mean().values,
        'missing_fraction':frame.isna().mean().values})
    p=p.merge(registry[['feature','family']],on='feature',how='left',validate='one_to_one')
    if p.family.isna().any(): raise ContractError('Missing feature dictionary entry.')
    return p


def round1(root,stop_after=None):
    hashes=checked_m01(root); cfg=json.loads((root/'configs/research_rounds.json').read_text())
    context={'raw_sha256':hashes,'source_hash':source_hash(root),'config':cfg,'environment':current_environment()}
    key=digest(context); directory=root/'artifacts/r01'/key[:20]
    cache=StageCache(directory,key); progress=Progress(directory/'progress.jsonl',180,4)
    with exclusive_lock(root/'artifacts/r01.lock'):
        atomic_json(directory/'context.json',context)
        statuses={}
        for stage in ('construction','diagnostics'):
            reused=cache.reuse(stage); statuses[stage]='reused_verified' if reused else 'computed'
            progress.log(stage,statuses[stage],0,1)
            paths=[]
            def save(name,value):
                p=directory/name
                if isinstance(value,pd.DataFrame): atomic_csv(p,value,index=False)
                else: atomic_json(p,value)
                paths.append(p)
            if not reused and stage=='construction':
                tables=load_tables(root/'data/raw/metadata')
                pool,reservation=development_pool(tables['train.csv'])
                series=tables['train_series.csv'].loc[tables['train_series.csv'][STUDY].isin(pool[STUDY])].copy()
                x,registry=protocol_features(pool,series)
                # Baseline entries stay visibly separate from new Round 1 families.
                baseline=[{'feature':c,'family':'baseline_acquisition_coverage','available_at_inference':True,
                    'uses_report_or_label':False,'learned_on_dataset':False,'predictive_status':'not_evaluated',
                    'mechanism':'Preserved M01 descriptors, not new features.'} for c in x if not c.startswith('r1__')]
                registry=pd.concat([pd.DataFrame(baseline),registry],ignore_index=True)
                save('features.private.csv',x.reset_index())
                save('feature_registry.csv',registry)
                save('reservation.json',reservation)
                save('sample_plan.private.csv',sample_plan(pool,series,n_studies=cfg['round1']['sample_studies'],seed=cfg['seed']))
                save('construction_summary.json',{'round':1,'development_studies':len(pool),'series':len(series),
                    'baseline_columns':sum(not c.startswith('r1__') for c in x),
                    'new_columns':sum(c.startswith('r1__') for c in x),'total_columns':x.shape[1],
                    'new_families':8,'model_fits':0,'official_score':None,'uses_labels_as_features':False})
            elif not reused:
                x=pd.read_csv(directory/'features.private.csv',dtype={STUDY:str}).set_index(STUDY)
                registry=pd.read_csv(directory/'feature_registry.csv')
                profile=feature_profile(x,registry); save('feature_profile.csv',profile)
                buckets={}
                for col in x:
                    h=digest(x[col].tolist()); buckets.setdefault(h,[]).append(col)
                duplicate_groups=[v for v in buckets.values() if len(v)>1]
                save('diagnostics.json',{'constant_columns':int(x.nunique().le(1).sum()),
                    'exact_duplicate_groups':duplicate_groups,'automatic_feature_drops':0,
                    'screening_fit_performed':False,'message':'Descriptive QA only; train-fold screening is deferred until supervised validation is approved.'})
            if paths: cache.commit(stage,paths)
            progress.log(stage,'complete',1,1)
            if stop_after==stage:
                receipt={'key':key,'status':'paused','stages':statuses,'run_directory':str(directory.relative_to(root))}
                atomic_json(root/'artifacts/r01_pause.json',receipt)
                return receipt
        if any(sha256(root/'data/raw/metadata'/n)!=h for n,h in hashes.items()): raise RuntimeError('Raw input mutation detected.')
        result={'key':key,'utc':utc(),'status':'complete','run_directory':str(directory.relative_to(root)),
            'stages':statuses,'model_fits':0,'official_score':None,'raw_inputs_unchanged':True}
        atomic_json(root/'artifacts/r01_latest.json',result)
        return result


def checked_round1(root):
    checked_m01(root)
    latest=json.loads((root/'artifacts/r01_latest.json').read_text())
    directory=root/latest['run_directory']
    if latest.get('status')!='complete' or directory.resolve().parent!=(root/'artifacts/r01').resolve():
        raise RuntimeError('Round 1 is not complete.')
    cache=StageCache(directory,latest['key'])
    if not all(cache.reuse(stage) for stage in ('construction','diagnostics')):
        raise RuntimeError('Round 1 checkpoints are incomplete.')
    context=json.loads((directory/'context.json').read_text())
    if context['source_hash']!=source_hash(root) or context['environment']!=current_environment():
        raise RuntimeError('Round 1 code/environment lineage changed.')
    return directory


def round2(root,limit=1):
    r1=checked_round1(root)
    if not 1<=limit<=6: raise ValueError('Pilot series limit must be between 1 and 6.')
    plan=pd.read_csv(r1/'sample_plan.private.csv',dtype={STUDY:str,SERIES:str})
    download=root/'artifacts/image_sample_download.json'
    if not download.exists(): raise RuntimeError('No complete authorized image series receipt. Round 2 stays gated.')
    receipt=json.loads(download.read_text())
    if receipt.get('plan_sha256')!=sha256(r1/'sample_plan.private.csv'): raise RuntimeError('Image sample was selected from a different plan.')
    available=[]
    for row in plan.to_dict('records'):
        lookup=digest([row[STUDY],row[SERIES]])
        entry=receipt.get('series',{}).get(lookup)
        if entry and entry.get('complete'): available.append((row,entry))
    if not available: raise RuntimeError('No complete sample series is available. Do not use partial downloads.')
    selected=available[:limit]
    cfg=json.loads((root/'configs/research_rounds.json').read_text())
    progress=Progress(root/'logs/round2_progress.jsonl',300,4)
    entries=[]; rows=[]; registry=None; computed=reused=0
    with exclusive_lock(root/'artifacts/r02.lock'):
        for number,(item,entry) in enumerate(selected,1):
            files={}
            for relative,expected in entry['files'].items():
                p=root/relative
                if p.is_symlink() or not p.is_file() or not p.resolve().is_relative_to((root/'data/raw/dicom_sample').resolve()) or sha256(p)!=expected:
                    raise RuntimeError('Sample file integrity or path check failed.')
                files[relative]=expected
            context={'files':files,'source_hash':source_hash(root),'environment':current_environment(),
                     'round2_config':cfg['round2'],'metadata':item}
            key=digest(context); directory=root/'artifacts/r02_series'/key[:20]; cache=StageCache(directory,key)
            if cache.reuse('representation'):
                reused+=1; result=json.loads((directory/'features.json').read_text()); progress.log('image_features','series_reused_verified',number,len(selected))
            else:
                progress.log('image_features','loading_complete_series',number-1,len(selected))
                volume,geometry=load_volume([root/p for p in files],item[STUDY],item[SERIES],item['Anatomical_Plane'])
                normalized,normalization=normalize(volume)
                features,records=image_features(normalized,geometry)
                result={'features':features,'registry':records,'normalization':normalization}
                atomic_json(directory/'features.json',result); atomic_json(directory/'context.json',context)
                cache.commit('representation',[directory/'features.json',directory/'context.json'])
                computed+=1; progress.log('image_features','series_checkpoint_saved',number,len(selected))
                del volume,normalized
            if registry is not None and registry!=result['registry']: raise RuntimeError('Series feature dictionaries differ.')
            registry=result['registry']; rows.append({STUDY:item[STUDY],SERIES:item[SERIES],
                'Anatomical_Plane':item['Anatomical_Plane'],**result['features']})
            entries.append({'key':key,'directory':str(directory.relative_to(root))})
        features=pd.DataFrame(rows)
        key=digest({'series':entries,'source_hash':source_hash(root),'limit':limit})
        directory=root/'artifacts/r02'/key[:20]; directory.mkdir(parents=True,exist_ok=True)
        atomic_csv(directory/'series_features.private.csv',features)
        dictionary=pd.DataFrame(registry); atomic_csv(directory/'feature_registry.csv',dictionary)
        x=features.set_index([STUDY,SERIES,'Anatomical_Plane'])
        atomic_csv(directory/'feature_profile.csv',feature_profile(x,dictionary))
        # Preserve view identity: never treat multiple planes as independent patients.
        wide=features.pivot(index=STUDY,columns='Anatomical_Plane',values=list(x.columns))
        complete=pd.MultiIndex.from_product([list(x.columns),PLANES])
        wide=wide.reindex(columns=complete); wide.columns=[f'{p.lower()}__{f}' for f,p in wide.columns]
        for p in PLANES: wide[p.lower()+'__view_present']=wide.index.isin(features.loc[features.Anatomical_Plane.eq(p),STUDY]).astype(int)
        atomic_csv(directory/'study_features.private.csv',wide.reset_index())
        summary={'round':2,'status':'pilot_complete','series_processed':len(rows),'studies_processed':features[STUDY].nunique(),
            'planned_series':len(plan),'available_complete_series':len(available),'pilot_series_limit':limit,
            'per_series_feature_columns':len(x.columns),'study_feature_columns':len(wide.columns),
            'families':8,'computed_series':computed,'reused_verified_series':reused,
            'model_fits':0,'official_score':None,'anatomical_segmentation_performed':False,
            'raw_images_in_return_package':False,'registry_status':'prepared_candidates_executed_locally_not_predictively_validated'}
        atomic_json(directory/'summary.json',summary)
        atomic_json(directory/'series_receipts.json',entries)
        cache=StageCache(directory,key)
        cache.commit('aggregate',[directory/n for n in ('series_features.private.csv','study_features.private.csv',
            'feature_registry.csv','feature_profile.csv','summary.json','series_receipts.json')])
        result={'utc':utc(),'key':key,'status':'pilot_complete','run_directory':str(directory.relative_to(root)),**summary}
        atomic_json(root/'artifacts/r02_latest.json',result)
        return result
