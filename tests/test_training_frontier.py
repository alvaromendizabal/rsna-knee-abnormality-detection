import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "training_frontier", ROOT / "src/rsna_research/training_frontier.py"
)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class TrainingFrontierTests(unittest.TestCase):
    def test_full_coverage(self):
        self.assertEqual(m.coverage_fraction(4407, 4407), 1.0)

    def test_bad_coverage(self):
        with self.assertRaises(ValueError):
            m.coverage_fraction(5, 4)

    def test_gap(self):
        self.assertAlmostEqual(m.leaderboard_gap(0.933, 0.958), 0.025)

    def test_bad_gap_input(self):
        with self.assertRaises(ValueError):
            m.leaderboard_gap(1.2, 0.9)

    def test_stage34_gain(self):
        self.assertAlmostEqual(
            m.score_delta(0.7637618665674922, 0.7602655715392667),
            0.0034962950282255,
        )

    def test_consistency_delta(self):
        self.assertLess(
            m.score_delta(0.7629688105245118, 0.7637618665674922),
            0.0,
        )

    def test_bad_score_delta(self):
        with self.assertRaises(ValueError):
            m.score_delta(-0.1, 0.5)

    def test_unscored(self):
        self.assertEqual(m.candidate_state(None, 0.933), "UNSCORED")

    def test_above(self):
        self.assertEqual(m.candidate_state(0.94, 0.933), "ABOVE_INCUMBENT")

    def test_stage36_below_incumbent(self):
        self.assertEqual(m.candidate_state(0.820, 0.933), "AT_OR_BELOW_INCUMBENT")


if __name__ == "__main__":
    unittest.main()
