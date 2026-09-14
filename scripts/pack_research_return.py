#!/usr/bin/env python3
"""User-run allowlisted evidence ZIP. No upload, raw data, credentials or MRI pixels."""
from pathlib import Path
import argparse
import json
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_knee.runtime import StageCache,atomic_json,digest,require_tests,sha256,source_hash,utc
from rsna_research.workflow import checked_round1,current_environment

def notebook_evidence(path,expected):
    doc=json.loads(path.read_text()); cells=[c for c in doc['cells'] if c['cell_type']=='code']
    sources=[''.join(c['source']) if isinstance(c['source'],list) else c['source'] for c in cells]
    if digest(sources)!=expected['code_sha256']: raise RuntimeError('Notebook code differs from prepared source; preserve your edits and stop.')
    if [c.get('execution_count') for c in cells]!=list(range(1,len(cells)+1)):
        raise RuntimeError('Restart Kernel and Run All, then save the notebook before packaging.')
    figures=0; text=''
    for cell in cells:
        for output in cell.get('outputs',[]):
            if output.get('output_type')=='error': raise RuntimeError('Notebook contains an error output.')
            figures+=int('application/vnd.plotly.v1+json' in output.get('data',{}))
            value=output.get('text',''); text+=''.join(value) if isinstance(value,list) else value
    if figures<expected['minimum_plotly_outputs'] or expected['completion_marker'] not in text:
        raise RuntimeError('Notebook is missing expected inline plots or completion marker.')
    return {'code_cells':len(cells),'inline_plotly_outputs':figures,'structural_execution_evidence':True,
        'actual_visual_reopening':'user must confirm separately; not inferred from MIME presence'}

def main():
    parser=argparse.ArgumentParser(description=__doc__); parser.add_argument('--through',type=int,choices=[1,2],default=1)
    args=parser.parse_args(); require_tests(ROOT); r1=checked_round1(ROOT)
    latest=json.loads((ROOT/'artifacts/r01_latest.json').read_text())
    pause=json.loads((ROOT/'artifacts/r01_pause.json').read_text())
    if latest['key']!=pause['key'] or latest['stages']['construction']!='reused_verified':
        raise RuntimeError('Round 1 controlled pause/resume evidence is missing.')
    m01=json.loads((ROOT/'artifacts/m01_latest.json').read_text()); mdir=ROOT/m01['run_directory']
    mpause=json.loads((ROOT/'artifacts/m01_pause_receipt.json').read_text())
    if mpause['key']!=m01['key'] or m01['stages']['schema']!='reused_verified': raise RuntimeError('M01 pause/resume evidence is missing.')
    manifest=json.loads((ROOT/'ARTIFACT_MANIFEST.json').read_text())['notebooks']
    new=json.loads((ROOT/'RESEARCH_ARTIFACT_MANIFEST.json').read_text())['notebooks']
    names=['notebooks/02_protocol_feature_investigation.ipynb']
    if args.through==2: names.append('notebooks/03_image_context_feature_investigation.ipynb')
    manifest.update({name:new[name] for name in names})
    evidence={name:notebook_evidence(ROOT/name,spec) for name,spec in manifest.items()}
    files=[ROOT/name for name in manifest]
    files += [ROOT/n for n in ('artifacts/preflight.json','artifacts/test_receipt.json','artifacts/tests.xml',
        'logs/tests.log','artifacts/m01_latest.json','artifacts/m01_pause_receipt.json',
        'artifacts/r01_latest.json','artifacts/r01_pause.json')]
    mnames=['context.json','schema_summary.json','table_sizes.csv','label_availability.csv','label_completeness.csv',
        'report_length_histogram.csv','report_script_presence.csv','supervision_summary.json','feature_dictionary.csv',
        'feature_profile.csv','series_plane_counts.csv','contrast_joint_counts.csv','plane_contrast_coverage.csv',
        'series_per_study.csv','planes_per_study.csv','representation_summary.json','schema.manifest.json',
        'supervision.manifest.json','representation.manifest.json','completion.json']
    files += [mdir/n for n in mnames]
    files += [r1/n for n in ('context.json','feature_registry.csv','reservation.json','construction_summary.json',
        'feature_profile.csv','diagnostics.json','construction.manifest.json','diagnostics.manifest.json')]
    if (ROOT/'artifacts/publication_inventory.json').is_file():
        # Git filenames can contain private identifiers; include a counts/flags-only projection.
        original=json.loads((ROOT/'artifacts/publication_inventory.json').read_text())
        allow=['utc','scope','account_operations','history_scan_complete','is_git_repository','working_tree_dirty',
               'head','history_review_required','license_review_required','visibility_and_remote_history_unverified','status','exception_type']
        public={k:original[k] for k in allow if k in original}
        public['possible_private_history_path_count']=len(original.get('possible_private_history_paths',[]))
        atomic_json(ROOT/'artifacts/publication_inventory_summary.json',public)
        files.append(ROOT/'artifacts/publication_inventory_summary.json')
    if args.through==2:
        r2=json.loads((ROOT/'artifacts/r02_latest.json').read_text()); directory=ROOT/r2['run_directory']
        if directory.resolve().parent!=(ROOT/'artifacts/r02').resolve() or r2['status']!='pilot_complete': raise RuntimeError('Round 2 pilot is incomplete.')
        if r2['computed_series']!=0 or r2['reused_verified_series']<1: raise RuntimeError('Demonstrate exact-checkpoint reuse in notebook 03.')
        if not StageCache(directory,r2['key']).reuse('aggregate'): raise RuntimeError('Round 2 aggregate evidence failed.')
        for entry in json.loads((directory/'series_receipts.json').read_text()):
            series=ROOT/entry['directory']
            if series.resolve().parent!=(ROOT/'artifacts/r02_series').resolve(): raise RuntimeError('Invalid series checkpoint path.')
            if not StageCache(series,entry['key']).reuse('representation'): raise RuntimeError('Series checkpoint integrity failed.')
            context=json.loads((series/'context.json').read_text())
            if context['source_hash']!=source_hash(ROOT) or context['environment']!=current_environment(): raise RuntimeError('Series source/environment changed.')
            for relative,expected in context['files'].items():
                p=ROOT/relative
                if p.is_symlink() or not p.resolve().is_relative_to((ROOT/'data/raw/dicom_sample').resolve()) or sha256(p)!=expected:
                    raise RuntimeError('Raw image checkpoint bytes changed.')
        files.append(ROOT/'artifacts/r02_latest.json')
        files += [directory/n for n in ('feature_registry.csv','feature_profile.csv','summary.json','series_receipts.json','aggregate.manifest.json')]
    files=sorted(set(files))
    for path in files:
        if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(ROOT.resolve()): raise RuntimeError('Missing or unsafe evidence file.')
        if path.stat().st_size>32*1024**2: raise RuntimeError('Evidence file exceeds the 32 MiB cap; inspect rather than truncate.')
    if sum(p.stat().st_size for p in files)>100*1024**2: raise RuntimeError('Return evidence exceeds 100 MiB.')
    report={'utc':utc(),'through_round':args.through,'notebooks':evidence,'model_fits':0,'official_score':None,
        'github_state':'unverified; no GitHub actions performed by this script',
        'files':{str(p.relative_to(ROOT)):sha256(p) for p in files},
        'excluded':['raw CSVs','reports','DICOMs','signed URLs','credentials','row-level matrices','private install/download logs'],
        'privacy':'Review locally before sharing. No automated check guarantees complete de-identification.'}
    dest=ROOT/'returns/rsna-knee-research-return.zip'; dest.parent.mkdir(exist_ok=True)
    pending=dest.with_suffix('.pending.zip')
    with zipfile.ZipFile(pending,'w',zipfile.ZIP_DEFLATED) as archive:
        for path in files: archive.write(path,str(path.relative_to(ROOT)))
        archive.writestr('RETURN_MANIFEST.json',json.dumps(report,indent=2))
    pending.replace(dest)
    atomic_json(ROOT/'returns/research_return_receipt.json',{'utc':utc(),'sha256':sha256(dest),'bytes':dest.stat().st_size,'uploaded':False})
    print('Created returns/rsna-knee-research-return.zip. Review it before sharing; nothing uploaded.')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print('STOP: '+str(exc) if isinstance(exc,RuntimeError) else 'STOP: evidence packaging failed; inspect the missing gate locally.')
        raise SystemExit(1)
