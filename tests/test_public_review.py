"""Public evidence and output contracts: reject stale, altered and inconsistent inputs."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from rsna_review.evidence import NOTEBOOK, NOTEBOOKS, REPORT, summary, verify_notebook


class PublicReviewTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / REPORT).read_text())
        self.notebook = json.loads((ROOT / NOTEBOOK).read_text())

    def test_saved_notebook_matches_evidence(self):
        self.assertEqual(verify_notebook(ROOT)['stage104_decision'], 'INCONCLUSIVE')

    def test_aggregate_mutations_rejected(self):
        mutations = [
            ('research_frontier', 'stage102_gain_vs_stage84', .1),
            ('research_frontier', 'stage104_highest_point_macro_auc', float('nan')),
            ('research_frontier', 'stage84_retained_macro_auc', True),
            ('aws_validation', 'fold_studies', [870] * 5),
            ('aws_validation', 'cross_fold_scanner_groups', 1),
            ('winner_technique_inventory', 'fully_implemented', 8.2),
            ('winner_technique_inventory', 'missing', 7),
            ('stage104_neighbor_context', 'delta_vs_matched_control', .01),
            ('stage104_neighbor_context', 'ci90_lower', .00001),
            ('public_score', 'internal_metrics_directly_comparable', True),
            ('publication_policy', 'model_weights_public', True),
        ]
        for section, key, value in mutations:
            with self.subTest(section=section, key=key):
                data = deepcopy(self.data)
                data[section][key] = value
                with self.assertRaises(ValueError):
                    summary(data)

    def test_historical_notebooks_match_saved_values(self):
        for number in ('12', '13'):
            with self.subTest(notebook=number):
                verify_notebook(ROOT, number=number)

    def test_historical_changed_chart_rejected(self):
        for number in ('12', '13'):
            with self.subTest(notebook=number), tempfile.TemporaryDirectory() as directory:
                notebook = json.loads((ROOT / NOTEBOOKS[number]).read_text())
                cell = next(c for c in notebook['cells'] if c['cell_type'] == 'code')
                output = next(o for o in cell['outputs'] if 'data' in o)
                output['data']['application/vnd.plotly.v1+json']['data'][0]['y'][0] = 999
                path = Path(directory) / 'historical.ipynb'
                path.write_text(json.dumps(notebook))
                with self.assertRaises(ValueError):
                    verify_notebook(ROOT, path, number)

    def test_stale_source_rejected(self):
        self.notebook['cells'][1]['source'] += ['\nprint("changed")']
        self.assert_invalid_notebook()

    def test_stale_input_rejected(self):
        self.notebook['metadata']['review_execution']['inputs_sha256'][REPORT] = '0' * 64
        self.assert_invalid_notebook()

    def test_wrong_chart_value_rejected(self):
        out = next(o for o in self.notebook['cells'][1]['outputs'] if 'data' in o)
        out['data']['application/vnd.plotly.v1+json']['data'][0]['y'][0] = .9
        self.assert_invalid_notebook()

    def test_missing_fallback_rejected(self):
        out = next(o for o in self.notebook['cells'][1]['outputs'] if 'data' in o)
        del out['data']['image/svg+xml']
        self.assert_invalid_notebook()

    def test_blank_fallback_rejected(self):
        out = next(o for o in self.notebook['cells'][1]['outputs'] if 'data' in o)
        out['data']['image/svg+xml'] = '<svg></svg>'
        self.assert_invalid_notebook()

    def test_incomplete_execution_rejected(self):
        self.notebook['cells'][1]['execution_count'] = None
        self.assert_invalid_notebook()

    def assert_invalid_notebook(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'review.ipynb'
            path.write_text(json.dumps(self.notebook))
            with self.assertRaises(ValueError):
                verify_notebook(ROOT, path)

    def test_optimized_verifier_rejects_stale_source(self):
        self.notebook['cells'][1]['source'] += ['\nprint("changed")']
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'review.ipynb'
            path.write_text(json.dumps(self.notebook))
            result = subprocess.run([sys.executable, '-O', str(ROOT / 'scripts/verify_review_notebook.py'), '--notebook', str(path)], capture_output=True, text=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Stale notebook code_sha256', result.stderr)

    def test_synthetic_example_uses_public_metric(self):
        spec = importlib.util.spec_from_file_location('public_demo', ROOT / 'examples/run_public_review.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        result = module.run_demo()
        self.assertEqual(result['macro_auc'], .75)
        self.assertEqual(result['invalid_inputs_rejected'], ['misordered', 'nonfinite'])
        self.assertEqual(result['positive_point_estimate_decision'], 'INCONCLUSIVE')
        self.assertEqual(result['evidence_type'], 'SYNTHETIC_ONLY')

    def test_demo_runs_from_unrelated_directory_optimized(self):
        with tempfile.TemporaryDirectory() as directory:
            result = subprocess.run([sys.executable, '-O', str(ROOT / 'examples/run_public_review.py')], cwd=directory, capture_output=True, text=True, check=True)
        self.assertEqual(json.loads(result.stdout)['macro_auc'], .75)


if __name__ == '__main__':
    unittest.main()
