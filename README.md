# RSNA Knee Abnormality Detection

**MRI image-model research, scored-reference deployment engineering, and leakage-aware residual modeling.**

A notebook-first machine-learning project by **Alvaro Mendizabal** for twelve knee-MRI findings. Reports are used only as training-supervision evidence; test-time prediction is image-only. AWS/SageMaker is the canonical private research environment, while this public repository is the curated employer-facing record.

> **Latest published state: verified execution evidence through Stage 72 submission-boundary hardening.** The historically best **0.933** scored reference remains the official control. A user-supplied September 29 leaderboard snapshot shows **0.961** at the top, a public-score gap of **0.028**. Stage 70 produced a complementary ResNet34/224 screen that advanced to independent confirmation. Stage 71 then delivered a strong aggregate blend gain but missed the frozen promotion rule because one confirmation fold was marginally negative. The branch is therefore closed rather than rationalized after the fact. Stage 72 is submission engineering only; **no new official score is claimed yet**.

## Start here

Open **[11 — Residual confirmation and submission boundary](notebooks/11_residual_confirmation_and_submission_boundary.ipynb)** for the current story: Stage 70 screening, Stage 71 independent confirmation, the preregistered gate outcome, and the transition from AWS research to the final competition-submission boundary.

Then read **[AWS residual frontier](docs/AWS_RESIDUAL_FRONTIER.md)**, **[Scored-reference frontier](docs/SCORED_REFERENCE_FRONTIER.md)**, **[Project status](docs/PROJECT_STATUS.md)**, and **[Training frontier](docs/TRAINING_FRONTIER.md)**.

## Current evidence

| Evidence boundary | Result |
|---|---:|
| Historical scored reference | **0.933 public macro-ROC-AUC** |
| User-supplied 2026-09-29 leaderboard snapshot | **0.961 leader** |
| Public-score gap | **0.028** |
| Stage 70 fixed blend vs grouped control | **0.789156 vs 0.787827; +0.001329** |
| Stage 70 paired bootstrap positive fraction | **96.3%** |
| Stage 70 median Spearman vs grouped control | **0.8177** |
| Stage 71 fixed blend vs grouped control | **0.800373 vs 0.797936; +0.002437** |
| Stage 71 confirmation fold deltas | **+0.002300 / -0.000085 / +0.005097** |
| Stage 71 paired bootstrap positive fraction | **100%** |
| Stage 71 promotion decision | **not promoted — frozen all-folds-nonnegative gate failed** |
| Canonical exact-window cache | **4,407 studies / 69.14 GiB** |
| Leakage-aware grouped research rows | **4,349 non-gold / 58 audit-only gold** |
| Stage 72 | **submission boundary hardened; no new official score yet** |

Internal grouped metrics are model-selection evidence and are **not** presented as substitutes for public leaderboard AUC.

## What the project demonstrates

- **Scored-baseline discipline:** the 0.933 system remains the official control until a new Kaggle result is actually scored.
- **Independent confirmation:** promising screening gains are retested on untouched grouped folds before promotion.
- **Preregistered decision rules:** a +0.002437 mean confirmation gain was still rejected because one frozen fold was slightly negative.
- **Complementarity-first modeling:** residual branches are evaluated for useful diversity relative to a stronger parent, not only standalone AUC.
- **Failure-driven engineering:** source, storage, tensor-layout, integrity, storage-budget, and authentication assumptions are converted into explicit gates.
- **AWS-first research:** canonical data, folds, labels, training, validation, checkpoints, and experiment state remain on AWS; Kaggle is reserved for the submission boundary.
- **Semi-reproducible public layer:** aggregate evidence, validation contracts, notebooks, and tests are public; private weights, MRI, row-level predictions, and exact competition glue remain private.

## Notebook guide

- [01 — Metadata and representation audit](notebooks/01_metadata_and_representation_audit.ipynb)
- [02 — Protocol feature investigation](notebooks/02_protocol_feature_investigation.ipynb)
- [03 — Image-context feature investigation](notebooks/03_image_context_feature_investigation.ipynb)
- [04 — Supervision and validation](notebooks/04_supervision_and_validation.ipynb)
- [05 — Multilingual teacher feasibility](notebooks/05_multilingual_teacher_pilot.ipynb)
- [06 — Image models and replication](notebooks/06_image_models_and_replication.ipynb)
- [07 — Full-data training frontier](notebooks/07_deployment_and_training_frontier.ipynb)
- [08 — Heterogeneous ensemble and deployment validation](notebooks/08_heterogeneous_ensemble_and_deployment_validation.ipynb)
- [09 — Scored-reference recovery and runtime frontier](notebooks/09_scored_reference_recovery_and_runtime.ipynb)
- [10 — AWS-only residual frontier](notebooks/10_aws_only_residual_frontier.ipynb)
- **[11 — Residual confirmation and submission boundary](notebooks/11_residual_confirmation_and_submission_boundary.ipynb)** — current entry point

Notebook 11 contains aggregate evidence only. It does not access AWS, expose identifiers, publish row-level predictions, reveal weights, or include the private competition stack.

## Public repository versus AWS workspace

**GitHub is the curated review and semi-reproducible engineering layer. AWS remains the canonical private research workspace.** Raw MRI, report text, identifiers, scanner assignments, row-level predictions, cache shards, model weights, credentials, return bundles, PYZ runners, and source-specific competition implementation details stay outside Git history.

Public checks use synthetic or aggregate evidence only:

`python -m unittest discover -s tests`

`python tools/public_quality.py`

No diagnostic or clinical use is claimed.
