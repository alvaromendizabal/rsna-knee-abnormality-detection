# RSNA Knee Abnormality Detection

**MRI image-model research, heterogeneous ensembling, leakage-aware validation, and scored-reference deployment engineering.**

A notebook-first machine-learning project by **Alvaro Mendizabal** for twelve knee-MRI findings. Reports are used only as training-supervision evidence; test-time prediction is image-only. AWS/SageMaker is the canonical private research environment, while this public repository is the curated employer-facing record.

> **Latest published milestone: Stage 63 · September 28, 2026 UTC.** The project has moved back onto the historically best **0.933** scored reference as the control. The assembled multi-branch reference snapshot now has **32 audited weight files**, **32 / 32 GPU checkpoint checks passed**, and **20 stored native-model fingerprints verified where available**. A trained Rad-head optimization reduced the relevant head-prediction calls from **20 to 15** and measured a **1.274× head-only speed ratio** with exact final CSV bytes on its controlled GPU trial. Complete real-image reproduction of the historical reference remains the next gate; no new leaderboard improvement is claimed.

## Start here

Open **[09 — Scored-reference recovery and runtime frontier](notebooks/09_scored_reference_recovery_and_runtime.ipynb)** for the current story: why the project returned to the strongest scored reference, how its model assets and runtime were recovered safely, what GPU checks now pass, and which speed optimization is ready for real-image validation.

Then read **[Scored-reference frontier](docs/SCORED_REFERENCE_FRONTIER.md)**, **[Current project status](docs/PROJECT_STATUS.md)**, and **[Training frontier](docs/TRAINING_FRONTIER.md)** for the evidence boundary and next score-moving milestones.

## Current evidence

| Evaluation setting | System / evidence | Result |
|---|---|---:|
| Official public leaderboard, historical | Reproduced public multi-model reference | **0.933** |
| Same returned leaderboard context, historical | Highest listed score | **0.958** |
| Historical public gap | Reference to last recorded leader | **0.025** |
| Official public leaderboard, historical | Independent DINO submission | **0.820** |
| Scanner-grouped five-fold OOF | Stage 47 DINO + MaxViT cross-fitted blend | **0.791208** |
| Independent confirmation folds 1, 3, 4 | Stage 50 MCL + Lateral Meniscus overlay | **0.798017** |
| Scored-reference recovery | Weight files audited | **32** |
| Scored-reference GPU readiness | Checkpoints passing GPU probes | **32 / 32** |
| Native-model verification | Stored fingerprints checked | **20** |
| Rad runtime experiment | Head-prediction calls | **20 → 15** |
| Rad runtime experiment | Head-only speed ratio | **1.274×** |

The public 0.933 and 0.958 scores are historical and are not treated as interchangeable with scanner-grouped internal OOF. Stage 63 establishes reference-loader/runtime readiness for the assembled snapshot, **not** a new accuracy result.

## What the project demonstrates

- **Scored-system discipline:** the strongest known scored reference is now the baseline for deployment and improvement work rather than a weaker standalone branch.
- **Model provenance and runtime recovery:** a multi-branch reference was reconstructed across versioned assets, checkpoint identities, isolated runtime dependencies, and strict loader checks without publishing the private weights.
- **GPU validation:** 32 reference checkpoints passed GPU construction/probe checks; 20 stored native fingerprints were verified where available.
- **Performance engineering with correctness gates:** a RadImageNet-head optimization removed diagnostic-only calls while requiring exact final values and CSV bytes before promotion to real-image testing.
- **Leakage-aware research:** scanner-group isolation, audit-only expert studies, independent confirmation, and explicit separation of public-score evidence from internal OOF evidence.
- **Scientific negative results:** weak complements and representation changes are closed when their preregistered gates fail rather than rationalized after the fact.
- **Restartable cloud engineering:** checksum-bound assets, resumable transfers, bounded execution, duplicate-process prevention, and explicit compute-cost accounting.

## Notebook guide

- [01 — Metadata and representation audit](notebooks/01_metadata_and_representation_audit.ipynb)
- [02 — Protocol feature investigation](notebooks/02_protocol_feature_investigation.ipynb)
- [03 — Image-context feature investigation](notebooks/03_image_context_feature_investigation.ipynb)
- [04 — Supervision and validation](notebooks/04_supervision_and_validation.ipynb)
- [05 — Multilingual teacher feasibility](notebooks/05_multilingual_teacher_pilot.ipynb)
- [06 — Image models and replication](notebooks/06_image_models_and_replication.ipynb)
- [07 — Full-data training frontier](notebooks/07_deployment_and_training_frontier.ipynb)
- [08 — Heterogeneous ensemble and deployment validation](notebooks/08_heterogeneous_ensemble_and_deployment_validation.ipynb)
- **[09 — Scored-reference recovery and runtime frontier](notebooks/09_scored_reference_recovery_and_runtime.ipynb)** — current entry point

Notebook 09 contains aggregate evidence only. It does not access AWS, expose patient/study identifiers, publish row-level predictions, reveal model weights, or include the private reference implementation.

## Public repository versus AWS workspace

**GitHub is the curated review and semi-reproducible engineering layer. AWS remains the canonical private research workspace.** This repository intentionally excludes raw MRI, report text, identifiers, scanner assignments, row-level predictions, cache shards, model weights, private logs, credentials, environments, return bundles, and source-specific implementation details that would reproduce the private competition stack verbatim.

Public checks use synthetic or aggregate evidence only:

`python -m unittest discover -s tests`

`python tools/public_quality.py`

See [current status](docs/PROJECT_STATUS.md), [scored-reference frontier](docs/SCORED_REFERENCE_FRONTIER.md), [training frontier](docs/TRAINING_FRONTIER.md), [data access](docs/DATA_ACCESS.md), and [research sources](docs/SOURCES.md). No diagnostic or clinical use is claimed.
