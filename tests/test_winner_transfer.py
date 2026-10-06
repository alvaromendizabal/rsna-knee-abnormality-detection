import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class WinnerTransferTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads((ROOT / "reports/current_frontier/results.json").read_text())

    def test_inventory_exceeds_research_gate(self):
        inv = self.data["winner_technique_inventory"]
        self.assertGreaterEqual(inv["competitions_audited"], 8)
        self.assertGreaterEqual(inv["top_solution_lineages_audited"], 15)
        self.assertGreaterEqual(inv["technique_families_identified"], 30)

    def test_capability_counts_are_exact(self):
        inv = self.data["winner_technique_inventory"]
        counted = sum(
            inv[k]
            for k in ["fully_implemented", "partially_implemented", "missing", "blocked"]
        )
        self.assertEqual(counted, inv["high_confidence_transferable_mechanisms"])
        self.assertEqual(counted, 29)

    def test_stage102_is_material_research_gain(self):
        f = self.data["research_frontier"]
        self.assertGreater(f["stage102_ordered_context_macro_auc"], f["stage84_retained_macro_auc"])
        self.assertGreater(f["stage102_gain_vs_stage84"], 0.003)

    def test_stage104_not_overpromoted(self):
        f = self.data["research_frontier"]
        self.assertGreater(f["stage104_highest_point_macro_auc"], f["stage102_ordered_context_macro_auc"])
        self.assertLess(f["stage104_ci90_lower"], 0.0)
        self.assertGreater(f["stage104_ci90_upper"], 0.0)
        self.assertIn("INCONCLUSIVE", f["stage104_interpretation"])

    def test_public_private_boundary(self):
        policy = self.data["publication_policy"]
        for key in [
            "row_level_predictions_public",
            "model_weights_public",
            "raw_mri_public",
            "private_runner_code_public",
            "source_recovery_handles_public",
            "exact_competition_fusion_logic_public",
        ]:
            self.assertFalse(policy[key])


if __name__ == "__main__":
    unittest.main()
