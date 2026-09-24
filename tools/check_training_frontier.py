#!/usr/bin/env python3
"""Audit the curated full-data training-frontier publication using aggregate evidence only."""
from pathlib import Path
import json
import math
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "reports/training_frontier/results.json").read_text())
N = json.loads((ROOT / "notebooks/07_deployment_and_training_frontier.ipynb").read_text())

L = D["leaderboard"]
assert L["reference_public_auc"] == 0.933
assert L["highest_returned_page_auc"] == 0.958
assert L["stage36_public_auc"] == 0.820
assert L["stage36_status"] == "complete"
assert math.isclose(L["dated_gap"], 0.025, abs_tol=1e-12)

T = D["training_data"]
assert T["cached_studies"] == T["train_studies"] == 4407
assert T["remaining_studies"] == 0
assert T["completed_shards"] == T["planned_shards"] == 14
assert math.isclose(T["coverage_fraction"], 1.0, abs_tol=1e-15)
assert T["unexpected_decode_failures"] == 0
assert T["pixel_payload_transform_changed"] is False

G = D["grouped_validation"]
assert G["scanner_groups"] == 59
assert G["folds"] == 5
assert G["fold_studies"] == [870, 870, 870, 870, 869]
assert G["non_gold_rows"] == 4349
assert G["gold_audit_rows"] == 58
assert G["gold_optimizer_rows"] == 0
assert G["group_leakage"] is False

S = D["stage34"]
assert S["baseline_macro_auc"] > S["starting_macro_auc"]
assert S["consistency_macro_auc"] < S["baseline_macro_auc"]
assert S["decision"] == "STOP_SUPERVISION_CONSISTENCY"
assert S["gold_used_for_model_selection"] is False
assert S["gold_optimizer_rows"] == 0

P = D["deployment"]
assert P["strict_checkpoint_load"] is True
assert P["dynamic_test_rows"] is True
assert P["decode_failures"] == 0
assert P["submission_requests"] == 1

assert D["next_gate"]["status"] == "ACTIVE_RESEARCH_NOT_YET_PROMOTED"

cells = [c for c in N["cells"] if c["cell_type"] == "code"]
assert [c.get("execution_count") for c in cells] == list(range(1, 7))
outputs = [o for c in cells for o in c.get("outputs", [])]
assert not any(o.get("output_type") == "error" for o in outputs)
plots = [o["data"] for o in outputs if "application/vnd.plotly.v1+json" in (o.get("data") or {})]
assert len(plots) == 3
assert all("image/svg+xml" in p for p in plots)
assert all(p["application/vnd.plotly.v1+json"]["layout"]["width"] >= 950 for p in plots)
assert any(
    "RSNA_FULL_DATA_FRONTIER_PUBLICATION_COMPLETE" in "".join(o.get("text", []))
    for o in outputs
)

paths = [
    "README.md",
    "docs/PROJECT_STATUS.md",
    "docs/TRAINING_FRONTIER.md",
    "docs/IMAGE_MODELS.md",
    "docs/SOURCES.md",
    "reports/training_frontier/results.json",
    "notebooks/07_deployment_and_training_frontier.ipynb",
    "src/rsna_research/training_frontier.py",
    "tests/test_training_frontier.py",
]
for name in paths:
    text = (ROOT / name).read_text()
    for pattern in [
        r"1\.2\.826\.0\.1\.3680043",
        r"AKIA[A-Z0-9]{16}",
        r"ASIA[A-Z0-9]{16}",
        r"gh[pousr]_[A-Za-z0-9]{20,}",
        r"X-Amz-(?:Signature|Credential)=",
        r"arn:aws:",
        r"/home/sagemaker-user/",
    ]:
        assert not re.search(pattern, text), f"Private-content pattern in {name}"

subprocess.run(
    [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(ROOT / "tests"),
        "-p",
        "test_training_frontier.py",
    ],
    check=True,
)
print(
    "TRAINING_FRONTIER_PUBLICATION_PASSED: full cache, grouped folds, Stage-34 matched training, "
    "Stage-36 official score, notebook outputs, privacy scan, 10 synthetic tests"
)
