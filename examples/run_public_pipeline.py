#!/usr/bin/env python3
"""Run actual CPU logistic fits on generated data; no MRI data or cloud access."""
import argparse
import json
import os
from pathlib import Path
import sys

# Tiny full-batch matrix operations are faster with one BLAS worker. Set before
# importing NumPy; these limits apply only to this standalone demo process.
for variable in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[variable] = "1"
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from rsna_review.public_pipeline import CacheValidationError, DemoConfig, run_pipeline


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("demo-output"))
    parser.add_argument("--seed", type=int, default=2026)
    parser.add_argument("--stop-after-fold", type=int, help="Commit this many folds, then pause successfully; omit to resume all folds.")
    args = parser.parse_args(argv)
    try:
        result = run_pipeline(args.output, DemoConfig(seed=args.seed), stop_after_fold=args.stop_after_fold)
    except (CacheValidationError, ValueError, OSError) as exc:
        parser.exit(2, f"Demo stopped: {exc}\n")
    print(json.dumps({"status": result["status"], "evidence_type": result["evidence_type"],
                      "completed_folds": result["completed_folds"], "metrics": result["metrics"],
                      "execution": result["execution"], "report": str(args.output / "report.html")}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
