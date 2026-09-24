# RSNA Knee Abnormality Detection

**MRI image-model research, reproducible deployment validation, and a complete scanner-grouped training frontier.**

A notebook-first machine-learning project by **Alvaro Mendizabal** for twelve knee-MRI findings. Reports are used only as training-supervision evidence; test-time prediction is image-only. The project spans MRI protocol/geometry research, weak supervision, DINOv2 transfer learning, public CoAtNet/Raptor reproduction, heterogeneous ensembles, code-competition deployment, and leakage-aware grouped validation.

> **Latest published milestone: Stages 33–36 · September 24, 2026 UTC.** The exact-window cache now covers **4,407 / 4,407 training studies across 14 / 14 shards**. A scanner catalog produced **59 scanner groups** and a leakage-safe five-fold split of **870 / 870 / 870 / 870 / 869** non-gold validation studies, while all **58 expert studies remain audit-only**. A matched Stage-34 training pilot improved the independent DINOv2 branch from **0.760266 to 0.763762 grouped macro-AUC**; an agreement-weighted supervision variant underperformed and was stopped. The Stage-36 image-only code submission then scored **0.820 public AUC**, establishing that the standalone DINO branch remains well below the reproduced **0.933** reference ensemble and the **0.958** returned leader.

## Start here

Open **[07 — Full-data training frontier](notebooks/07_deployment_and_training_frontier.ipynb)** for the current research story: complete-data readiness, grouped validation, the Stage-34 controlled training result, the Stage-36 official score, and the next ceiling-escape gates.

Then read **[Training frontier](docs/TRAINING_FRONTIER.md)** for the ranked research backlog and **[Image-model research record](docs/IMAGE_MODELS.md)** for architecture, ablations, provenance, and negative results.

## Current evidence

| Evaluation setting | System / evidence | Result |
|---|---|---:|
| Official public leaderboard | Reproduced public multi-model reference ensemble, submission `56442573` | **0.933** |
| Same returned leaderboard context | Highest listed score | **0.958** |
| Official public leaderboard | Independently trained DINOv2-Small epoch-3 code submission `56507693` | **0.820** |
| Scanner-grouped fold 0 | Stage-11 epoch-2 starting checkpoint | **0.760266** |
| Scanner-grouped fold 0 | Matched epoch-3 baseline | **0.763762** |
| Scanner-grouped fold 0 | Agreement-weighted epoch-3 candidate | **0.762969** |
| Training readiness | Exact-window cache | **4,407 / 4,407 studies (100%)** |
| Validation readiness | Scanner-grouped split | **5 folds, 59 scanner groups, 0 cross-fold group leakage** |

The **0.025 gap** remains the comparable difference between the 0.933 scored reference and the 0.958 returned leader. The independent DINO result is reported separately because it is a different system and scored substantially lower. Local grouped AUC is not presented as a substitute for leaderboard AUC.

## What the project demonstrates

- **End-to-end experimental ownership:** data contracts, validation design, training, deployment, score reconciliation, and explicit promotion/kill decisions are connected in one reproducible research program.
- **Leakage-aware validation:** scanner-group isolation, 58 sealed expert-audit studies, five balanced folds, zero gold optimizer rows, and explicit non-promotion of exposed audit evidence.
- **MRI representation engineering:** physical field-of-view cropping, contiguous slice triplets, plane/contrast selection, laterality normalization, missing-view handling, and exact-window caching.
- **Modern transfer learning:** an independently trained DINOv2 branch plus strict reproduction of a 73.1M-parameter CoAtNet/Raptor branch.
- **Scientific negative results:** the primary heterogeneous blend failed replication; agreement-weighted supervision underperformed a matched baseline; both directions were stopped instead of rationalized.
- **Deployment rigor:** strict checkpoint loading, dynamic hidden-test handling, offline T4 execution, schema/range checks, and one guarded code-competition submission.
- **Data-complete frontier:** the project has moved from partial-cache infrastructure into cache-equivalence, trainable-depth, full five-fold OOF training, geometry, and OOF ensembling research.

## Notebook guide

- [01 — Metadata and representation audit](notebooks/01_metadata_and_representation_audit.ipynb)
- [02 — Protocol feature investigation](notebooks/02_protocol_feature_investigation.ipynb)
- [03 — Image-context feature investigation](notebooks/03_image_context_feature_investigation.ipynb)
- [04 — Supervision and validation](notebooks/04_supervision_and_validation.ipynb)
- [05 — Multilingual teacher feasibility](notebooks/05_multilingual_teacher_pilot.ipynb)
- [06 — Image models and replication](notebooks/06_image_models_and_replication.ipynb)
- **[07 — Full-data training frontier](notebooks/07_deployment_and_training_frontier.ipynb)** — current entry point

Notebook 07 replays verified aggregate evidence only. It does not access AWS, poll Kaggle, expose study identifiers, or claim results from in-flight stages.

## Public repository versus AWS workspace

**GitHub is the curated review and reproducibility layer. AWS remains the canonical private research workspace.** This repository intentionally excludes raw MRI, report text, study identifiers, row-level predictions, cache shards, model weights, private logs, credentials, environments, and full return bundles.

Public checks use synthetic or aggregate evidence only:

`python -m unittest discover -s tests`

`python tools/public_quality.py`

See [current status](docs/PROJECT_STATUS.md), [training frontier](docs/TRAINING_FRONTIER.md), [data access](docs/DATA_ACCESS.md), and [research sources](docs/SOURCES.md). No diagnostic or clinical use is claimed.
