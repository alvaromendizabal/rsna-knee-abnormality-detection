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
    def test_coverage(self):
        self.assertAlmostEqual(m.coverage_fraction(960, 4407), 960 / 4407)

    def test_bad_coverage(self):
        with self.assertRaises(ValueError):
            m.coverage_fraction(5, 4)

    def test_gap(self):
        self.assertAlmostEqual(m.leaderboard_gap(0.933, 0.958), 0.025)

    def test_bad_gap_input(self):
        with self.assertRaises(ValueError):
            m.leaderboard_gap(1.2, 0.9)

    def test_dino_parity_ratio(self):
        self.assertLess(m.parity_ratio(1.043081283569336e-6, 0.001), 0.002)

    def test_raptor_parity_ratio(self):
        self.assertLess(m.parity_ratio(5.960464477539062e-7, 0.0001), 0.01)

    def test_bad_tolerance(self):
        with self.assertRaises(ValueError):
            m.parity_ratio(0.0, 0.0)

    def test_pending(self):
        self.assertEqual(m.candidate_state(None, 0.933), "PENDING")

    def test_above(self):
        self.assertEqual(m.candidate_state(0.94, 0.933), "ABOVE_INCUMBENT")

    def test_at_or_below(self):
        self.assertEqual(m.candidate_state(0.90, 0.933), "AT_OR_BELOW_INCUMBENT")


if __name__ == "__main__":
    unittest.main()
