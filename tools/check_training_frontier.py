#!/usr/bin/env python3
"""Audit the curated Stage-31/32 publication using aggregate evidence only."""
from pathlib import Path
import json
import math
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "reports/training_frontier/results.json").read_text())
N = json.loads((ROOT / "notebooks/07_deployment_and_training_frontier.ipynb").read_text())

assert D["leaderboard"]["reference_public_auc"] == 0.933
assert D["leaderboard"]["highest_returned_page_auc"] == 0.958
assert D["leaderboard"]["candidate_public_auc"] is None
assert math.isclose(D["leaderboard"]["dated_gap"], 0.025, abs_tol=1e-12)

T = D["training_data"]
assert T["cached_studies"] == 960 and T["train_studies"] == 4407
assert T["remaining_studies"] == 3447
assert math.isclose(T["coverage_fraction"], 960 / 4407, abs_tol=1e-15)
assert T["latest_full_data_training_performed"] is False

P = D["deployment"]
for key in ("dino", "raptor", "blend"):
    assert P["cpu_gpu_max_abs_diff"][key] <= P["parity_tolerances"][key]

assert D["stage32"]["gates_passed"] == 8
assert D["stage32"]["remote_writes"] == 0
assert D["stage32"]["training_fits"] == 0
assert D["next_gate"]["status"] == "PREPARED_NOT_YET_COMPLETED"

cells = [c for c in N["cells"] if c["cell_type"] == "code"]
assert [c.get("execution_count") for c in cells] == list(range(1, 7))
outputs = [o for c in cells for o in c.get("outputs", [])]
assert not any(o.get("output_type") == "error" for o in outputs)
plots = [o["data"] for o in outputs if "application/vnd.plotly.v1+json" in (o.get("data") or {})]
assert len(plots) == 3
assert all("image/svg+xml" in p for p in plots)
assert all(p["application/vnd.plotly.v1+json"]["layout"]["width"] >= 950 for p in plots)
assert any(
    "RSNA_TRAINING_FRONTIER_PUBLICATION_COMPLETE" in "".join(o.get("text", []))
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
    "TRAINING_FRONTIER_PUBLICATION_PASSED: aggregate score state, GPU parity, "
    "cache coverage, notebook outputs, privacy scan, 10 synthetic tests"
)
