"""Four frozen training reports, two matched prompt arms, no target promotion."""
from __future__ import annotations
import collections, csv, json, time
from pathlib import Path
from teacher_common import ROOT,STAGE,WORK,LABELS,STATES,ARMS,Stop,Progress,read_json,save_json,sha,digest,source_map,environment,previous,require_tests,lock,utc
from teacher_contract import scripts,validate_output,CANARIES,canary_matches
from teacher_runtime import checked_assets,LocalServer


def select_reports(rows,assignments,candidates,limit=4,max_chars=3000):
    """Reuse prior pilot IDs and frozen groups; never choose on expert outcomes."""
    assignment={a['id']:a for a in assignments}
    permitted={r['id']:r for r in candidates['records']}
    eligible=[];excluded=collections.Counter()
    for row in rows:
        sid=row['id']
        if sid not in permitted:continue
        a=assignment.get(sid)
        if not a or a['split']!='training_unlabeled' or row['has_gold']:
            raise Stop('PREVIOUS_PILOT_HOLDOUT_VIOLATION')
        if not row['report'].strip():excluded['blank']+=1;continue
        if len(row['report'])>max_chars:excluded['over_character_cap_not_truncated']+=1;continue
        flags=scripts(row['report'])
        eligible.append({**row,'group':a['group'],'scripts':sorted(flags),'lexical':permitted[sid]['arms']['joint_context']})
    order=sorted(eligible,key=lambda r:digest([20260914,'teacher-selection',r['group'],r['id']]))
    result=[];used=set()
    # A deliberately heterogeneous operational sample, NOT a prevalence sample.
    for kind in ('CYRILLIC','GREEK','OTHER','LATIN'):
        found=next((r for r in order if r['group'] not in used and kind in r['scripts']),None)
        if found:result.append(found);used.add(found['group'])
        if len(result)==limit:break
    for r in order:
        if len(result)==limit:break
        if r['group'] not in used:result.append(r);used.add(r['group'])
    if len(result)!=limit:raise Stop('FOUR_ELIGIBLE_FROZEN_TRAINING_GROUPS_REQUIRED')
    for i,r in enumerate(result):r['sample_alias']=f'S{i+1:02d}'
    return result,{'eligible_reports':len(eligible),'excluded':dict(excluded),'selected_reports':len(result),
                  'scripts':{s:sum(s in r['scripts'] for r in result) for s in ('LATIN','CYRILLIC','GREEK','OTHER')}}

def load_selection(directory):
    assignment=list(csv.DictReader((directory/'split_assignments.private.csv').open(newline='',encoding='utf-8')))
    candidates=read_json(directory/'candidate_states.private.json')
    if candidates.get('training_use_allowed') is not False:raise Stop('PREVIOUS_TARGET_APPROVAL_CHANGED')
    rows=[]
    with (ROOT/'data/raw/metadata/train.csv').open(newline='',encoding='utf-8-sig') as f:
        reader=csv.DictReader(f)
        if set(reader.fieldnames or [])!={'StudyInstanceUID','Report',*LABELS}:raise Stop('TRAIN_SCHEMA_CHANGED')
        for raw in reader:
            rows.append({'id':raw['StudyInstanceUID'],'report':raw['Report'],
                         'has_gold':any((raw[l] or '').strip()!='' for l in LABELS)})
    if len({r['id'] for r in rows})!=len(rows):raise Stop('DUPLICATE_RAW_STUDY')
    cfg=read_json(STAGE/'protocol.json')
    return select_reports(rows,assignment,candidates,cfg['reports'],cfg['max_report_characters'])

def load_call(directory,name,request_key):
    path=directory/'calls'/(name+'.private.json');receipt=directory/'calls'/(name+'.receipt.json')
    if not receipt.exists():
        if path.exists():raise Stop('UNRECEIPTED_PRIVATE_OUTPUT_PRESERVED')
        return None
    r=read_json(receipt)
    if r.get('request_key')!=request_key or not path.is_file() or sha(path)!=r.get('sha256'):raise Stop('CALL_CHECKPOINT_TAMPERED')
    return read_json(path)

def one_call(server,directory,name,report,arm,key,progress,expected=None):
    request_key=digest([key,name,digest(report),arm])
    old=load_call(directory,name,request_key)
    if old is not None:
        progress.log('inference_checkpoint_reused',call_alias=name,status=old['status']);return old,False
    # A prior started-but-unfinished request is evidence, not permission to retry forever.
    attempted=directory/'calls'/(name+'.attempt.json')
    if attempted.exists():raise Stop('UNFINISHED_INFERENCE_ATTEMPT_PRESERVED_REVIEW_BEFORE_RETRY')
    save_json(attempted,{'utc':utc(),'request_key':request_key,'status':'started'})
    progress.log('inference_started',call_alias=name,arm=arm)
    start=time.monotonic();result={'name':name,'arm':arm,'status':'invalid','model_inference_calls':0};before=server.inference_requests_sent
    try:
        text,timing=server.infer(report,arm)
        result['raw_output']=text;result['timing']=timing
        result['output']=validate_output(text,report);result['status']='valid'
        if expected is not None:
            result['canary_matches']=canary_matches(result['output'],expected)
            if not all(result['canary_matches'].values()):result['status']='canary_failed'
    except Stop as exc:
        result['code']=str(exc);result['timing']={'seconds':round(time.monotonic()-start,3),'prompt_tokens':0,'completion_tokens':0}
    result['model_inference_calls']=server.inference_requests_sent-before
    path=directory/'calls'/(name+'.private.json');save_json(path,result)
    save_json(directory/'calls'/(name+'.receipt.json'),{'utc':utc(),'request_key':request_key,'sha256':sha(path),'status':result['status']})
    progress.log('inference_finished',call_alias=name,status=result['status'],elapsed_call_seconds=result['timing']['seconds'])
    return result,True

def summarize(selected,selection,prior,records,outcome,new_calls,reused_calls):
    c={arm:{l:{s:0 for s in STATES} for l in LABELS} for arm in ['lexical_reference',*ARMS]}
    all_valid={arm:{} for arm in ARMS};timing={a:{'seconds':0.,'prompt_tokens':0,'completion_tokens':0} for a in ARMS}
    completed={a:0 for a in ARMS};invalid=collections.Counter();canaries=[]
    for item in selected:
        for l in LABELS:c['lexical_reference'][l][item['lexical'][l]]+=1
    for r in records:
        if r['name'].startswith('C'):
            canaries.append({'name':r['name'],'status':r['status'],'matches':[int(r.get('canary_matches',{}).get(l,False)) for l in LABELS]});continue
        a=r['arm'];t=r.get('timing',{})
        for k in timing[a]:timing[a][k]+=t.get(k,0)
        if r['status']!='valid':invalid[r.get('code',r['status'])]+=1;continue
        completed[a]+=1;alias=r['name'].split('_')[0];all_valid[a][alias]=r['output']
        for l in LABELS:c[a][l][r['output'][l]['state']]+=1
    paired=sorted(set(all_valid[ARMS[0]])&set(all_valid[ARMS[1]]))
    differences={l:sum(all_valid[ARMS[0]][sid][l]['state']!=all_valid[ARMS[1]][sid][l]['state'] for sid in paired) for l in LABELS}
    # Only compare marginal counts on common successful reports (never shift denominators).
    pair_counts={a:{l:{s:0 for s in STATES} for l in LABELS} for a in ['lexical_reference',*ARMS]}
    sel={r['sample_alias']:r for r in selected}
    for sid in paired:
        for l in LABELS:
            pair_counts['lexical_reference'][l][sel[sid]['lexical'][l]]+=1
            for a in ARMS:pair_counts[a][l][all_valid[a][sid][l]['state']]+=1
    return {'status':outcome,'prior_sample_reports':prior['sampled_reports'],'prior_joint_counts':prior['counts']['joint_context'],
            'selection':selection,'selected_reports':len(selected),'canaries':canaries,'completed_reports':completed,
            'paired_reports':len(paired),'paired_counts':pair_counts,'all_observed_counts':c,'paired_disagreements':differences,
            'invalid_reasons':dict(invalid),'timing':timing,'new_model_calls':new_calls,'reused_calls':reused_calls,
            'total_attempted_calls':len(records),'model_fits':0,'official_auc':None,'clinical_accuracy':None,
            'training_targets_approved':False,'patient_disjointness_verified':False,'report_text_exported':False,
            'sealed_expert_studies':58,'sealed_report_overlap_studies':4,'candidate_source':'model output, not adjudicated ground truth'}

def finish(directory,key,summary,records,lineage):
    save_json(directory/'summary.json',summary);save_json(directory/'lineage.json',lineage)
    save_json(directory/'DECISION.json',{'status':'HUMAN_ADJUDICATION_REQUIRED','outcome':summary['status'],
              'training_targets_approved':False,'official_auc':None,'clinical_accuracy':None,
              'next':'Review original-language evidence locally; scale only after accuracy-oriented adjudication. No winner selected by candidate coverage.'})
    paths=[directory/'summary.json',directory/'lineage.json',directory/'DECISION.json',directory/'selection.private.json']
    paths += list((directory/'calls').glob('*.json'))
    save_json(directory/'CHECKPOINT.json',{'key':key,'outcome':summary['status'],'files':{str(p.relative_to(directory)):sha(p) for p in paths}})
    latest={'utc':utc(),'key':key,'directory':str(directory.relative_to(ROOT)),'outcome':summary['status'],
            'new_model_calls':summary['new_model_calls'],'reused_calls':summary['reused_calls'],'model_fits':0,'official_auc':None,'status':'recorded'}
    save_json(WORK/'latest.json',latest);return latest

def checked_checkpoint(directory,key):
    p=directory/'CHECKPOINT.json'
    if not p.exists():return False
    r=read_json(p)
    if r.get('key')!=key:raise Stop('TEACHER_CHECKPOINT_KEY_CHANGED')
    for name,h in r['files'].items():
        from teacher_common import safe_path
        if sha(safe_path(directory,name))!=h:raise Stop('TEACHER_CHECKPOINT_BYTES_CHANGED')
    return True

def analyze():
    require_tests();prior_directory,prior=previous();assets=checked_assets();cfg=read_json(STAGE/'protocol.json')
    selected,selection=load_selection(prior_directory)
    lineage={'source':source_map(),'environment':environment(),'previous_key':cfg['previous']['key'],
             'model_sha256':read_json(STAGE/'MODEL_PROVENANCE.json')['model']['sha256'],'runtime_files':assets[2]['files'],
             'selection_sha256':digest(selected),'configuration':cfg}
    key=digest(lineage);directory=WORK/'runs'/key[:20];progress=Progress()
    with lock('inference'):
        if checked_checkpoint(directory,key):
            summary=read_json(directory/'summary.json');latest={'utc':utc(),'key':key,'directory':str(directory.relative_to(ROOT)),
                'outcome':summary['status'],'status':'reused_verified','new_model_calls':0,'reused_calls':summary['total_attempted_calls'],'model_fits':0,'official_auc':None}
            save_json(WORK/'latest.json',latest);progress.log('whole_pilot_reused_verified',new_model_calls=0);return latest
        directory.mkdir(parents=True,exist_ok=True);save_json(directory/'selection.private.json',{'selected':selected,'do_not_upload':True})
        records=[];new=0;reused=0;outcome='complete'
        # Report data are sent only to this temporary, authenticated loopback server.
        with LocalServer(assets,cfg['limits']) as server:
            for i,canary in enumerate(CANARIES):
                r,fresh=one_call(server,directory,f'C{i+1:02d}',canary['report'],'domain_contract',key,progress,canary)
                records.append(r);new+=r.get('model_inference_calls',0) if fresh else 0;reused+=int(not fresh)
                if r['status']!='valid':outcome='blocked_canary';break
            if outcome=='complete':
                for i,item in enumerate(selected):
                    # Counterbalance order; this does not turn four reports into an accuracy sample.
                    order=ARMS if i%2==0 else list(reversed(ARMS))
                    for a in order:
                        r,fresh=one_call(server,directory,item['sample_alias']+'_'+a,item['report'],a,key,progress)
                        records.append(r);new+=r.get('model_inference_calls',0) if fresh else 0;reused+=int(not fresh)
                        if r['status']!='valid':outcome='blocked_output_contract';break
                    if outcome!='complete':break
        previous()  # raw and sealed evidence must remain byte-identical
        summary=summarize(selected,selection,prior,records,outcome,new,reused)
        latest=finish(directory,key,summary,records,lineage)
        progress.log('teacher_pilot_recorded',outcome=outcome,new_model_calls=new,reused_calls=reused)
        return latest

def current_run():
    require_tests();previous();latest=read_json(WORK/'latest.json')
    from teacher_common import safe_path
    d=safe_path(ROOT,latest['directory'])
    if not d.is_relative_to(WORK/'runs') or not checked_checkpoint(d,latest['key']):raise Stop('TEACHER_CHECKPOINT_NOT_READY')
    lineage=read_json(d/'lineage.json')
    if lineage['source']!=source_map() or lineage['environment']!=environment():raise Stop('TEACHER_SOURCE_OR_ENV_CHANGED')
    return d,read_json(d/'summary.json')
