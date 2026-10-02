#!/usr/bin/env python3
from pathlib import Path
import json, math, re, subprocess, sys

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/"reports/current_frontier/results.json").read_text())

P=D["public_score"]
assert P["current_official_best"]==0.943
assert P["leader_snapshot"]==0.961
assert math.isclose(P["gap"],0.018,abs_tol=1e-12)
assert P["internal_metrics_directly_comparable"] is False

A=D["aws_validation"]
assert A["canonical_cache_studies"]==4407
assert A["grouped_non_gold_rows"]==4349
assert A["gold_audit_rows"]==58
assert A["gold_optimizer_rows"]==0
assert A["scanner_groups"]==59
assert A["cross_fold_scanner_groups"]==0
assert A["fold_studies"]==[870,870,870,870,869]

R=D["promoted_target_residual"]
assert R["status"]=="PROMOTED"
assert R["all_folds_positive"] is True
assert R["protected_target_count"]==10
assert math.isclose(R["macro_gain"],0.00247874121884617,abs_tol=1e-15)

S=D["stage80_dense_anatomy"]
assert S["status"]=="SCIENTIFIC_NEGATIVE_SCREEN"
assert S["decision"]=="CLOSE_AT_SCREEN"
assert S["macro_gain"]<0
assert S["bootstrap_positive_fraction"]<0.5

assert D["stage81"]["status"]=="PREPARED_NOT_EXECUTED"
assert D["stage81"]["accuracy_claimed"] is False
assert D["publication_policy"]["aws_canonical"] is True

nb=json.loads((ROOT/"notebooks/12_owned_residual_and_representation_frontier.ipynb").read_text())
code=[c for c in nb["cells"] if c["cell_type"]=="code"]
assert [c.get("execution_count") for c in code]==[1,2,3,4]
outs=[o for c in code for o in c.get("outputs",[])]
assert not any(o.get("output_type")=="error" for o in outs)
assert sum("application/vnd.plotly.v1+json" in (o.get("data") or {}) for o in outs)>=3
assert sum("image/svg+xml" in (o.get("data") or {}) for o in outs)>=3
assert any(
    "OWNED_RESIDUAL_FRONTIER_PUBLICATION_COMPLETE" in "".join(o.get("text",[]))
    for o in outs if o.get("output_type")=="stream"
)

paths=[
    "README.md",
    "docs/PROJECT_STATUS.md",
    "docs/AWS_RESIDUAL_FRONTIER.md",
    "reports/current_frontier/results.json",
    "notebooks/12_owned_residual_and_representation_frontier.ipynb",
]
patterns=[
    r"1\.2\.826\.0\.1\.3680043",
    r"AKIA[A-Z0-9]{16}",
    r"ASIA[A-Z0-9]{16}",
    r"gh[pousr]_[A-Za-z0-9]{20,}",
    r"X-Amz-(?:Signature|Credential)=",
    r"arn:aws:",
    r"/home/sagemaker-user/",
]
for name in paths:
    txt=(ROOT/name).read_text()
    for p in patterns:
        assert not re.search(p,txt), f"private-content pattern in {name}"

subprocess.run([
    sys.executable,"-m","unittest","discover","-s",str(ROOT/"tests"),
    "-p","test_current_frontier.py",
],check=True)

print("CURRENT_FRONTIER_PUBLICATION_PASSED")
