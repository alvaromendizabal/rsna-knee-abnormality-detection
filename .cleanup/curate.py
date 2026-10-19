"""Retire unrelated experiments while preserving final MRI review contracts."""
from pathlib import Path
import ast,json,subprocess
R=Path.cwd()
subprocess.run(['git','diff','--exit-code','683c2188a0323b0d6655e627fc6668af0a4177d0','HEAD','--','.',':(exclude).github/workflows',':(exclude).cleanup',':(exclude)README.md',':(exclude)docs'],check=True)
def put(name,text):
 p=R/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text.rstrip()+'\n')
def selected(name,names,header):
 text=(R/name).read_text();lines=text.splitlines(keepends=True)
 return header+'\n\n'+'\n\n'.join(''.join(lines[min([n.lineno]+[x.lineno for x in n.decorator_list])-1:n.end_lineno]).rstrip() for n in ast.parse(text).body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names)+'\n'
pixels=selected('src/rsna_research/pixels.py',{'ordered_geometry','load_volume','normalize'},'''"""Public MRI ingestion: spatial ordering, bounded decoding and case-local normalization.
These primitives are not the private model or a handcrafted feature campaign.
No anatomical segmentation, quantitative T1/T2 or clinical validity is implied.
"""
from __future__ import annotations
from pathlib import Path
import numpy as np
from rsna_knee.schema import ContractError''')
current=selected('src/rsna_research/current_frontier.py',{'aggregate_gain','retention_state','paired_interval_state'},'''"""Finite, scope-preserving comparisons for retained grouped MRI evidence."""
from __future__ import annotations
from math import isfinite''')
image=selected('src/rsna_research/image_models.py',{'probabilities','binary_auc','brier','fixed_blend','attention_pool'},'''"""Numerical metric, fixed-blend and global-pooling contracts.
Global attention normalization covers all encoding microbatches.
These reference primitives are not the withheld MRI training recipe.
"""
from __future__ import annotations
import math
from typing import Sequence''')
runtime=selected('src/rsna_knee/runtime.py',{'utc','sha256','digest','atomic_json','current_rss_bytes','Progress','StageCache'},'''"""Atomic stage evidence and bounded memory telemetry for public integrity tests."""
from __future__ import annotations
import hashlib,json,os,tempfile,time
from pathlib import Path
from datetime import datetime,timezone
import psutil''')
nb=json.loads((R/'notebooks/14_winner_transfer_and_context_modeling.ipynb').read_text())
nb['cells']=[nb['cells'][i] for i in (0,1,4,5,6,7,8)]
nb['cells'][0]['source']=['# Cross-slice context evaluation\n','\n','Executed analysis of the original grouped development aggregates: a retained context improvement, exact fold population, and an inconclusive extension. This notebook regenerates the reported arithmetic and charts, not private MRI predictions.\n','\n','The external **0.943** record and the **4,349-study scanner-grouped** development results are separate evaluation settings. Neither establishes clinical validity. The original report remains unmodified.\n','\n','## Retained development comparison\n','The truncated axis makes small differences visible. A higher point estimate is not automatically a supported improvement.']
for c in nb['cells']:
 if c['cell_type']=='code':c['outputs']=[];c['execution_count']=None
nb['metadata'].pop('review_execution',None)
keep_knee={'__init__.py','schema.py','metrics.py','runtime.py','downloads.py'}
keep_research={'__init__.py','comparison.py','pixels.py','image_models.py','current_frontier.py'}
keep_scripts={'execute_review_notebook.py','verify_review_notebook.py'}
keep_tools={'check_publication_boundary.py','public_quality.py','test_public_demo.mjs'}
keep_tests={'conftest.py','test_schema_and_representations.py','test_runtime_memory.py','test_metrics_and_evidence.py','test_research_comparison.py','test_research_pixels.py','test_image_models.py','test_current_frontier.py','test_public_pipeline.py','test_probability_diagnostics.py','test_public_review.py','test_employer_portfolio.py','test_publication_boundary.py'}
keep_docs={'ARCHITECTURE.md','EMPLOYER_CASE_STUDY.md','EMPLOYER_REVIEW_GUIDE.md','REPRODUCIBILITY.md','GIT_PUBLICATION.md','PROJECT_CLOSEOUT.md','CONTEXT_MODELING_FRONTIER.md','SOURCES.md'}
removed=[]
for name in filter(None,subprocess.check_output(['git','ls-files','-z']).decode().split('\0')):
 p=Path(name);parts=p.parts
 retire=parts[0] in {'research','configs','notebooks'}
 retire |= name in {'PROJECT_STATUS.md','requirements-audit.txt','requirements-research.txt'}
 retire |= name.startswith('src/rsna_knee/') and p.name not in keep_knee
 retire |= name.startswith('src/rsna_research/') and p.name not in keep_research
 retire |= parts[0]=='scripts' and p.name not in keep_scripts
 retire |= parts[0]=='tools' and p.name not in keep_tools
 retire |= parts[0]=='tests' and p.name not in keep_tests
 retire |= parts[0]=='reports' and name!='reports/current_frontier/results.json'
 retire |= parts[0]=='docs' and len(parts)==2 and p.name not in keep_docs
 if retire and (R/name).is_file():(R/name).unlink();removed.append(name)
put('src/rsna_research/pixels.py',pixels)
put('src/rsna_research/current_frontier.py',current)
put('src/rsna_research/image_models.py',image)
put('src/rsna_knee/runtime.py',runtime)
put('notebooks/01_context_evaluation.ipynb',json.dumps(nb,indent=1,ensure_ascii=False))
p=R/'src/rsna_review/evidence.py';s=p.read_text().replace("NOTEBOOK = 'notebooks/14_winner_transfer_and_context_modeling.ipynb'","NOTEBOOK = 'notebooks/01_context_evaluation.ipynb'")
s='\n'.join(line for line in s.splitlines() if not line.startswith('NOTEBOOKS ='))+'\n'
s=s.replace("    w = data['winner_technique_inventory']\n",'')
a=s.index('    coverage = counts(');b=s.index("    require(data['public_score']",a);s=s[:a]+s[b:]
s=s.replace(", 'coverage': coverage",'')
a=s.index('def verify_historical(');b=s.index('def verify_notebook(',a);s=s[:a]+s[b:]
s=s.replace("def verify_notebook(root, path=None, number='14'):","def verify_notebook(root, path=None):").replace('root / NOTEBOOKS[number]','root / NOTEBOOK')
s=s.replace("    if number in ('12', '13'):\n        return verify_historical(n, expected, number)\n",'')
s=s.replace("len(code) == 4 and [c.get('execution_count') for c in code] == [1, 2, 3, 4]","len(code) == 3 and [c.get('execution_count') for c in code] == [1, 2, 3]")
s=s.replace('len(plots) == len(svgs) == 4','len(plots) == len(svgs) == 3').replace('Four Plotly and SVG charts required','Three Plotly and SVG charts required')
s=s.replace("plots[:3], [expected['scores'], expected['coverage'], expected['folds']]","plots[:2], [expected['scores'], expected['folds']]")
s=s.replace("['Stage 84', 'Stage 102', 'Stage 104'], ['Full', 'Partial', 'Missing', 'Blocked'],","['Stage 84', 'Stage 102', 'Stage 104'],")
s=s.replace("trace = plots[3]['data'][0]","trace = plots[2]['data'][0]");p.write_text(s)
p=R/'scripts/execute_review_notebook.py';s=p.read_text().replace('import NOTEBOOKS, fingerprints','import NOTEBOOK, fingerprints').replace("    parser.add_argument('--notebook', choices=('12', '13', '14'), default='14')\n",'').replace('ROOT / NOTEBOOKS[args.notebook]','ROOT / NOTEBOOK').replace('verify_notebook(ROOT, args.output, args.notebook)','verify_notebook(ROOT, args.output)');p.write_text(s)
p=R/'scripts/verify_review_notebook.py';s=p.read_text().replace("    parser.add_argument('--number', choices=('12', '13', '14'), default='14')\n",'').replace('verify_notebook(ROOT, args.notebook, args.number)','verify_notebook(ROOT, args.notebook)');p.write_text(s)
p=R/'tests/test_public_review.py';s=p.read_text().replace('NOTEBOOK, NOTEBOOKS, REPORT','NOTEBOOK, REPORT');a=s.index('    def test_historical_notebooks');b=s.index('    def test_stale_source',a);s=s[:a]+s[b:];s='\n'.join(x for x in s.splitlines() if "('winner_technique_inventory'" not in x)+'\n';p.write_text(s)
p=R/'tests/test_image_models.py';s=p.read_text();a=s.index('    def test_primary_failed');b=s.index("if __name__",a);p.write_text(s[:a]+'\n'+s[b:])
p=R/'tests/test_research_pixels.py';s=p.read_text().replace('ordered_geometry,normalize,image_features,glcm,pool2d,load_volume,FAMILIES','ordered_geometry,normalize,load_volume');a=s.index('def geometry():');b=s.index('def test_pinned_reader',a);s=s[:a]+s[b:];a=s.index("@pytest.mark.parametrize('seed'");b=s.index('def test_actual_synthetic_dicom',a);s=s[:a]+s[b:];s=s.replace('x,_=normalize(v); f,r=image_features(x,g)\n    assert len(f)==140 and g[\'slice_count\']==8',"x,_=normalize(v)\n    assert x.shape==(8,16,16) and g['slice_count']==8");p.write_text(s)
p=R/'tests/test_schema_and_representations.py';s=p.read_text();a=s.index('def test_fluid_and_fat');b=s.index('def test_example_overlap',a);s=s[:a]+s[b:];s='\n'.join(x for x in s.splitlines() if not x.startswith(('import numpy','import pandas','from rsna_knee.representations')))+'\n';p.write_text(s)
put('tests/test_current_frontier.py','''"""The retained result must not turn an uncertain increment into a promotion."""
import importlib.util
import math
from pathlib import Path
import unittest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('comparison_rules',ROOT/'src/rsna_research/current_frontier.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class RetainedEvidenceTests(unittest.TestCase):
    def test_ordered_context_gain(self):
        self.assertAlmostEqual(m.aggregate_gain(.7978447501637148,.7943833865949643),.0034613635687505,places=14)
    def test_interval_not_point_estimate_controls_support(self):
        self.assertEqual(m.paired_interval_state(lower=-.0001735904,upper=.0002000818,delta=.0000498760527818),'INCONCLUSIVE')
    def test_invalid_evidence_rejected(self):
        for bad in (math.nan,math.inf,-.1,1.1):
            with self.subTest(value=bad), self.assertRaises(ValueError):m.aggregate_gain(bad,.8)
        with self.assertRaises(ValueError):m.paired_interval_state(lower=1,upper=0,delta=.1)
    def test_negative_result_is_preserved(self):
        self.assertEqual(m.retention_state(candidate=.7,baseline=.8),'SCIENTIFIC_NEGATIVE')
        self.assertEqual(m.retention_state(candidate=.9,baseline=.8,valid=False),'INVALID')
    def test_supported_interval_signs(self):
        self.assertEqual(m.paired_interval_state(lower=.001,upper=.003,delta=.002),'POSITIVE_SUPPORTED')
        self.assertEqual(m.paired_interval_state(lower=-.003,upper=-.001,delta=-.002),'NEGATIVE_SUPPORTED')
if __name__=='__main__':unittest.main()
''')
p=R/'tools/check_publication_boundary.py';s=p.read_text();n=next(x for x in ast.parse(s).body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='AUDITED_ASSETS' for t in x.targets));lines=s.splitlines(keepends=True);s=''.join(lines[:n.lineno-1])+"AUDITED_ASSETS = {}  # No vendored experiment plots require binary exceptions.\n"+''.join(lines[n.end_lineno:]);p.write_text(s)
p=R/'tests/test_publication_boundary.py';s=p.read_text();a=s.index('    def test_existing_asset_allowance');b=s.index('    def test_cli_reports',a);s=s[:a]+'''    def test_asset_allowance_requires_exact_path_and_bytes(self):
        from unittest.mock import patch
        raw = b'\\x89PNG\\x00inert-generated-test-fixture'
        name = 'assets/fixture.png'
        pin = {'bytes': len(raw), 'sha256': hashlib.sha256(raw).hexdigest()}
        with patch.dict(guard.AUDITED_ASSETS, {name: pin}, clear=True):
            self.assertEqual(guard.inspect_bytes(name, raw), [])
            self.assertEqual(guard.inspect_bytes(name, raw + b'changed'), ['AUDITED_ASSET_CHANGED'])
            self.assertTrue(guard.inspect_bytes('elsewhere/fixture.png', raw))

'''+s[b:];p.write_text(s)
put('tools/public_quality.py','''#!/usr/bin/env python3
"""Verify maintained source and final aggregate review without private inputs."""
from __future__ import annotations
import ast
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from rsna_review.evidence import verify_notebook

def main():
    names=subprocess.check_output(['git','-C',str(ROOT),'ls-files','--cached','--others','--exclude-standard','-z']).decode().split('\\0')
    checked=0
    for name in set(filter(None,names)):
        p=ROOT/name
        if p.is_file() and p.suffix=='.py':
            ast.parse(p.read_text(encoding='utf-8'),filename=name);checked+=1
    verify_notebook(ROOT)
    for name in ('test_image_models.py','test_current_frontier.py','test_employer_portfolio.py'):
        subprocess.run([sys.executable,'-S','-m','unittest','discover','-s','tests','-p',name,'-q'],cwd=ROOT,check=True,timeout=60)
    print('PUBLIC_QUALITY_PASSED',checked,'Python sources; final evidence and numerical contracts')
if __name__=='__main__':main()
''')
p=R/'docs/EMPLOYER_CASE_STUDY.md';s=p.read_text().replace('../notebooks/14_winner_transfer_and_context_modeling.ipynb','../notebooks/01_context_evaluation.ipynb');s='\n'.join(x for x in s.splitlines() if not any(b in x for b in ['RESEARCH_TIMELINE.md','WINNER_TRANSFER_FRONTIER.md','SCORED_REFERENCE_FRONTIER.md','ANATOMY_QUALIFICATION_FRONTIER.md','reports/figures']))+'\n';s='\n'.join(x for x in s.splitlines() if not (x.startswith('| Stop fixed spatial') or x.startswith('The anatomy route')))+'\n';s=s.replace('[Notebook 14]','[Final context analysis]').replace('replay three aggregate notebooks','replay the final aggregate notebook').replace('and anatomy-transfer studies','and cross-slice context');p.write_text(s)
p=R/'docs/GIT_PUBLICATION.md';s=p.read_text().replace('notebooks/14_winner_transfer_and_context_modeling.ipynb','notebooks/01_context_evaluation.ipynb').replace('python tools/check_current_frontier.py\n','').replace('affected Notebooks 12–14','final context-evaluation notebook');p.write_text(s)
p=R/'docs/CONTEXT_MODELING_FRONTIER.md';s=p.read_text().replace('- move to a materially different ranked capability.','- preserve the uncertainty as part of the final evaluation record.');p.write_text(s)
p=R/'docs/SOURCES.md';s=p.read_text();s='\n'.join(x for x in s.splitlines() if not (x.startswith('| S9 ') or x.startswith('| S10 ') or x.startswith('Earlier supervision') or x.startswith('No public source is used')))+'\n';s=s.replace('Sources support research hypotheses and attribution','Sources document the recorded model lineage and public numerical/data contracts').replace('**our hypotheses** — recorded in notebooks/docs;','**public reference controls** — clearly separated from the private model;');p.write_text(s)
p=R/'tests/test_employer_portfolio.py';s=p.read_text().replace('notebooks/14_winner_transfer_and_context_modeling.ipynb','notebooks/01_context_evaluation.ipynb');s='\n'.join(x for x in s.splitlines() if not ('"docs/RESEARCH_TIMELINE.md",' in x or '"docs/WINNER_TRANSFER_FRONTIER.md",' in x))+'\n';a=s.index('    def test_timeline_records');b=s.index('    def test_context_frontier',a);s=s[:a]+s[b:];a=s.index('    def test_winner_frontier');b=s.index('    def test_employer_docs_respect',a);s=s[:a]+s[b:];p.write_text(s)
p=R/'review/project.json';d=json.loads(p.read_text());d['source_files']=['review/run.py','src/rsna_review/evidence.py','notebooks/01_context_evaluation.ipynb'];d['cards'][0]['implementation']='src/rsna_review/public_pipeline.py';d['cards'][0]['tests']='tests/test_public_pipeline.py';d['cards'][1].update(title='Preserve global pooling across microbatches.',decision='Normalize attention over all encoded windows; independent chunk softmax is not equivalent.',boundary='These are numerical reference contracts, not the private MRI model recipe.');d['summary']='A twelve-label MRI project with scanner-grouped evidence, ordered context, validated data and numerical contracts, and recoverable training. Public controls are fitted on authored data and clearly separated from the private model.';p.write_text(json.dumps(d,indent=2)+'\n')
for p in [R/'README.md',*(R/'docs').glob('*.md')]:p.write_text(p.read_text().rstrip()+'\n')
print('Retired',len(removed),'tracked paths; original final aggregate report unchanged')
