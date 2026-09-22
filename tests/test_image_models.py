"""Public tests use synthetic inputs only; they do not rerun MRI experiments."""
import importlib.util
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('image_models', ROOT / 'src/rsna_research/image_models.py')
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ImageModelContractTests(unittest.TestCase):
    def test_auc_perfect(self): self.assertEqual(m.binary_auc([0, 1], [0.1, 0.9]), 1.0)
    def test_auc_reversed(self): self.assertEqual(m.binary_auc([0, 1], [0.9, 0.1]), 0.0)
    def test_auc_ties(self): self.assertEqual(m.binary_auc([0, 1], [0.5, 0.5]), 0.5)
    def test_auc_one_class(self): self.assertIsNone(m.binary_auc([1, 1], [0.1, 0.9]))
    def test_auc_alignment(self):
        with self.assertRaises(ValueError): m.binary_auc([1], [0.1, 0.9])
    def test_auc_invalid_label(self):
        with self.assertRaises(ValueError): m.binary_auc([2], [0.5])
    def test_probability_nonfinite(self):
        with self.assertRaises(ValueError): m.probabilities([math.nan])
    def test_probability_range(self):
        with self.assertRaises(ValueError): m.probabilities([1.1])
    def test_probability_empty(self):
        with self.assertRaises(ValueError): m.probabilities([])
    def test_brier(self): self.assertAlmostEqual(m.brier([0, 1], [0.1, 0.9]), 0.01)
    def test_blend(self): self.assertAlmostEqual(m.fixed_blend([0.8], [0.2])[0], 0.74)
    def test_blend_alignment(self):
        with self.assertRaises(ValueError): m.fixed_blend([0.1], [0.1, 0.2])
    def test_blend_weight(self):
        with self.assertRaises(ValueError): m.fixed_blend([0.1], [0.2], -0.1)
    def test_global_attention(self): self.assertEqual(m.attention_pool([[1, 3], [3, 5]], [0, 0]), [2, 4])
    def test_stable_attention(self): self.assertEqual(m.attention_pool([[1], [3]], [1000, 1000]), [2])
    def test_global_not_independent_microbatches(self):
        global_value = m.attention_pool([[0], [10]], [0, 3])[0]
        self.assertGreater(global_value, 9)
        self.assertNotAlmostEqual(global_value, 5)
    def test_ragged(self):
        with self.assertRaises(ValueError): m.attention_pool([[1], [1, 2]], [0, 0])
    def test_nonfinite_attention(self):
        with self.assertRaises(ValueError): m.attention_pool([[1]], [math.inf])
    def test_primary_failed(self): self.assertEqual(m.promotion(-0.0032600308641975717, -0.0071902767015902536, 12, 12), 'STOP_FIXED_BLEND_DIRECTION')
    def test_brier_cannot_rescue_auc(self): self.assertEqual(m.promotion(-0.01, -0.1, 12, 12), 'STOP_FIXED_BLEND_DIRECTION')
    def test_promotion_is_not_submission(self): self.assertEqual(m.promotion(0.003, 0.0, 12, 12), 'CANDIDATE_FOR_BROADER_VALIDATION')
    def test_insufficient_support(self): self.assertEqual(m.promotion(0.1, -0.1, 11, 12), 'INCONCLUSIVE_SUPPORT')
    def test_too_few_studies(self): self.assertEqual(m.promotion(0.1, -0.1, 12, 5), 'INCONCLUSIVE_SUPPORT')
    def test_small_effect(self): self.assertEqual(m.promotion(0.001, 0.0, 12, 12), 'INCONCLUSIVE_EFFECT')

if __name__ == '__main__': unittest.main()
