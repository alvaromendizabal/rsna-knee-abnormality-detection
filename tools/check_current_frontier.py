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
assert A["fully_labeled_rows_outside_recovered_selection_lineage"] == 0
assert A["scanner_groups"] == 59
assert A["cross_fold_scanner_groups"] == 0
assert A["fold_studies"] == [870, 870, 870, 870, 869]

F = D["research_frontier"]
assert math.isclose(F["stage84_retained_macro_auc"], 0.7943833865949643, abs_tol=1e-15)
assert math.isclose(F["stage102_ordered_context_macro_auc"], 0.7978447501637148, abs_tol=1e-15)
assert F["stage102_gain_vs_stage84"] > 0.003
assert math.isclose(F["stage104_highest_point_macro_auc"], 0.7978946262164966, abs_tol=1e-15)
assert F["stage104_ci90_lower"] < 0 < F["stage104_ci90_upper"]
assert F["stage104_interpretation"] == "RETAIN_POINT_ESTIMATE_INCONCLUSIVE"
assert F["public_score_comparable"] is False

I = D["winner_technique_inventory"]
assert I["competitions_audited"] >= 8
assert I["top_solution_lineages_audited"] >= 15
assert I["technique_families_identified"] == 37
assert I["high_confidence_transferable_mechanisms"] == 29
assert sum(I[k] for k in ("fully_implemented", "partially_implemented", "missing", "blocked")) == 29

AN = D["anatomy_program"]
assert AN["reference_structures"] == 9
assert AN["reference_mean_dice"] > 0.90
assert AN["reference_min_structure_dice"] > 0.85
assert AN["reference_gate_passed"] is True

S103 = D["stage103_integration"]
assert S103["tracks_completed"] == S103["tracks_total"] == 14
assert S103["cached_image_canaries_verified"] == 10
assert S103["full_cohort_export_parity_passed"] is True
assert S103["new_predictive_gain"] is False

S104 = D["stage104_neighbor_context"]
assert S104["status"] == "SUCCESS_INCONCLUSIVE_HYPOTHESIS"
assert S104["tracks_completed"] == S104["tracks_total"] == 14
assert S104["ci90_lower"] < 0 < S104["ci90_upper"]
assert S104["decision"] == "PRESERVE_POINT_ESTIMATE_CLOSE_MICROTUNING"

assert D["publication_policy"]["aws_canonical"] is True
assert D["publication_policy"]["row_level_predictions_public"] is False
assert D["publication_policy"]["model_weights_public"] is False
assert D["publication_policy"]["exact_competition_fusion_logic_public"] is False
assert D["publication_policy"]["public_checks_require_network"] is False

nb = json.loads((ROOT / "notebooks/14_winner_transfer_and_context_modeling.ipynb").read_text())
code = [c for c in nb["cells"] if c["cell_type"] == "code"]
outs = [o for c in code for o in c.get("outputs", [])]
assert code and all(c.get("execution_count") is not None for c in code)
assert not any(o.get("output_type") == "error" for o in outs)
assert sum("application/vnd.plotly.v1+json" in (o.get("data") or {}) for o in outs) == 4
assert sum("image/svg+xml" in (o.get("data") or {}) for o in outs) == 4
assert nb["metadata"]["publication_boundary"] == "aggregate-public-safe-stage104"
assert "M14_PUBLICATION_COMPLETE" in json.dumps(nb)

paths = [
    "README.md",
    "docs/PROJECT_STATUS.md",
    "docs/EMPLOYER_CASE_STUDY.md",
    "docs/RESEARCH_TIMELINE.md",
    "docs/EMPLOYER_REVIEW_GUIDE.md",
    "docs/CONTEXT_MODELING_FRONTIER.md",
    "docs/WINNER_TRANSFER_FRONTIER.md",
    "reports/current_frontier/results.json",
    "src/rsna_research/current_frontier.py",
    "tests/test_current_frontier.py",
    "tests/test_winner_transfer.py",
    "notebooks/14_winner_transfer_and_context_modeling.ipynb",
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
competitive_framing = [
    "leader" + " snapshot",
    "public-score " + "gap",
    "top " + "score",
    "trying to " + "beat",
    "beat the " + "top",
]

for name in paths:
    txt = (ROOT / name).read_text(encoding="utf-8")
    for pattern in private_patterns:
        assert not re.search(pattern, txt), f"private-content pattern in {name}"
    lowered = txt.lower()
    for fragment in competitive_framing:
        assert fragment.lower() not in lowered, f"external-comparison framing in {name}"

for pattern in ("test_current_frontier.py", "test_winner_transfer.py", "test_employer_portfolio.py"):
    subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", str(ROOT / "tests"), "-p", pattern],
        check=True,
    )

print("CURRENT_FRONTIER_PUBLICATION_PASSED")
