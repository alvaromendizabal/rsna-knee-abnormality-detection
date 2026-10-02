# RSNA Knee Abnormality Detection

**MRI image-model research, leakage-aware validation, target-specific residual modeling, and representation-diversity experiments.**

A notebook-first machine-learning project by **Alvaro Mendizabal** for twelve knee-MRI findings. AWS/SageMaker is the canonical private research environment; this public repository is the curated employer-facing layer. Raw MRI, identifiers, row-level predictions, model weights, private runners, and competition-specific inference glue stay outside Git history.

> **Latest verified public state: AWS research through Stage 80; Stage 81 is prepared but not yet executed.** The current official public-score incumbent is **0.943 macro ROC-AUC**. A user-supplied October 1 leaderboard snapshot shows **0.961** at the top, leaving a **0.018** public-score gap. Internally, a target-specific residual component was independently confirmed and promoted on all five grouped folds. A later dense-anatomy branch was executed correctly and closed as a scientific negative rather than tuned post hoc.

## Start here

Open **[12 — Owned residual and representation frontier](notebooks/12_owned_residual_and_representation_frontier.ipynb)** for the current story: the promoted target-specific residual, the AWS-only research boundary, the closed dense-anatomy experiment, and the next representation-diversity frontier.

Then read **[Project status](docs/PROJECT_STATUS.md)** and **[AWS residual frontier](docs/AWS_RESIDUAL_FRONTIER.md)**.

## Current evidence

| Evidence boundary | Result |
|---|---:|
| Current official public best | **0.943 macro ROC-AUC** |
| User-supplied 2026-10-01 leaderboard snapshot | **0.961 leader** |
| Public-score gap | **0.018** |
| Canonical exact-window cache | **4,407 studies / 69.14 GiB** |
| Grouped research rows | **4,349 non-gold / 58 audit-only gold** |
| Scanner groups | **59; zero cross-fold leakage** |
| Current owned internal OOF | **0.793686 macro ROC-AUC** |
| Promoted residual full-OOF gain | **+0.002479** |
| Promoted target gains | **MCL +0.012874; Lateral Meniscus +0.016871** |
| Dense-anatomy screen | **−0.000801 macro AUC; closed negative** |
| Dense-anatomy bootstrap positive fraction | **7.5%** |
| Next branch | **dense self-supervised feature distillation; prepared, not executed** |

Internal grouped metrics are model-selection evidence and are **not directly comparable** with the public leaderboard score.

## What this project demonstrates

- **AWS-first ML ownership:** canonical data, preprocessing, training, OOF validation, checkpoints, diagnostics, notebooks, and experiment state remain on SageMaker.
- **Leakage-aware validation:** scanner-grouped folds, audit-only gold rows, and zero gold optimizer rows.
- **Target-specific modeling:** weak findings receive specialist residual treatment rather than forcing one global blend policy across all targets.
- **Independent confirmation:** promising screening evidence must survive untouched folds before promotion.
- **Scientific negative results:** a correctly executed branch is closed when the frozen evidence is weak, instead of being rescued with post-hoc tuning.
- **Representation diversity:** the current frontier prioritizes decorrelated features and residual signal over blind backbone scaling.
- **Failure-driven engineering:** source, storage, tensor-layout, numeric-equivalence, and runtime assumptions are converted into regression gates.
- **Semi-reproducible publication:** aggregate evidence, decision contracts, tests, and executed notebooks are public; competition-sensitive assets remain private.

## Notebook guide

- [01 — Metadata and representation audit](notebooks/01_metadata_and_representation_audit.ipynb)
- [02 — Protocol feature investigation](notebooks/02_protocol_feature_investigation.ipynb)
- [03 — Image-context feature investigation](notebooks/03_image_context_feature_investigation.ipynb)
- [04 — Supervision and validation](notebooks/04_supervision_and_validation.ipynb)
- [05 — Multilingual teacher feasibility](notebooks/05_multilingual_teacher_pilot.ipynb)
- [06 — Image models and replication](notebooks/06_image_models_and_replication.ipynb)
- [07 — Full-data training frontier](notebooks/07_deployment_and_training_frontier.ipynb)
- [08 — Heterogeneous ensemble and deployment validation](notebooks/08_heterogeneous_ensemble_and_deployment_validation.ipynb)
- [09 — Scored-reference recovery and runtime](notebooks/09_scored_reference_recovery_and_runtime.ipynb)
- [10 — AWS-only residual frontier](notebooks/10_aws_only_residual_frontier.ipynb)
- [11 — Residual confirmation and submission boundary](notebooks/11_residual_confirmation_and_submission_boundary.ipynb)
- **[12 — Owned residual and representation frontier](notebooks/12_owned_residual_and_representation_frontier.ipynb)** — current entry point

Notebook 12 contains aggregate evidence only. It does not access AWS, expose identifiers, publish row-level predictions, reveal model weights, or include private competition implementation details.

## Public repository versus private AWS workspace

**GitHub is the curated review and semi-reproducible engineering layer. AWS remains the canonical research workspace.**

Private by design:

- raw MRI and reports
- study identifiers and scanner assignments
- row-level OOF/test predictions
- cache shards and memmaps
- model weights and checkpoints
- private runners and return bundles
- credentials and service state
- exact production/submission glue

Public checks:

`python -m unittest discover -s tests`

`python tools/check_current_frontier.py`

No diagnostic or clinical use is claimed.
