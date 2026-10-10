import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EmployerPortfolioTests(unittest.TestCase):
    def test_required_employer_docs_exist(self):
        required = [
            "README.md",
            "docs/ARCHITECTURE.md",
            "docs/EMPLOYER_CASE_STUDY.md",
            "docs/RESEARCH_TIMELINE.md",
            "docs/EMPLOYER_REVIEW_GUIDE.md",
            "docs/REPRODUCIBILITY.md",
            "docs/PROJECT_CLOSEOUT.md",
            "docs/assets/portfolio-hero.svg",
            "docs/assets/architecture.svg",
            "examples/run_public_pipeline.py",
            "docs/CONTEXT_MODELING_FRONTIER.md",
            "docs/WINNER_TRANSFER_FRONTIER.md",
            "notebooks/14_winner_transfer_and_context_modeling.ipynb",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_readme_exposes_review_and_reproduction_paths(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for path in [
            "docs/EMPLOYER_REVIEW_GUIDE.md",
            "docs/EMPLOYER_CASE_STUDY.md",
            "docs/ARCHITECTURE.md",
            "docs/REPRODUCIBILITY.md",
            "docs/PROJECT_CLOSEOUT.md",
            "examples/run_public_pipeline.py",
            "requirements-review.lock",
        ]:
            self.assertIn(path, text)
            self.assertTrue((ROOT / path).is_file(), path)
        self.assertIn("0.943", text)
        self.assertIn("0.7978448", text)
        self.assertIn("SYNTHETIC_ONLY", text)

    def test_employer_review_links_resolve(self):
        for name in ('README.md', 'docs/EMPLOYER_REVIEW_GUIDE.md',
                     'docs/REPRODUCIBILITY.md', 'docs/PROJECT_CLOSEOUT.md',
                     'docs/ARCHITECTURE.md', 'docs/EMPLOYER_CASE_STUDY.md'):
            document = ROOT / name
            for destination in re.findall(r'\]\(([^\s)]+)\)', document.read_text()):
                if destination.startswith(('https://', 'http://', '#', 'mailto:')):
                    continue
                target = destination.split('#', 1)[0]
                self.assertTrue((document.parent / target).is_file(), f'{name}: {target}')

    def test_case_study_shows_ownership_and_outcomes(self):
        text = (ROOT / "docs/EMPLOYER_CASE_STUDY.md").read_text(encoding="utf-8")
        for phrase in [
            "Executive summary",
            "My ownership",
            "Core constraints",
            "Key decisions",
            "Engineering highlights",
            "Technical stack",
            "Outcomes",
            "What this demonstrates to an employer",
        ]:
            self.assertIn(phrase, text)

    def test_timeline_records_decisions(self):
        text = (ROOT / "docs/RESEARCH_TIMELINE.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("### Decision"), 8)
        self.assertIn("winner-technique audit", text.lower())
        self.assertIn("ordered cross-slice context", text.lower())

    def test_context_frontier_shows_gain_and_uncertainty(self):
        text = (ROOT / "docs/CONTEXT_MODELING_FRONTIER.md").read_text(encoding="utf-8")
        self.assertIn("0.7943834", text)
        self.assertIn("0.7978448", text)
        self.assertIn("0.7978946", text)
        self.assertIn("crossed zero", text.lower())

    def test_winner_frontier_has_inventory_and_coverage(self):
        text = (ROOT / "docs/WINNER_TRANSFER_FRONTIER.md").read_text(encoding="utf-8")
        for phrase in ["9 prior competitions", "15 independent", "37 normalized", "29 high-confidence"]:
            self.assertIn(phrase, text)

    def test_employer_docs_respect_publication_boundary(self):
        paths = [
            "README.md",
            "docs/EMPLOYER_CASE_STUDY.md",
            "docs/RESEARCH_TIMELINE.md",
            "docs/EMPLOYER_REVIEW_GUIDE.md",
            "docs/REPRODUCIBILITY.md",
            "docs/CONTEXT_MODELING_FRONTIER.md",
            "docs/WINNER_TRANSFER_FRONTIER.md",
        ]
        banned = [
            r"1\.2\.826\.0\.1\.3680043",
            r"AKIA[A-Z0-9]{16}",
            r"ASIA[A-Z0-9]{16}",
            r"gh[pousr]_[A-Za-z0-9]{20,}",
            r"X-Amz-(?:Signature|Credential)=",
            r"arn:aws:",
            r"/home/sagemaker-user/",
            "top " + "score",
            "trying to " + "beat",
            "beat the " + "top",
            "leader " + "snapshot",
            "public-score " + "gap",
        ]
        for rel in paths:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for pattern in banned:
                self.assertIsNone(re.search(pattern, text, re.IGNORECASE), f"{rel}: {pattern}")


if __name__ == "__main__":
    unittest.main()
