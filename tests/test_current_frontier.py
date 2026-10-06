import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.rsna_research.current_frontier import (
    aggregate_gain,
    paired_interval_state,
    parent_reconstruction_summary,
    retention_state,
    screening_state,
    winner_transfer_coverage,
)


class CurrentFrontierTests(unittest.TestCase):
    def test_stage102_full_cohort_gain(self):
        gain = aggregate_gain(0.7978447501637148, 0.7943833865949643)
        self.assertAlmostEqual(gain, 0.0034613635687505, places=14)
        self.assertEqual(
            retention_state(
                candidate=0.7978447501637148,
                baseline=0.7943833865949643,
                valid=True,
            ),
            "RETAIN_POSITIVE",
        )

    def test_stage104_increment_is_inconclusive(self):
        self.assertAlmostEqual(
            aggregate_gain(0.7978946262164966, 0.7978447501637148),
            0.0000498760527818,
            places=14,
        )
        self.assertEqual(
            paired_interval_state(
                lower=-0.0001735904,
                upper=0.0002000818,
                delta=0.0000498760527818,
            ),
            "INCONCLUSIVE",
        )

    def test_negative_spatial_screen_closes(self):
        state = screening_state(
            macro_gain=-0.0008008280403827,
            fold_gains={"0": 0.0002088, "2": -0.0012338},
            bootstrap_positive_fraction=0.075,
        )
        self.assertEqual(state, "CLOSE")

    def test_winner_transfer_coverage(self):
        d = winner_transfer_coverage(
            fully_implemented=8,
            partially_implemented=11,
            missing=6,
            blocked=4,
        )
        self.assertEqual(d["total"], 29)
        self.assertAlmostEqual(d["full_coverage_fraction"], 8 / 29)

    def test_parent_reconstruction_summary(self):
        d = parent_reconstruction_summary(
            native_members=20,
            native_windows=200,
            a5_folds=5,
            rad_layouts=3,
            recovered_asset_bytes=2967474476,
        )
        self.assertTrue(d["core_trained_branches_restored"])

    def test_report_contract(self):
        d = json.loads((ROOT / "reports/current_frontier/results.json").read_text())
        self.assertEqual(d["public_score"]["verified_official_score"], 0.943)
        self.assertFalse(d["public_score"]["internal_metrics_directly_comparable"])

        f = d["research_frontier"]
        self.assertAlmostEqual(f["stage102_ordered_context_macro_auc"], 0.7978447501637148)
        self.assertAlmostEqual(f["stage104_highest_point_macro_auc"], 0.7978946262164966)
        self.assertEqual(f["stage104_interpretation"], "RETAIN_POINT_ESTIMATE_INCONCLUSIVE")
        self.assertFalse(f["public_score_comparable"])

        inv = d["winner_technique_inventory"]
        self.assertEqual(inv["competitions_audited"], 9)
        self.assertEqual(inv["top_solution_lineages_audited"], 15)
        self.assertEqual(inv["technique_families_identified"], 37)
        self.assertEqual(inv["high_confidence_transferable_mechanisms"], 29)

        anatomy = d["anatomy_program"]
        self.assertTrue(anatomy["reference_gate_passed"])
        self.assertGreater(anatomy["reference_mean_dice"], 0.90)

        s103 = d["stage103_integration"]
        self.assertEqual(s103["tracks_completed"], 14)
        self.assertTrue(s103["full_cohort_export_parity_passed"])

        s104 = d["stage104_neighbor_context"]
        self.assertEqual(s104["status"], "SUCCESS_INCONCLUSIVE_HYPOTHESIS")
        self.assertEqual(s104["tracks_completed"], 14)
        self.assertEqual(s104["decision"], "PRESERVE_POINT_ESTIMATE_CLOSE_MICROTUNING")

        self.assertTrue(d["publication_policy"]["aws_canonical"])
        self.assertFalse(d["publication_policy"]["model_weights_public"])
        self.assertFalse(d["publication_policy"]["exact_competition_fusion_logic_public"])


if __name__ == "__main__":
    unittest.main()
