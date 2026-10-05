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
assert A["fully_labeled_audit_rows"] == 58
assert A["audit_optimizer_rows"] == 0
assert A["fully_labeled_rows_outside_recovered_selection_lineage"] == 0
assert A["scanner_groups"] == 59
assert A["cross_fold_scanner_groups"] == 0
assert A["fold_studies"] == [870, 870, 870, 870, 869]

R = D["retained_residual_evidence"]
assert R["status"] == "RETAINED_POSITIVE_CHALLENGER"
assert R["candidate_macro_auc"] > R["baseline_macro_auc"]
assert math.isclose(R["macro_gain"], 0.0006961577947851, abs_tol=1e-15)
assert R["public_score_comparable"] is False

assert D["stage80_fixed_spatial"]["decision"] == "CLOSE_TESTED_CONFIGURATION"
assert D["stage83_frozen_orthopedic_foundation"]["decision"] == "CLOSE_FROZEN_FEATURE_CONFIGURATION"

PR = D["parent_reconstruction"]
assert PR["native_members_executed"] == 20
assert PR["native_window_evaluations"] == 200
assert PR["a5_folds_executed"] == 5
assert PR["rad_layouts_executed"] == 3
assert PR["raptor_diagnostic_views_completed"] == 4
assert PR["coat_source_checkpoint_gates_completed"] == 8
assert PR["coat_trained_predictions_completed"] == 7
assert PR["joint_diagnostic_bank_created"] is True
assert PR["complete_input_views"] == 0
assert PR["full_parent_parity_established"] is False

S93 = D["stage93_validation_acquisition_audit"]
assert S93["status"] == "SUCCESS"
assert S93["units_completed"] == S93["units_total"] == 7
assert S93["present_series"] == 77
assert S93["declared_series"] == 152
assert S93["absent_series"] == 75
assert S93["untouched_fully_labeled_studies"] == 0

S94 = D["stage94_source_recovery"]
assert S94["status"] == "BLOCKED_RESOURCE_AUTHORIZATION"
assert S94["raw_files_downloaded"] == 0
assert S94["automatic_bypass_attempted"] is False

S95 = D["stage95_geometry_audit"]
assert S95["status"] == "SUCCESS_NEGATIVE_HYPOTHESIS"
assert S95["headers_inspected"] == 2287
assert S95["geometry_flags"] == 0
assert S95["unevaluable_series"] == 0

S96 = D["stage96_anatomy_qualification"]
assert S96["status"] == "SUCCESS"
assert S96["tracks_completed"] == S96["tracks_total"] == 4
assert S96["foreground_anatomy_labels"] == 9
assert S96["coordinate_adapters_validated"] == 3
assert S96["parent_component_arrays_checked"] == 10
assert S96["real_segmentation_inference_completed"] is False
assert S96["reference_dice_measured"] is False
assert S96["lifecycle"] == "QUALIFIED_FOR_REFERENCE_PILOT"

assert D["publication_policy"]["aws_canonical"] is True
assert D["publication_policy"]["github_employer_facing"] is True
assert D["publication_policy"]["row_level_predictions_public"] is False
assert D["publication_policy"]["model_weights_public"] is False
assert D["publication_policy"]["public_checks_require_network"] is False

for notebook, boundary in [
    ("notebooks/12_owned_residual_and_representation_frontier.ipynb", "aggregate-public-safe-historical"),
    ("notebooks/13_parent_reconstruction_and_anatomy_qualification.ipynb", "aggregate-public-safe-stage96"),
]:
    nb = json.loads((ROOT / notebook).read_text())
    code = [c for c in nb["cells"] if c["cell_type"] == "code"]
    outs = [o for c in code for o in c.get("outputs", [])]
    assert not any(o.get("output_type") == "error" for o in outs)
    assert sum("application/vnd.plotly.v1+json" in (o.get("data") or {}) for o in outs) >= 2
    assert sum("image/svg+xml" in (o.get("data") or {}) for o in outs) >= 2
    assert nb["metadata"]["publication_boundary"] == boundary

paths = [
    "README.md",
    "docs/PROJECT_STATUS.md",
    "docs/AWS_RESIDUAL_FRONTIER.md",
    "docs/PARENT_RECONSTRUCTION_FRONTIER.md",
    "docs/ANATOMY_AWARE_TRANSFER_PROGRAM.md",
    "docs/ANATOMY_MODEL_QUALIFICATION.md",
    "docs/REPRODUCIBILITY.md",
    "reports/current_frontier/results.json",
    "src/rsna_research/anatomy_qualification.py",
    "tests/test_anatomy_qualification.py",
    "notebooks/12_owned_residual_and_representation_frontier.ipynb",
    "notebooks/13_parent_reconstruction_and_anatomy_qualification.ipynb",
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

for pattern in ("test_current_frontier.py", "test_anatomy_qualification.py"):
    subprocess.run(
        [
            sys.executable,
            "-m",
            "unittest",
            "discover",
            "-s",
            str(ROOT / "tests"),
            "-p",
            pattern,
        ],
        check=True,
    )

print("CURRENT_FRONTIER_PUBLICATION_PASSED")
