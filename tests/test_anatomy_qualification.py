import unittest

from src.rsna_research.anatomy_qualification import (
    exact_fallback_unchanged,
    qualification_state,
    reference_quality_gate,
)


class AnatomyQualificationTests(unittest.TestCase):
    def test_reference_gate_passes_at_frozen_thresholds(self):
        scores = {f"label_{i}": 0.90 for i in range(9)}
        result = reference_quality_gate(scores)
        self.assertTrue(result["passed"])
        self.assertEqual(result["label_count"], 9)
        self.assertAlmostEqual(result["mean_dice"], 0.90)

    def test_reference_gate_rejects_one_weak_structure(self):
        scores = {f"label_{i}": 0.95 for i in range(9)}
        scores["label_8"] = 0.49
        result = reference_quality_gate(scores)
        self.assertFalse(result["passed"])
        self.assertEqual(result["min_dice"], 0.49)

    def test_reference_gate_requires_complete_label_set(self):
        with self.assertRaises(ValueError):
            reference_quality_gate({"only_one": 0.9})

    def test_reference_gate_rejects_invalid_dice(self):
        scores = {f"label_{i}": 0.90 for i in range(9)}
        scores["label_0"] = 1.01
        with self.assertRaises(ValueError):
            reference_quality_gate(scores)

    def test_exact_parent_fallback(self):
        parent = [0.0, 0.2, 0.5, 1.0]
        self.assertTrue(exact_fallback_unchanged(parent, list(parent)))
        self.assertFalse(exact_fallback_unchanged(parent, [0.0, 0.2, 0.5000001, 1.0]))

    def test_qualification_lifecycle(self):
        self.assertEqual(
            qualification_state(
                tracks_completed=3,
                tracks_total=4,
                real_inference_completed=False,
            ),
            "QUALIFICATION_INCOMPLETE",
        )
        self.assertEqual(
            qualification_state(
                tracks_completed=4,
                tracks_total=4,
                real_inference_completed=False,
            ),
            "QUALIFIED_FOR_REFERENCE_PILOT",
        )
        self.assertEqual(
            qualification_state(
                tracks_completed=4,
                tracks_total=4,
                real_inference_completed=True,
                reference_gate_passed=True,
            ),
            "REFERENCE_GATE_PASSED",
        )
        self.assertEqual(
            qualification_state(
                tracks_completed=4,
                tracks_total=4,
                real_inference_completed=True,
                reference_gate_passed=False,
            ),
            "REFERENCE_GATE_REJECTED",
        )


if __name__ == "__main__":
    unittest.main()
