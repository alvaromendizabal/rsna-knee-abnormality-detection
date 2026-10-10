import unittest
import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.rsna_research.scored_reference_frontier import head_call_reduction, median_speed_ratio

class ScoredReferenceFrontierTests(unittest.TestCase):
    def test_head_call_reduction(self):
        self.assertEqual(head_call_reduction(20, 15), 0.25)
    def test_median_speed_ratio(self):
        b=[0.02673059500011732,0.026663292000193906,0.0265207500001452]
        c=[0.02350604199978079,0.020931547000145656,0.02078682299952561]
        self.assertAlmostEqual(median_speed_ratio(b,c), 1.2738328418825595, places=12)
    def test_invalid_inputs(self):
        with self.assertRaises(ValueError): head_call_reduction(0,0)
        with self.assertRaises(ValueError): median_speed_ratio([],[])

if __name__ == '__main__': unittest.main()
