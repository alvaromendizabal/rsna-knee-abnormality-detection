"""The retained result must not turn an uncertain increment into a promotion."""
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
