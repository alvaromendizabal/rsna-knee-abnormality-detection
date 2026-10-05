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
            "notebooks/13_parent_reconstruction_and_anatomy_qualification.ipynb",
        ]
        for rel in required:
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_readme_has_fast_review_contract(self):
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for heading in [
            "## 30-second overview",
            "### What employers should notice",
            "## System architecture",
            "## Research decisions that matter",
            "### 2-minute recruiter review",
            "### 10-minute ML engineering review",
            "### 15-minute research review",
            "## Technical stack",
        ]:
            self.assertIn(heading, text)
        self.assertIn("flowchart LR", text)
        self.assertIn("0.943", text)

    def test_architecture_has_three_system_views(self):
        text = (ROOT / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("```mermaid"), 3)
        for phrase in [
            "model identity includes data identity",
            "Control plane",
            "Failure recovery",
            "Validation architecture",
            "Anatomy-aware extension",
            "Public/private architecture boundary",
        ]:
            self.assertIn(phrase.lower(), text.lower())

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

    def test_timeline_records_questions_evidence_decisions(self):
        text = (ROOT / "docs/RESEARCH_TIMELINE.md").read_text(encoding="utf-8")
        self.assertGreaterEqual(text.count("### Decision"), 5)
        self.assertIn("Current controlled research plan", text)
        self.assertIn("A0", text)
        self.assertIn("A4", text)

    def test_employer_docs_respect_publication_boundary(self):
        paths = [
            "README.md",
            "docs/ARCHITECTURE.md",
            "docs/EMPLOYER_CASE_STUDY.md",
            "docs/RESEARCH_TIMELINE.md",
            "docs/EMPLOYER_REVIEW_GUIDE.md",
        ]
        banned = [
            r"1\\.2\\.826\\.0\\.1\\.3680043",
            r"AKIA[A-Z0-9]{16}",
            r"ASIA[A-Z0-9]{16}",
            r"gh[pousr]_[A-Za-z0-9]{20,}",
            r"X-Amz-(?:Signature|Credential)=",
            r"arn:aws:",
            r"/home/sagemaker-user/",
            r"top score",
            r"trying to beat",
            r"beat the top",
            r"leader snapshot",
            r"public-score gap",
            r"0\\.961",
        ]
        for rel in paths:
            text = (ROOT / rel).read_text(encoding="utf-8")
            for pattern in banned:
                self.assertIsNone(re.search(pattern, text, re.IGNORECASE), f"{rel}: {pattern}")


if __name__ == "__main__":
    unittest.main()
