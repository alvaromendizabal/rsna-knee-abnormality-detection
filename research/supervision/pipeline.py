"""Source-locked split construction and matched weak-supervision experiments.

No gold outcome analysis, no network, no model fit, and no image download.
This creates candidates for review; it does not approve a training-label source.
"""
from __future__ import annotations
import collections, csv, importlib.metadata, json, re, unicodedata
from pathlib import Path
import numpy as np
from common import (ROOT,STAGE,WORK,NB,LABELS,STATES,ARMS,Stop,Progress,atomic,save_json,
                    read_json,sha,digest,source_map,environment,require_tests,lock,checkpoint,utc)
from labels import normalized_report, extract


def core_source_hash(root=ROOT):
    paths=[]
    for folder in ('src','scripts','tests','configs'):
        paths += [p for p in (root/folder).rglob('*') if p.is_file() and p.suffix in ('.py','.sh','.json','.csv') and '__pycache__' not in p.parts]
    paths += [root/'requirements-audit.txt',root/'pytest.ini']
    return digest({str(p.relative_to(root)):sha(p) for p in sorted(paths)})

def checked_previous():
    cfg=read_json(STAGE/'protocol.json');expected=cfg['previous']
    if core_source_hash()!=expected['core_source_hash']:raise Stop('PREVIOUS_RESEARCH_SOURCE_CHANGED_PRESERVE_AND_INSPECT')
    r=read_json(ROOT/'artifacts/test_receipt.json')
    if r.get('source_hash')!=expected['core_source_hash'] or r.get('status')!='passed' or r.get('tests')!=123 or any(r.get(x)!=0 for x in ('returncode','failures','errors','skipped')):
        raise Stop('PREVIOUS_TEST_EVIDENCE_MISMATCH')
    if sha(ROOT/'artifacts/tests.xml')!=r['junit_sha256']:raise Stop('PREVIOUS_TEST_XML_CHANGED')
    protected={}
    for filename,h in expected['metadata_sha256'].items():
        p=ROOT/'data/raw/metadata'/filename
        if p.is_symlink() or not p.is_file() or sha(p)!=h:raise Stop('METADATA_BYTES_CHANGED')
        protected[str(p.relative_to(ROOT))]=h
    for stem,key in expected['stage_keys'].items():
        p=ROOT/'artifacts'/f'{stem}_latest.json';val=read_json(p)
        if val.get('key')!=key or val.get('status') not in ('complete','pilot_complete'):raise Stop('PREVIOUS_STAGE_KEY_CHANGED')
        protected[str(p.relative_to(ROOT))]=sha(p)
    for n in expected['completed_notebooks']:
        p=ROOT/'notebooks'/n
        if not p.is_file() or p.is_symlink():raise Stop('PRIOR_NOTEBOOK_MISSING')
        protected[str(p.relative_to(ROOT))]=sha(p)
    return cfg,protected

def load_availability_only(path):
    # Read only the presence/absence of gold cells; never convert or summarize
    # their 0/1 values. Do not include gold report text in the candidate sample.
    rows=[]
    with Path(path).open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f)
        if set(reader.fieldnames or [])!={'StudyInstanceUID','Report',*LABELS}:raise Stop('TRAIN_SCHEMA_CHANGED')
        for raw in reader:
            rows.append({'id':raw['StudyInstanceUID'],'report':raw['Report'],
                         'has_gold':any((raw[l] or '').strip()!='' for l in LABELS)})
    if not rows or len(rows)>10000:raise Stop('TRAIN_ROW_CAP')
    if len({r['id'] for r in rows})!=len(rows):raise Stop('DUPLICATE_STUDY_ID')
    return rows

def split_rows(rows,pilot_ids,seed=20260914):
    # Exact normalized report grouping is conservative, NOT verified patient ID.
    # Case folding can reserve extra duplicates beyond the previous four.
    groups={r['id']:digest(normalized_report(r['report'])) for r in rows}
    protected={groups[r['id']] for r in rows if r['has_gold']}
    pilot_groups={groups[x] for x in pilot_ids if x in groups}
    assignment=[]
    for r in rows:
        g=groups[r['id']]
        if r['has_gold']:split='sealed_expert';fold=-1
        elif g in protected:split='expert_report_overlap';fold=-1
        else:
            fold=1 if g in pilot_groups else int(digest([seed,'split',g])[:16],16)%5
            split='development_unlabeled' if fold==0 else 'training_unlabeled'
        assignment.append({'id':r['id'],'group':g,'split':split,'fold':fold,'pilot_group':g in pilot_groups})
    permitted={a['group'] for a in assignment if a['split']=='training_unlabeled'}
    held={a['group'] for a in assignment if a['split']=='development_unlabeled'}
    if permitted&held or protected&(permitted|held):raise Stop('REPORT_GROUP_LEAKAGE')
    return assignment

def choose_pilot(rows,assignment,limit=256,seed=20260914):
    ids={a['id']:a for a in assignment if a['split']=='training_unlabeled'}
    bygroup={}
    for r in rows:
        if r['id'] in ids:bygroup.setdefault(ids[r['id']]['group'],[]).append(r)
    order=sorted(bygroup,key=lambda g:digest([seed,'supervision_sample',g]))[:limit]
    result=[min(bygroup[g],key=lambda r:digest([seed,'representative',r['id']])) for g in order]
    if not result:raise Stop('NO_TRAINING_REPORTS_AVAILABLE')
    return result

def script_flags(report):
    names=set()
    for c in report:
        if c.isalpha():
            n=unicodedata.name(c,'')
            names.add(next((s for s in ('LATIN','CYRILLIC','GREEK') if s in n),'OTHER'))
    return names

def analyze_sample(sample,progress=None):
    records=[];script_counts=collections.Counter()
    for index,row in enumerate(sample,1):
        script_counts.update(script_flags(row['report']))
        record={'id':row['id'],'arms':{arm:extract(row['report'],arm) for arm in ARMS}}
        records.append(record)
        if progress and (index%32==0 or index==len(sample)):progress.log('assertion_comparisons',index,len(sample))
    counts={a:{l:{s:0 for s in STATES} for l in LABELS} for a in ARMS}
    for r in records:
        for arm in ARMS:
            for label,state in r['arms'][arm].items():counts[arm][label][state]+=1
    disagreement={a:{l:sum(r['arms'][a][l]!=r['arms']['joint_context'][l] for r in records) for l in LABELS}
                  for a in ARMS if a!='joint_context'}
    observed=np.asarray([[r['arms']['joint_context'][l] in ('positive','negative') for l in LABELS] for r in records],dtype=int)
    shared=observed.T@observed
    union=observed.sum(axis=0)[:,None]+observed.sum(axis=0)[None,:]-shared
    jaccard=np.divide(shared,union,out=np.zeros_like(shared,dtype=float),where=union>0)
    aggregate={'sampled_reports':len(sample),'counts':counts,'disagreement_with_joint':disagreement,
               'scripts':{s:int(script_counts[s]) for s in ('LATIN','CYRILLIC','GREEK','OTHER')},
               'binary_evidence_jaccard':jaccard.tolist(),'binary_evidence_union':union.tolist(),
               'clinical_accuracy':None,'official_auc':None,'training_targets_approved':False,
               'extraction_language_scope':'English lexical patterns only; no inferred language identity'}
    return records,aggregate

def write_csv(path,rows):
    import io
    if not rows:raise Stop('EMPTY_OUTPUT_TABLE')
    text=io.StringIO(newline='');w=csv.DictWriter(text,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    atomic(path,text.getvalue().encode())

def run_analysis():
    require_tests();cfg,protected=checked_previous();p=Progress(cfg['limits']['analysis_seconds'])
    lineage={'source':source_map(),'environment':environment(),'protected':protected,'config':cfg}
    key=digest(lineage);directory=WORK/'runs'/key[:20]
    with lock('analysis'):
        if checkpoint(directory,key):
            result={'utc':utc(),'status':'complete','key':key,'directory':str(directory.relative_to(ROOT)),
                    'stage':'reused_verified','new_reports_processed':0,'model_fits':0,'official_auc':None}
            save_json(WORK/'latest.json',result);print('SUPERVISION_CHECKPOINT_REUSED',flush=True);return result
        directory.mkdir(parents=True,exist_ok=True)
        p.log('split',0,1,'reading_metadata')
        rows=load_availability_only(ROOT/'data/raw/metadata/train.csv')
        if sum(r['has_gold'] for r in rows)!=58:raise Stop('SEALED_EXPERT_COUNT_CHANGED')
        r1=read_json(ROOT/'artifacts/r01_latest.json');plan=ROOT/r1['run_directory']/'sample_plan.private.csv'
        if not plan.resolve().is_relative_to((ROOT/'artifacts/r01').resolve()) or plan.is_symlink():raise Stop('PRIOR_SAMPLE_PLAN_PATH')
        with plan.open(newline='') as f:pilot_ids={r['StudyInstanceUID'] for r in csv.DictReader(f)}
        assignment=split_rows(rows,pilot_ids,cfg['seed']);sample=choose_pilot(rows,assignment,cfg['sample_reports'],cfg['seed'])
        if any(r['has_gold'] for r in sample):raise Stop('SEALED_EXPERT_LEAKAGE')
        write_csv(directory/'split_assignments.private.csv',assignment)
        split_counts=collections.Counter(a['split'] for a in assignment)
        fold_groups={str(i):len({a['group'] for a in assignment if a['fold']==i}) for i in range(5)}
        p.log('split',1,1,'assignment_written')
        records,aggregate=analyze_sample(sample,p)
        save_json(directory/'candidate_states.private.json',{'records':records,'training_use_allowed':False})
        # Blinded review priority, not a random accuracy sample. Reports stay
        # local and are explicitly excluded from every return-package path.
        scores={r['id']:sum(r['arms']['mention_only'][l]!=r['arms']['joint_context'][l] for l in LABELS) for r in records}
        chosen=sorted(sample,key=lambda r:(-scores[r['id']],digest([cfg['seed'],r['id']])))[:24]
        save_json(directory/'review_queue.private.json',{'purpose':'English-scope and assertion review; not an accuracy estimate',
            'reports':[{'StudyInstanceUID':r['id'],'Report':r['report'],'review_status':'unreviewed'} for r in chosen],
            'do_not_upload':True})
        aggregate['split_counts']={k:int(split_counts[k]) for k in ('sealed_expert','expert_report_overlap','training_unlabeled','development_unlabeled')}
        aggregate['fold_groups']=fold_groups
        aggregate['groups_crossing_training_development']=0
        aggregate['gold_outcomes_used']=False
        aggregate['patient_disjointness_verified']=False
        aggregate['pilot_image_studies_forced_to_training']=sum(a['id'] in pilot_ids and a['split']=='training_unlabeled' for a in assignment)
        aggregate['pilot_studies_excluded_by_sealed_overlap']=sum(a['id'] in pilot_ids and a['split'] in ('sealed_expert','expert_report_overlap') for a in assignment)
        aggregate['supervision_comparisons']=len(ARMS)
        aggregate['label_cells_per_arm']=len(sample)*len(LABELS)
        save_json(directory/'summary.json',aggregate)
        save_json(directory/'lineage.json',lineage)
        save_json(directory/'DECISION.json',{'status':'REVIEW_REQUIRED_BEFORE_TARGET_PROMOTION','model_fits':0,'official_auc':None,
            'next':'Review English-scope, abstention and disagreement; design a multilingual teacher/annotation comparison before image training.',
            'frozen_image_experiment_plan':'joint multi-plane representation plus matched leave-one-family-out experiments; same encoder, folds and budget',
            'holdout_policy':'58 expert-labeled studies plus normalized-report overlaps sealed; development split is not patient-verified'})
        for rel,h in protected.items():
            if sha(ROOT/rel)!=h:raise Stop('PROTECTED_FILE_CHANGED_DURING_ANALYSIS')
        files={f.name:sha(f) for f in directory.iterdir() if f.is_file() and f.name!='CHECKPOINT.json'}
        save_json(directory/'CHECKPOINT.json',{'key':key,'status':'complete','utc':utc(),'files':files})
        result={'utc':utc(),'status':'complete','key':key,'directory':str(directory.relative_to(ROOT)),
                'stage':'computed','new_reports_processed':len(sample),'model_fits':0,'official_auc':None}
        save_json(WORK/'latest.json',result);p.log('finish',1,1,'checkpoint_complete')
        return result

def current_run():
    require_tests();cfg,protected=checked_previous();v=read_json(WORK/'latest.json');d=ROOT/v['directory']
    if d.is_symlink() or not d.resolve().is_relative_to((WORK/'runs').resolve()):raise Stop('RUN_DIRECTORY_UNSAFE')
    key=digest({'source':source_map(),'environment':environment(),'protected':protected,'config':cfg})
    if v.get('key')!=key or not checkpoint(d,key):raise Stop('CURRENT_RUN_LINEAGE_MISMATCH')
    return d,read_json(d/'summary.json')
