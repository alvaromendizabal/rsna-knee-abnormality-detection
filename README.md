# RSNA Knee Abnormality Detection

**MRI image-model research, heterogeneous ensembling, leakage-aware validation, and deployment parity engineering.**

A notebook-first machine-learning project by **Alvaro Mendizabal** for twelve knee-MRI findings. Reports are used only as training-supervision evidence; test-time prediction is image-only. AWS/SageMaker is the canonical research environment, while this public repository is the curated employer-facing record.

> **Latest published milestone: Stage 54 · September 27, 2026 UTC.** The project progressed from a complete scanner-grouped DINO baseline to a heterogeneous DINO + MaxViT ensemble, then confirmed a targeted MCL + Lateral Meniscus expert overlay on three untouched folds. Subsequent deployment work reproduced all 15 owned checkpoints on bounded samples, established exact sampled raw-image parity, and exercised the raw-input ensemble end to end. Stage 54 then completed a controlled depth-position experiment and rejected the proposed representation change under its prespecified fold-level gate.

## Start here

Open **[08 — Heterogeneous ensemble and deployment validation](notebooks/08_heterogeneous_ensemble_and_deployment_validation.ipynb)** for the current research story: OOF progression, independent confirmation, deployment parity, raw-input validation, and the latest controlled negative experiment.

Then read **[Current project status](docs/PROJECT_STATUS.md)** and **[Training frontier](docs/TRAINING_FRONTIER.md)** for the evidence boundary, closed directions, and next high-value research/deployment gates.

## Current evidence

| Evaluation setting | System / evidence | Result |
|---|---|---:|
| Scanner-grouped five-fold OOF | Stage 43 DINO incumbent | **0.786557** |
| Scanner-grouped five-fold OOF | Stage 47 DINO + MaxViT cross-fitted blend | **0.791208** |
| Independent confirmation folds 1, 3, 4 | Stage 47 baseline | **0.795488** |
| Independent confirmation folds 1, 3, 4 | Stage 50 MCL + Lateral Meniscus overlay | **0.798017** |
| Independent confirmation delta | Stage 50 versus frozen baseline | **+0.002529** |
| Five-fold descriptive OOF | Stage 50 selected system | **0.793687** |
| Official public leaderboard, historical | Reproduced public multi-model reference | **0.933** |
| Same returned leaderboard context, historical | Highest listed score | **0.958** |
| Deployment validation | Sampled archived-probability replay | **10,080 comparisons passed** |
| Raw preprocessing validation | Complete canary studies | **3 / 3 exact at uint8 pixel level** |
| Stage 54 controlled experiment | Corrected-depth head versus matched legacy head, fold 0 | **Rejected** |

The **0.025 public gap** is the historically comparable difference between the 0.933 scored reference and the 0.958 returned leader. Internal grouped OOF values are model-selection evidence and are **not** presented as substitutes for leaderboard AUC.

## What the project demonstrates

- **End-to-end experimental ownership:** data contracts, scanner-group validation, training, model selection, deployment parity, cost control, and explicit promotion/kill decisions are connected in one research program.
- **Leakage-aware validation:** 59 scanner groups, five group-isolated folds, 4,349 non-gold OOF rows, 58 expert audit-only studies, and zero gold optimizer rows.
- **Heterogeneous model research:** a DINOv2 image branch was complemented by a weaker standalone MaxViT branch whose prediction diversity produced a material OOF ensemble gain.
- **Independent confirmation:** the Stage 50 two-target overlay was frozen using screening folds 0 and 2, then improved all three untouched confirmation folds.
- **Scientific negative results:** ConvNeXt complement, four-target weak-expert blending, agreement weighting, and the Stage 54 depth-position change were stopped when their gates failed.
- **Deployment rigor:** exact cache-aligned uint8 preprocessing, strict checkpoint lineage, sampled replay across all 15 owned checkpoints, exact raw-image canaries, and whole-cohort ranking semantics.
- **Efficiency engineering:** resumable feature banks, same-process threaded I/O, bounded GPU work, checkpoint reuse, and explicit compute-cost accounting.

## Latest controlled negative result

Stage 54 compared two six-epoch heads on the same frozen feature bank, initialization, optimizer rows, seed, and held-out fold:

| Fold-0 system | Macro-AUC |
|---|---:|
| Frozen parent head | 0.747798 |
| Matched legacy-depth head | **0.748827** |
| Corrected relative-depth head | 0.748599 |
| Stage-50 incumbent overlay boundary | 0.788045 |
| Legacy-depth 10% research overlay | 0.787949 |
| Corrected-depth 10% research overlay | 0.788083 |

The corrected head did not beat the matched legacy control, so a condition required to hold on every screening fold failed. The experiment was closed before spending another fold of GPU time. The incumbent was not modified.

## Notebook guide

- [01 — Metadata and representation audit](notebooks/01_metadata_and_representation_audit.ipynb)
- [02 — Protocol feature investigation](notebooks/02_protocol_feature_investigation.ipynb)
- [03 — Image-context feature investigation](notebooks/03_image_context_feature_investigation.ipynb)
- [04 — Supervision and validation](notebooks/04_supervision_and_validation.ipynb)
- [05 — Multilingual teacher feasibility](notebooks/05_multilingual_teacher_pilot.ipynb)
- [06 — Image models and replication](notebooks/06_image_models_and_replication.ipynb)
- [07 — Full-data training frontier](notebooks/07_deployment_and_training_frontier.ipynb)
- **[08 — Heterogeneous ensemble and deployment validation](notebooks/08_heterogeneous_ensemble_and_deployment_validation.ipynb)** — current entry point

Notebook 08 contains aggregate evidence only. It does not access AWS, expose study identifiers, publish row-level predictions, or include model weights.

## Public repository versus AWS workspace

**GitHub is the curated review and reproducibility layer. AWS remains the canonical private research workspace.** This repository intentionally excludes raw MRI, report text, study identifiers, row-level predictions, cache shards, model weights, private logs, credentials, environments, and full return bundles.

Public checks use synthetic or aggregate evidence only:

python -m unittest discover -s tests

python tools/public_quality.py

See [current status](docs/PROJECT_STATUS.md), [training frontier](docs/TRAINING_FRONTIER.md), [data access](docs/DATA_ACCESS.md), and [research sources](docs/SOURCES.md). No diagnostic or clinical use is claimed.
