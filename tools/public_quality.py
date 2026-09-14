#!/usr/bin/env python3
from __future__ import annotations
import ast, json, pathlib, re, sys
ROOT = pathlib.Path(__file__).resolve().parents[1]
for p in ROOT.rglob('*.py'):
    if '.git' not in p.parts:
        ast.parse(p.read_text(encoding='utf-8'), filename=str(p))
markers = {
    '01_metadata_and_representation_audit.ipynb': 'M01_METADATA_AUDIT_COMPLETE',
    '02_protocol_feature_investigation.ipynb': 'R01_FEATURE_INVESTIGATION_COMPLETE',
    '03_image_context_feature_investigation.ipynb': 'R02_IMAGE_PILOT_COMPLETE',
    '04_supervision_and_validation.ipynb': 'SUPERVISION_MILESTONE_COMPLETE',
    '05_multilingual_teacher_pilot.ipynb': 'TEACHER_PILOT_RECORDED',
}
for name, marker in markers.items():
    p = ROOT / 'notebooks' / name
    if not p.is_file():
        raise SystemExit(f'missing notebook: {name}')
    nb = json.loads(p.read_text(encoding='utf-8'))
    blob = json.dumps(nb, ensure_ascii=False)
    if marker not in blob:
        raise SystemExit(f'missing completion marker in {name}')
    plotly = png = 0
    for cell in nb.get('cells', []):
        for out in cell.get('outputs', []) or []:
            data = out.get('data') or {}
            plotly += int('application/vnd.plotly.v1+json' in data)
            png += int('image/png' in data)
    if plotly < 12 or png < 12:
        raise SystemExit(f'{name}: expected >=12 Plotly and >=12 PNG outputs; found {plotly}/{png}')
for bad in ['data', 'artifacts', 'logs', 'returns', '.venv']:
    if (ROOT / bad).exists():
        raise SystemExit(f'forbidden public path: {bad}')
print('PUBLIC_QUALITY_PASSED')
