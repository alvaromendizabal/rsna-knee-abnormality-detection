#!/usr/bin/env python3
from pathlib import Path
import json
import math
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
D = json.loads((ROOT / "reports/current_frontier/results.json").read_text())

P = D["public_score"]
assert P["verified_official_score"] == 0.943
assert P["metric"] == "unweighted_macro_roc_auc_12_targets"
assert P["higher_is_better"] is True
assert P["internal_metrics_directly_comparable"] is False

A = D["aws_validation"]
assert A["canonical_cache_studies"] == 4407
assert A["grouped_non_gold_rows"] == 4349
assert A["gold_audit_rows"] == 58
assert A["gold_optimizer_rows"] == 0
assert A["scanner_groups"] == 59
assert A["cross_fold_scanner_groups"] == 0
assert A["fold_studies"] == [870, 870, 870, 870, 869]

R = D["retained_residual_evidence"]
assert R["status"] == "RETAINED_POSITIVE_CHALLENGER"
assert R["candidate_macro_auc"] > R["baseline_macro_auc"]
assert math.isclose(R["macro_gain"], 0.0006961577947851, abs_tol=1e-15)
assert R["public_score_comparable"] is False

S80 = D["stage80_fixed_spatial"]
assert S80["status"] == "SCIENTIFIC_NEGATIVE_SCREEN"
assert S80["decision"] == "CLOSE_TESTED_CONFIGURATION"
assert S80["macro_gain"] < 0

S83 = D["stage83_frozen_orthopedic_foundation"]
assert S83["status"] == "SCIENTIFIC_NEGATIVE_SCREEN"
assert S83["decision"] == "CLOSE_FROZEN_FEATURE_CONFIGURATION"
assert S83["macro_gain"] < 0

PR = D["parent_reconstruction"]
assert PR["native_members_executed"] == 20
assert PR["native_window_evaluations"] == 200
assert PR["a5_folds_executed"] == 5
assert PR["rad_layouts_executed"] == 3
assert PR["raptor_checkpoints_recovered"] == 3
assert PR["coat_families_with_principal_assets"] == 3
assert PR["private_assets_recovered_bytes"] == 2967474476
assert PR["full_parent_parity_established"] is False

S91 = D["stage91_recovery"]
assert S91["status"] == "BLOCKED_WITH_REUSABLE_RECOVERY"
assert S91["orchestration_milestones_completed"] == 11
assert S91["orchestration_milestones_total"] == 11
assert S91["new_private_objects"] == 160
assert S91["raw_acquisition_access_complete"] is False

assert D["publication_policy"]["aws_canonical"] is True
assert D["publication_policy"]["github_employer_facing"] is True
assert D["publication_policy"]["row_level_predictions_public"] is False
assert D["publication_policy"]["model_weights_public"] is False

nb = json.loads((ROOT / "notebooks/12_owned_residual_and_representation_frontier.ipynb").read_text())
code = [c for c in nb["cells"] if c["cell_type"] == "code"]
outs = [o for c in code for o in c.get("outputs", [])]
assert not any(o.get("output_type") == "error" for o in outs)
assert sum("application/vnd.plotly.v1+json" in (o.get("data") or {}) for o in outs) >= 2
assert sum("image/svg+xml" in (o.get("data") or {}) for o in outs) >= 2
assert nb["metadata"]["publication_boundary"] == "aggregate-public-safe-historical"

paths = [
    "README.md",
    "docs/PROJECT_STATUS.md",
    "docs/AWS_RESIDUAL_FRONTIER.md",
    "docs/PARENT_RECONSTRUCTION_FRONTIER.md",
    "docs/ANATOMY_AWARE_TRANSFER_PROGRAM.md",
    "reports/current_frontier/results.json",
    "notebooks/12_owned_residual_and_representation_frontier.ipynb",
]

private_patterns = [
    r"1\.2\.826\.0\.1\.3680043",
    r"AKIA[A-Z0-9]{16}",
    r"ASIA[A-Z0-9]{16}",
    r"gh[pousr]_[A-Za-z0-9]{20,}",
    r"X-Amz-(?:Signature|Credential)=",
    r"arn:aws:",
    r"/home/sagemaker-user/",
]
comparison_fragments = [
    "0." + "961",
    "leader" + "_snapshot",
    "leader" + " snapshot",
    "public-score " + "gap",
]

for name in paths:
    txt = (ROOT / name).read_text()
    for pattern in private_patterns:
        assert not re.search(pattern, txt), f"private-content pattern in {name}"
    lowered = txt.lower()
    for fragment in comparison_fragments:
        assert fragment.lower() not in lowered, f"external-comparison framing in {name}"

subprocess.run(
    [
        sys.executable,
        "-m",
        "unittest",
        "discover",
        "-s",
        str(ROOT / "tests"),
        "-p",
        "test_current_frontier.py",
    ],
    check=True,
)

print("CURRENT_FRONTIER_PUBLICATION_PASSED")
