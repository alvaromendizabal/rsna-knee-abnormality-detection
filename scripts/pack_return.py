#!/usr/bin/env python3
"""Package only allowlisted aggregate evidence and unchanged-source executed notebooks."""
import json
from pathlib import Path
import sys
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_knee.runtime import StageCache,atomic_json,digest,require_tests,sha256,utc

AGGREGATES=['context.json','schema_summary.json','table_sizes.csv','label_availability.csv',
 'label_completeness.csv','report_length_histogram.csv','report_script_presence.csv','supervision_summary.json',
 'feature_dictionary.csv','feature_profile.csv','series_plane_counts.csv','contrast_joint_counts.csv',
 'plane_contrast_coverage.csv','series_per_study.csv','planes_per_study.csv','representation_summary.json',
 'schema.manifest.json','supervision.manifest.json','representation.manifest.json','completion.json','progress.jsonl']

def notebook_evidence(path,expected):
    doc=json.loads(path.read_text()); cells=[c for c in doc['cells'] if c['cell_type']=='code']
    sources=[''.join(c['source']) if isinstance(c['source'],list) else c['source'] for c in cells]
    if digest(sources)!=expected['code_sha256']: raise RuntimeError('Notebook code differs from the prepared artifact.')
    counts=[c.get('execution_count') for c in cells]
    if counts!=list(range(1,len(cells)+1)): raise RuntimeError('Restart kernel, Run All, and save the notebook before packaging.')
    errors=[]; figures=0; text=''
    for c in cells:
        for output in c.get('outputs',[]):
            if output.get('output_type')=='error': errors.append(output.get('ename','unknown'))
            if 'application/vnd.plotly.v1+json' in output.get('data',{}): figures+=1
            payload=output.get('text',[])
            text+=''.join(payload) if isinstance(payload,list) else payload
    if errors or figures<expected['minimum_plotly_outputs'] or expected['completion_marker'] not in text:
        raise RuntimeError('Notebook outputs are incomplete, contain errors, or lack inline Plotly outputs.')
    return dict(code_cells=len(cells),plotly_outputs=figures,structural_execution_evidence=True,
                visual_reopening_confirmed_by_user='user must confirm separately')

def main():
    require_tests(ROOT)
    latest=json.loads((ROOT/'artifacts/m01_latest.json').read_text())
    run=ROOT/latest['run_directory']
    if run.resolve().parent!=(ROOT/'artifacts/m01').resolve(): raise RuntimeError('Unexpected run path.')
    cache=StageCache(run,latest['key'])
    for stage in ('schema','supervision','representation'):
        if not cache.reuse(stage): raise RuntimeError('A complete stage is missing.')
    if latest.get('status')!='complete' or not latest.get('raw_inputs_unchanged'):
        raise RuntimeError('Audit not complete.')
    pause=json.loads((ROOT/'artifacts/m01_pause_receipt.json').read_text())
    if pause['key']!=latest['key'] or latest['stages']['schema']!='reused_verified':
        raise RuntimeError('The controlled pause/resume demonstration was not recorded for this run.')
    # Verify raw hashes again without including any raw file in the package.
    context=json.loads((run/'context.json').read_text())
    for name,expected in context['data_sha256'].items():
        if sha256(ROOT/'data/raw/metadata'/name)!=expected: raise RuntimeError('Raw input changed since audit.')
    manifest=json.loads((ROOT/'ARTIFACT_MANIFEST.json').read_text())
    notebook_receipts={}
    files=[ROOT/'artifacts/preflight.json',ROOT/'artifacts/test_receipt.json',ROOT/'artifacts/tests.xml',
           ROOT/'logs/tests.log',ROOT/'artifacts/m01_latest.json',ROOT/'artifacts/m01_pause_receipt.json']
    for name,expected in manifest['notebooks'].items():
        p=ROOT/name; notebook_receipts[name]=notebook_evidence(p,expected); files.append(p)
    files.extend(run/name for name in AGGREGATES)
    if any(not p.is_file() or p.is_symlink() for p in files): raise RuntimeError('Missing/unsafe evidence file.')
    # context/manifests contain only hashes, versions, fixed settings and aggregate metadata.
    result=dict(utc=utc(),status='complete',notebooks=notebook_receipts,model_fits=0,official_score=None,
        excluded=['raw CSVs','DICOM images','report text','ID-bearing feature matrices','private CLI logs','credentials'],
        files={str(p.relative_to(ROOT)):sha256(p) for p in files},
        privacy_note='Review the archive locally before sharing; automated checks are not a complete privacy proof.')
    destination=ROOT/'returns/rsna-knee-m01-return.zip'; destination.parent.mkdir(exist_ok=True)
    pending=destination.with_suffix('.pending.zip')
    with zipfile.ZipFile(pending,'w',zipfile.ZIP_DEFLATED) as archive:
        for p in files: archive.write(p,str(p.relative_to(ROOT)))
        archive.writestr('RETURN_MANIFEST.json',json.dumps(result,indent=2))
    pending.replace(destination)
    atomic_json(ROOT/'returns/return_receipt.json',dict(utc=utc(),sha256=sha256(destination),bytes=destination.stat().st_size))
    print('Created returns/rsna-knee-m01-return.zip; nothing uploaded. Review before sharing.')
    print('Confirm manually that both saved notebooks reopen with visible inline figures.')

if __name__=='__main__':
    try: main()
    except Exception as exc:
        print(f'STOP: {exc}')
        raise SystemExit(1)
