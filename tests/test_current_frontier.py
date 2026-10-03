import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rsna_research.current_frontier import (
    aggregate_gain,
    parent_reconstruction_summary,
    retention_state,
    screening_state,
)


class CurrentFrontierTests(unittest.TestCase):
    def test_retained_positive_gain(self):
        gain = aggregate_gain(0.7943833865949643, 0.7936872288001792)
        self.assertAlmostEqual(gain, 0.0006961577947851, places=14)
        self.assertEqual(
            retention_state(
                candidate=0.7943833865949643,
                baseline=0.7936872288001792,
                valid=True,
            ),
            "RETAIN_POSITIVE",
        )

    def test_invalid_evidence_is_not_retained(self):
        self.assertEqual(
            retention_state(candidate=0.9, baseline=0.8, valid=False),
            "INVALID",
        )

    def test_negative_spatial_screen_closes(self):
        state = screening_state(
            macro_gain=-0.0008008280403827,
            fold_gains={"0": 0.0002088, "2": -0.0012338},
            bootstrap_positive_fraction=0.075,
        )
        self.assertEqual(state, "CLOSE")

    def test_parent_reconstruction_summary(self):
        d = parent_reconstruction_summary(
            native_members=20,
            native_windows=200,
            a5_folds=5,
            rad_layouts=3,
            recovered_asset_bytes=2967474476,
        )
        self.assertTrue(d["core_trained_branches_restored"])
        self.assertEqual(d["native_members"], 20)
        self.assertEqual(d["a5_folds"], 5)

    def test_report_contract(self):
        d = json.loads((ROOT / "reports/current_frontier/results.json").read_text())
        self.assertEqual(d["public_score"]["verified_official_score"], 0.943)
        self.assertEqual(
            d["public_score"]["metric"],
            "unweighted_macro_roc_auc_12_targets",
        )
        self.assertTrue(d["public_score"]["higher_is_better"])
        self.assertFalse(d["public_score"]["internal_metrics_directly_comparable"])
        self.assertEqual(
            d["retained_residual_evidence"]["status"],
            "RETAINED_POSITIVE_CHALLENGER",
        )
        self.assertEqual(
            d["stage80_fixed_spatial"]["status"],
            "SCIENTIFIC_NEGATIVE_SCREEN",
        )
        self.assertEqual(
            d["stage83_frozen_orthopedic_foundation"]["status"],
            "SCIENTIFIC_NEGATIVE_SCREEN",
        )
        self.assertEqual(d["parent_reconstruction"]["native_members_executed"], 20)
        self.assertEqual(d["parent_reconstruction"]["a5_folds_executed"], 5)
        self.assertEqual(d["parent_reconstruction"]["rad_layouts_executed"], 3)
        self.assertEqual(d["parent_reconstruction"]["raptor_checkpoints_recovered"], 3)
        self.assertFalse(d["parent_reconstruction"]["full_parent_parity_established"])
        self.assertEqual(d["stage91_recovery"]["orchestration_milestones_completed"], 11)
        self.assertFalse(d["stage91_recovery"]["raw_acquisition_access_complete"])
        self.assertTrue(d["publication_policy"]["aws_canonical"])
        self.assertFalse(d["publication_policy"]["model_weights_public"])


if __name__ == "__main__":
    unittest.main()
