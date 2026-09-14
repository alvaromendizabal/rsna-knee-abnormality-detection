"""Metadata-only milestone. No image loading, training, report labeling, or network."""
from __future__ import annotations
from collections import Counter
from functools import lru_cache
import json
from pathlib import Path
import re
import unicodedata
import numpy as np
import pandas as pd
from .schema import FILES, LABELS, PLANES, STUDY, load_tables
from .representations import acquisition_features, feature_dictionary
from .runtime import (Progress, StageCache, atomic_csv, atomic_json, digest, exclusive_lock,
                      require_tests, sha256, source_hash, utc, versions)

@lru_cache(maxsize=8192)
def script_of(character: str):
    if not character.isalpha(): return None
    name = unicodedata.name(character, '')
    return next((x for x in ('LATIN','GREEK','CYRILLIC') if x in name), 'OTHER')

def report_profile(reports: pd.Series, progress: Progress) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    lengths, scripts, hashes = [], Counter(), Counter()
    blank = 0
    for i, text in enumerate(reports.astype(str), start=1):
        if len(text) > 2_000_000: raise ValueError('A report exceeds the 2M-character safety cap.')
        lengths.append(len(text))
        normalized = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', text)).strip()
        if not normalized: blank += 1
        else: hashes[digest(normalized)] += 1
        for script in {script_of(c) for c in set(text)} - {None}: scripts[script] += 1
        if i % 200 == 0 or i == len(reports): progress.log('supervision', 'reports_profiled', i, len(reports))
    bins = [0,250,500,1000,2000,4000,8000,16000,2_000_001]
    counts, _ = np.histogram(lengths, bins=bins)
    histogram = pd.DataFrame({'character_range':[f'{a}–{b-1}' for a,b in zip(bins[:-1],bins[1:])],
                              'reports':counts})
    scripts_frame = pd.DataFrame({'script':['LATIN','GREEK','CYRILLIC','OTHER'],
                                 'reports_with_script':[scripts[x] for x in ('LATIN','GREEK','CYRILLIC','OTHER')]})
    summary = dict(blank_reports=blank, duplicate_normalized_report_groups=sum(n>1 for n in hashes.values()),
        reports_in_duplicate_groups=sum(n for n in hashes.values() if n>1),
        scripts_are_not_language_labels=True, duplicate_text_is_not_patient_identity=True,
        raw_text_exported=False, expert_label_values_exported=False)
    return histogram, scripts_frame, summary

def run(root: Path, stop_after: str | None = None) -> dict:
    require_tests(root)
    config = json.loads((root/'configs/milestone01.json').read_text())
    raw = root/config['raw_directory']
    with exclusive_lock(root/'artifacts/m01.lock'):
        data_hashes = {name:sha256(raw/name) for name in FILES}
        total_bytes = sum((raw/name).stat().st_size for name in FILES)
        if total_bytes > config['maximum_total_csv_bytes']: raise ValueError('Total CSV size cap exceeded.')
        context = dict(data_sha256=data_hashes, source_hash=source_hash(root), environment=versions(), config=config)
        key = digest(context); directory = root/'artifacts/m01'/key[:20]
        cache = StageCache(directory, key)
        atomic_json(directory/'context.json', context)
        progress = Progress(directory/'progress.jsonl', config['worker_soft_seconds'], config['worker_rss_gib'])
        progress.log('load', 'reading_five_csvs', 0, 5)
        tables = load_tables(raw)
        progress.log('load', 'schema_and_joins_checked', 5, 5)
        train = tables['train.csv']; test = tables['test.csv']; ts = tables['train_series.csv']
        stages = {}
        for stage in ('schema','supervision','representation'):
            reused = cache.reuse(stage); stages[stage] = 'reused_verified' if reused else 'computed'
            progress.log(stage, stages[stage], 0, 1)
            paths = []
            def save_json(name, value):
                p=directory/name; atomic_json(p,value); paths.append(p)
            def save_csv(name, frame, index=False):
                p=directory/name; atomic_csv(p,frame,index=index); paths.append(p)
            if not reused and stage == 'schema':
                observed = train[LABELS].notna().sum(axis=1)
                save_json('schema_summary.json', dict(status='PASS', utc=utc(), row_counts={k:len(v) for k,v in tables.items()},
                    csv_total_mib=round(total_bytes/1024**2,3), fully_labeled_studies=int(observed.eq(12).sum()),
                    partially_labeled_studies=int(observed.between(1,11).sum()), unlabeled_studies=int(observed.eq(0).sum()),
                    unknown_label_cells=int(train[LABELS].isna().sum().sum()), unknowns_kept_missing=True,
                    unique_ids=True, referential_integrity=True,
                    train_example_study_overlap=int(len(set(train[STUDY])&set(test[STUDY]))),
                    example_data_is_not_a_validation_split=True,
                    patient_disjointness_verified=False, patient_identifier_in_documented_csv=False,
                    reports_available_in_test=False, example_test_is_full_hidden_test=False,
                    dicom_content_verified=False, model_fits=0, official_score=None))
                save_csv('table_sizes.csv', pd.DataFrame([dict(table=k,rows=len(v),mib=(raw/k).stat().st_size/1024**2)
                                                        for k,v in tables.items()]))
            elif not reused and stage == 'supervision':
                availability = train[LABELS].notna().sum()
                save_csv('label_availability.csv', pd.DataFrame({'target':LABELS,'observed':availability.values,
                                                               'unknown':len(train)-availability.values}))
                observed = train[LABELS].notna().sum(axis=1)
                save_csv('label_completeness.csv', pd.DataFrame({'observed_targets':range(13),
                    'studies':[int(observed.eq(i).sum()) for i in range(13)]}))
                hist,scripts,summary = report_profile(train['Report'],progress)
                save_csv('report_length_histogram.csv',hist); save_csv('report_script_presence.csv',scripts)
                save_json('supervision_summary.json',summary)
            elif not reused and stage == 'representation':
                features = acquisition_features(train,ts)
                test_features = acquisition_features(test,tables['test_series.csv'])
                if list(features.columns)!=list(test_features.columns): raise ValueError('Feature schemas disagree.')
                # ID-bearing matrices remain private and are excluded from the return package.
                save_csv('train_acquisition_features.private.csv',features,index=True)
                save_csv('example_test_acquisition_features.private.csv',test_features,index=True)
                dictionary=feature_dictionary(features.columns)
                save_csv('feature_dictionary.csv',dictionary)
                profile=pd.DataFrame({'feature':features.columns,'distinct_values':features.nunique().values,
                    'minimum':features.min().values,'maximum':features.max().values,
                    'zero_fraction':features.eq(0).mean().values})
                save_csv('feature_profile.csv',profile)
                save_csv('series_plane_counts.csv',ts['Anatomical_Plane'].value_counts().reindex(PLANES,fill_value=0)
                         .rename_axis('plane').reset_index(name='series'))
                joint=ts.groupby(['Fluid_Sensitive','Fat_Suppression']).size().reindex(
                    pd.MultiIndex.from_product([[0,1],[0,1]],names=['Fluid_Sensitive','Fat_Suppression']),fill_value=0)
                save_csv('contrast_joint_counts.csv',joint.reset_index(name='series'))
                coverage=[]
                for plane in PLANES:
                    for fluid in (0,1):
                        for fat in (0,1):
                            selected=ts[(ts.Anatomical_Plane==plane)&(ts.Fluid_Sensitive==fluid)&(ts.Fat_Suppression==fat)]
                            coverage.append(dict(plane=plane,contrast=f'fluid={fluid}; fat={fat}',studies=selected[STUDY].nunique()))
                save_csv('plane_contrast_coverage.csv',pd.DataFrame(coverage))
                counts=ts.groupby(STUDY).size().value_counts().sort_index()
                save_csv('series_per_study.csv',counts.rename_axis('series_per_study').reset_index(name='studies'))
                plane_counts=ts.groupby(STUDY).Anatomical_Plane.nunique().value_counts().reindex([1,2,3],fill_value=0)
                save_csv('planes_per_study.csv',plane_counts.rename_axis('planes_available').reset_index(name='studies'))
                save_json('representation_summary.json',dict(candidate_columns=len(features.columns),
                    constant_columns=int(features.nunique().le(1).sum()), studies=len(features),
                    no_features_dropped=True, uses_reports=False, uses_clinical_labels=False,
                    predictive_utility='NOT_TESTED', train_test_schema_match=True, model_fits=0))
            if not reused: cache.commit(stage,paths)
            progress.log(stage,'stage_complete',1,1)
            if stop_after == stage:
                receipt=dict(utc=utc(),status='paused_as_requested',key=key,stage=stage,stages=stages)
                atomic_json(root/'artifacts/m01_pause_receipt.json',receipt)
                return receipt
        if data_hashes != {name:sha256(raw/name) for name in FILES}: raise RuntimeError('Raw input bytes changed.')
        result=dict(utc=utc(),status='complete',key=key,run_directory=str(directory.relative_to(root)),stages=stages,
                    raw_inputs_unchanged=True,model_fits=0,image_files_downloaded=0,official_score=None)
        atomic_json(directory/'completion.json',result); atomic_json(root/'artifacts/m01_latest.json',result)
        progress.log('finish','complete',3,3)
        return result
