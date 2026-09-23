# RSNA Knee Abnormality Detection

**MRI image-model research, reproducible deployment validation, and a data-complete training frontier.**

A notebook-first machine-learning project by **Alvaro Mendizabal** for twelve knee-MRI findings. Reports are used only as training-supervision evidence; test-time prediction is image-only. The project spans protocol/geometry research, weak supervision, DINOv2 transfer learning, public CoAtNet/Raptor reproduction, heterogeneous ensembles, deployment-parity testing, and a scanner-grouped full-data training roadmap.

> **Latest published milestone: Stage 32 · September 23, 2026 UTC.** Stage 31 completed a hermetic CPU shadow, offline Tesla T4 preview, and one guarded candidate submission. Stage 32 then verified that the candidate was still pending, current competition metadata matched the accepted AWS copy, and only **960 / 4,407 training studies (21.8%)** were present in the exact-window cache. The next competitive step is therefore complete-data grouped training—not another deployment repair or exposed-cohort blend sweep.

## Start here

Open **[07 — Deployment and training frontier](notebooks/07_deployment_and_training_frontier.ipynb)** for the current research story: official-score boundaries, CPU/GPU parity, cache coverage, and the ranked ceiling-escape backlog.

Then read **[Training frontier](docs/TRAINING_FRONTIER.md)** for the next modeling decision and **[Image-model research record](docs/IMAGE_MODELS.md)** for architecture, ablations, provenance, and limitations.

## Current evidence

| Evaluation setting | System / evidence | Result |
|---|---|---:|
| Official public leaderboard, verified return | Reproduced public multi-model reference ensemble, submission `56442573` | **0.933** |
| Same returned leaderboard page | Highest listed score | **0.958** |
| Exact Stage-31 release candidate | 90% fluid-only Raptor + 10% DINOv2, submission `56476938` | **Pending in Stage-32 evidence** |
| Offline Tesla T4 preview | Maximum DINO CPU/GPU difference | **1.043e-6** |
| Offline Tesla T4 preview | Maximum Raptor CPU/GPU difference | **5.960e-7** |
| Offline Tesla T4 preview | Maximum blend CPU/GPU difference | **5.782e-7** |
| Training readiness | Accepted exact-window cache | **960 / 4,407 studies (21.8%)** |

The **0.025 leaderboard gap** is a dated, comparable difference between the 0.933 scored reference and the 0.958 returned leader. The pending candidate has no published score in the Stage-32 evidence, so it is not counted as an improvement. Deployment parity proves implementation fidelity, not predictive superiority.

## What the project demonstrates

- **Leakage-aware validation:** scanner-group reasoning, sealed expert-audit rows, explicit promotion/kill thresholds, and preservation of negative results.
- **MRI representation engineering:** physical field-of-view cropping, true contiguous slice triplets, plane/contrast selection, target-specific attention, missing-view handling, and real-DICOM parity checks.
- **Modern transfer learning:** an independently trained DINOv2 branch plus strict reproduction of a 73.1M-parameter CoAtNet/Raptor branch.
- **Scientific ensembling:** screening, disjoint-cohort replication, rejection of a failed primary blend, and a guarded secondary release whose score remains pending.
- **Deployment rigor:** hermetic CPU shadow inference, strict checkpoint loading, explicit numerical contracts, offline T4 execution, and component-level CPU/GPU parity before submission.
- **Data-centric ceiling escape:** Stage 32 identified incomplete training-data coverage and missing fold-complete OOF evidence as the current bottleneck.

## Notebook guide

- [01 — Metadata and representation audit](notebooks/01_metadata_and_representation_audit.ipynb)
- [02 — Protocol feature investigation](notebooks/02_protocol_feature_investigation.ipynb)
- [03 — Image-context feature investigation](notebooks/03_image_context_feature_investigation.ipynb)
- [04 — Supervision and validation](notebooks/04_supervision_and_validation.ipynb)
- [05 — Multilingual teacher feasibility](notebooks/05_multilingual_teacher_pilot.ipynb)
- [06 — Image models and replication](notebooks/06_image_models_and_replication.ipynb)
- **[07 — Deployment and training frontier](notebooks/07_deployment_and_training_frontier.ipynb)** — current entry point

Notebook 07 replays verified aggregate evidence only. It does not access AWS, rerun MRI inference, poll Kaggle, or claim completion of the next data-build stage.

## Public repository versus AWS workspace

**GitHub is the curated review and reproducibility layer. AWS remains the canonical research workspace.** This public repository intentionally excludes raw MRI, reports, study identifiers, row-level predictions, model weights, private logs, credentials, environments, and full return bundles.

Public checks use synthetic or aggregate evidence only:

`python -m unittest discover -s tests`

`python tools/public_quality.py`

See [current status](docs/PROJECT_STATUS.md), [training frontier](docs/TRAINING_FRONTIER.md), [data access](docs/DATA_ACCESS.md), and [research sources](docs/SOURCES.md). No diagnostic or clinical use is claimed.
