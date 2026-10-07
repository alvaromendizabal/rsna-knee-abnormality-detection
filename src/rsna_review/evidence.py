"""Recompute displayed aggregates and verify notebook provenance without private data."""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

NOTEBOOK = 'notebooks/14_winner_transfer_and_context_modeling.ipynb'
NOTEBOOKS = {'12': 'notebooks/12_owned_residual_and_representation_frontier.ipynb', '13': 'notebooks/13_parent_reconstruction_and_anatomy_qualification.ipynb', '14': NOTEBOOK}
REPORT = 'reports/current_frontier/results.json'
INPUTS = (REPORT, 'src/rsna_review/evidence.py')


def require(condition, message):
    if not condition:
        raise ValueError(message)


def finite(value, name):
    require(type(value) in (int, float) and math.isfinite(value), f'{name}: finite number required')
    return value


def counts(values, name):
    require(all(type(v) is int and v >= 0 for v in values), f'{name}: nonnegative integer required')
    return values


def summary(data):
    f = data['research_frontier']
    a = data['aws_validation']
    w = data['winner_technique_inventory']
    s = data['stage104_neighbor_context']
    scores = [f[k] for k in ('stage84_retained_macro_auc', 'stage102_ordered_context_macro_auc', 'stage104_highest_point_macro_auc')]
    require(all(0 <= finite(x, 'AUC') <= 1 for x in scores), 'AUC outside [0, 1]')
    gain = scores[1] - scores[0]
    require(math.isclose(gain, finite(f['stage102_gain_vs_stage84'], 'gain'), abs_tol=1e-14), 'Stage 102 gain mismatch')
    delta = finite(s['neighbor_context_macro_auc'], 'neighbor') - finite(s['matched_control_macro_auc'], 'control')
    require(math.isclose(scores[2], s['neighbor_context_macro_auc'], abs_tol=1e-14), 'Stage 104 score mismatch')
    require(math.isclose(delta, finite(s['delta_vs_matched_control'], 'matched delta'), abs_tol=1e-14), 'Matched delta mismatch')
    require(math.isclose(scores[2] - scores[1], finite(s['delta_vs_stage102'], 'reference delta'), abs_tol=1e-14), 'Reference delta mismatch')
    lower, upper = finite(s['ci90_lower'], 'CI lower'), finite(s['ci90_upper'], 'CI upper')
    require(lower < 0 < upper, 'Published Stage 104 interval must remain inconclusive')
    require(f['stage104_interpretation'] == 'RETAIN_POINT_ESTIMATE_INCONCLUSIVE', 'Inconclusive interpretation changed')
    folds = counts(a['fold_studies'], 'folds')
    require(len(folds) == 5 and sum(folds) == a['grouped_non_gold_rows'], 'Fold population mismatch')
    require(a['cross_fold_scanner_groups'] == 0, 'Scanner overlap detected')
    coverage = counts([w[k] for k in ('fully_implemented', 'partially_implemented', 'missing', 'blocked')], 'coverage')
    require(sum(coverage) == w['high_confidence_transferable_mechanisms'], 'Coverage mismatch')
    require(data['public_score']['internal_metrics_directly_comparable'] is False, 'External and development scores must be separate')
    for key in ('row_level_predictions_public', 'model_weights_public', 'raw_mri_public', 'private_runner_code_public', 'exact_competition_fusion_logic_public'):
        require(data['publication_policy'][key] is False, f'Private boundary changed: {key}')
    return {'as_of_utc': data['as_of_utc'], 'scores': scores, 'stage102_gain': gain, 'coverage': coverage,
            'folds': folds, 'matched_delta': delta, 'reference_delta': scores[2] - scores[1], 'ci90': [lower, upper], 'stage104_decision': 'INCONCLUSIVE'}


def fingerprints(root, notebook):
    code = [''.join(c['source']) for c in notebook['cells'] if c['cell_type'] == 'code']
    return {'code_sha256': hashlib.sha256(json.dumps(code, ensure_ascii=False).encode()).hexdigest(),
            'inputs_sha256': {p: hashlib.sha256((root / p).read_bytes()).hexdigest() for p in INPUTS}}


def verify_historical(notebook, expected, number):
    code = [c for c in notebook['cells'] if c['cell_type'] == 'code']
    require(len(code) == 2 and [c.get('execution_count') for c in code] == [1, 2], 'Incomplete historical notebook execution')
    outputs = [o for c in code for o in c.get('outputs', [])]
    require(not any(o['output_type'] == 'error' for o in outputs), 'Historical notebook error')
    plots = [o['data']['application/vnd.plotly.v1+json'] for o in outputs if 'application/vnd.plotly.v1+json' in o.get('data', {})]
    svgs = [o['data']['image/svg+xml'] for o in outputs if 'image/svg+xml' in o.get('data', {})]
    require(len(plots) == len(svgs) == 2 and all('<svg' in ''.join(x) and '<path' in ''.join(x) and len(''.join(x)) > 1500 for x in svgs), 'Two saved Plotly and SVG charts required')
    if number == '12':
        charts = [(['Baseline', 'Retained residual'], [.7912075114786626, .7936862526975088]),
                  (['Fold 0', 'Fold 2', 'Macro'], [.0002088, -.0012338, -.0008008280403827])]
    else:
        charts = [(['E87A', 'E87B', 'E87C', 'ANATOMY_PILOT', 'E87F', 'E87E'], [89, 87, 81, 80, 77, 71]),
                  (['Native members', 'A5 folds', 'Raptor views', 'CoAt predictions', 'Audit units', 'Anatomy tracks'], [20, 5, 4, 7, 7, 4])]
    for plot, (labels, values) in zip(plots, charts, strict=True):
        trace = plot['data'][0]
        require(trace['x'] == labels and trace['y'] == values, 'Historical chart differs from published source values')
    return expected


def verify_notebook(root, path=None, number='14'):
    root = Path(root)
    n = json.loads((Path(path) if path else root / NOTEBOOKS[number]).read_text())
    expected = summary(json.loads((root / REPORT).read_text()))
    provenance = n['metadata'].get('review_execution', {})
    require(provenance.get('engine') in ('jupyter', 'ipython-inprocess'), 'Missing real execution provenance')
    for key, value in fingerprints(root, n).items():
        require(provenance.get(key) == value, f'Stale notebook {key}')
    if number in ('12', '13'):
        return verify_historical(n, expected, number)
    code = [c for c in n['cells'] if c['cell_type'] == 'code']
    require(len(code) == 4 and [c.get('execution_count') for c in code] == [1, 2, 3, 4], 'Incomplete notebook execution')
    outputs = [o for c in code for o in c.get('outputs', [])]
    require(not any(o['output_type'] == 'error' for o in outputs), 'Notebook contains error output')
    plots = [o['data']['application/vnd.plotly.v1+json'] for o in outputs if 'application/vnd.plotly.v1+json' in o.get('data', {})]
    svgs = [o['data']['image/svg+xml'] for o in outputs if 'image/svg+xml' in o.get('data', {})]
    require(len(plots) == len(svgs) == 4 and all('<svg' in ''.join(x) and '<path' in ''.join(x) and len(''.join(x)) > 1500 for x in svgs), 'Four Plotly and SVG charts required')
    for plot, values, labels in zip(plots[:3], [expected['scores'], expected['coverage'], expected['folds']],
        [['Stage 84', 'Stage 102', 'Stage 104'], ['Full', 'Partial', 'Missing', 'Blocked'], ['Fold 0', 'Fold 1', 'Fold 2', 'Fold 3', 'Fold 4']], strict=True):
        require(len(plot['data']) == 1 and plot['data'][0]['y'] == values and plot['data'][0]['x'] == labels, 'Chart differs from source evidence')
    trace = plots[3]['data'][0]
    require(trace['x'] == [expected['reference_delta']], 'Wrong Stage 104 comparator')
    require(trace['error_x']['array'] == [expected['ci90'][1] - expected['reference_delta']], 'Upper interval mismatch')
    require(trace['error_x']['arrayminus'] == [expected['reference_delta'] - expected['ci90'][0]], 'Lower interval mismatch')
    streams = ''.join(''.join(o.get('text', '')) for o in outputs if o['output_type'] == 'stream')
    marker = 'REVIEW_SUMMARY '
    lines = [line.removeprefix(marker) for line in streams.splitlines() if line.startswith(marker)]
    require(len(lines) == 1 and json.loads(lines[0]) == expected, 'Saved summary differs from evidence')
    require('M14_PUBLICATION_COMPLETE' in streams, 'Completion marker missing')
    return expected
