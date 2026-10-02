import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))

from src.rsna_research.current_frontier import (
    aggregate_gain,
    promoted_residual_summary,
    public_score_gap,
    screening_state,
)

class CurrentFrontierTests(unittest.TestCase):
    def test_public_gap(self):
        self.assertEqual(public_score_gap(0.943,0.961),0.018)

    def test_promoted_residual_gain(self):
        self.assertAlmostEqual(
            aggregate_gain(0.7936862526975088,0.7912075114786626),
            0.00247874121884617,
            places=14,
        )

    def test_promoted_residual_summary(self):
        d=promoted_residual_summary(
            baseline=0.7912075114786626,
            candidate=0.7936862526975088,
            all_folds_positive=True,
            protected_target_count=10,
        )
        self.assertTrue(d["promoted"])
        self.assertEqual(d["protected_target_count"],10)

    def test_stage80_closes(self):
        state=screening_state(
            macro_gain=-0.0008008280403827,
            fold_gains={"0":0.0002088,"2":-0.0012338},
            bootstrap_positive_fraction=0.075,
        )
        self.assertEqual(state,"CLOSE")

    def test_report_contract(self):
        d=json.loads((ROOT/"reports/current_frontier/results.json").read_text())
        self.assertEqual(d["public_score"]["current_official_best"],0.943)
        self.assertFalse(d["public_score"]["internal_metrics_directly_comparable"])
        self.assertEqual(d["promoted_target_residual"]["status"],"PROMOTED")
        self.assertTrue(d["promoted_target_residual"]["all_folds_positive"])
        self.assertEqual(d["stage80_dense_anatomy"]["decision"],"CLOSE_AT_SCREEN")
        self.assertEqual(d["stage81"]["status"],"PREPARED_NOT_EXECUTED")
        self.assertFalse(d["stage81"]["accuracy_claimed"])

if __name__=="__main__":
    unittest.main()
