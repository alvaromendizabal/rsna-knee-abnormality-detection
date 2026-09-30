# RSNA Knee Abnormality Detection

**MRI image-model research, scored-reference deployment engineering, and leakage-aware residual modeling.**

A notebook-first machine-learning project by **Alvaro Mendizabal** for twelve knee-MRI findings. Reports are used only as training-supervision evidence; test-time prediction is image-only. AWS/SageMaker is the canonical private research environment, while this public repository is the curated employer-facing record.

> **Latest published state: verified execution evidence through Stage 69; Stage 70 prepared, not executed.** The historically best **0.933** scored reference remains the mandatory public control. A user-supplied September 29 leaderboard snapshot shows **0.961** at the top, a public-score gap of **0.028**. After reference-runtime recovery succeeded, development-time preview acquisition was closed when competition-data access was unavailable in AWS. The project then pivoted to an AWS-only, leakage-aware residual-model program using the existing grouped folds and exact-window cache. Two engineering failures exposed and hardened important assumptions: the canonical cache lives in object storage, and its tensor layout is **NCHW**, not NHWC. No new accuracy result is claimed from these stages.

## Start here

Open **[10 — AWS-only residual frontier](notebooks/10_aws_only_residual_frontier.ipynb)** for the current story: the 0.933 control, the source-access decision, canonical cache contract, failure-driven hardening, and the prepared ResNet34/224 screening experiment.

Then read **[AWS residual frontier](docs/AWS_RESIDUAL_FRONTIER.md)**, **[Scored-reference frontier](docs/SCORED_REFERENCE_FRONTIER.md)**, **[Project status](docs/PROJECT_STATUS.md)**, and **[Training frontier](docs/TRAINING_FRONTIER.md)**.

## Current evidence

| Evidence boundary | Result |
|---|---:|
| Historical scored reference | **0.933 public macro-ROC-AUC** |
| User-supplied 2026-09-29 leaderboard snapshot | **0.961 leader** |
| Public-score gap | **0.028** |
| Reference GPU checkpoint checks | **32 / 32 passed** |
| Stored native-model fingerprints checked | **20** |
| Controlled Rad-head benchmark | **1.274× head-only speed ratio** |
| Canonical exact-window cache | **4,407 studies / 69.14 GiB** |
| Leakage-aware grouped research rows | **4,349 non-gold / 58 audit-only gold** |
| Stage 67 development preview path | **closed after source-access block** |
| Stage 68 model fits | **0 — source-location failure** |
| Stage 69 model fits | **0 — cache-layout failure** |
| Stage 70 | **prepared, not executed** |

Internal grouped metrics are model-selection evidence and are **not** presented as substitutes for public leaderboard AUC.

## What the project demonstrates

- **Scored-baseline discipline:** the 0.933 system remains the control for public-score improvement work.
- **Failure-driven engineering:** environment, source, storage, and tensor-layout assumptions are converted into explicit regression gates rather than patched ad hoc.
- **AWS-first research:** canonical data, folds, labels, training, validation, checkpoints, and experiment state remain on AWS; Kaggle is reserved for the final submission boundary.
- **Leakage-aware model development:** 59 scanner groups, 4,349 non-gold research rows, 58 audit-only expert rows, and zero gold optimizer rows.
- **Residual-model strategy:** new branches are judged for complementary signal rather than standalone score alone.
- **Semi-reproducible public layer:** aggregate evidence, layout contracts, experiment state, notebooks, and tests are public; private weights, MRI, row-level predictions, and exact competition glue remain private.

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
- **[10 — AWS-only residual frontier](notebooks/10_aws_only_residual_frontier.ipynb)** — current entry point

Notebook 10 contains aggregate/synthetic evidence only. It does not access AWS, expose identifiers, publish row-level predictions, reveal weights, or include the private competition stack.

## Public repository versus AWS workspace

**GitHub is the curated review and semi-reproducible engineering layer. AWS remains the canonical private research workspace.** Raw MRI, report text, identifiers, scanner assignments, row-level predictions, cache shards, model weights, credentials, return bundles, and source-specific competition implementation details stay outside Git history.

Public checks use synthetic or aggregate evidence only:

`python -m unittest discover -s tests`

`python tools/public_quality.py`

No diagnostic or clinical use is claimed.
