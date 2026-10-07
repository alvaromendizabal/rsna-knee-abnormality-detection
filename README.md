# RSNA Knee Abnormality Detection

[![Publication checks](https://github.com/alvaromendizabal/rsna-knee-abnormality-detection/actions/workflows/publication-checks.yml/badge.svg)](https://github.com/alvaromendizabal/rsna-knee-abnormality-detection/actions/workflows/publication-checks.yml)
[![Public quality](https://github.com/alvaromendizabal/rsna-knee-abnormality-detection/actions/workflows/public-quality.yml/badge.svg)](https://github.com/alvaromendizabal/rsna-knee-abnormality-detection/actions/workflows/public-quality.yml)

**End-to-end medical-imaging ML research on AWS: leakage-aware validation, heterogeneous deep-learning reconstruction, anatomy-aware representation learning, winner-informed cross-slice modeling, resumable GPU experimentation, and production-style experiment governance.**

A notebook-first project by **Alvaro Mendizabal** for twelve knee-MRI findings. AWS/SageMaker is the canonical private research environment; this repository is the curated employer-facing and semi-reproducible layer. Raw MRI, identifiers, row-level predictions, private checkpoints, return bundles, and exact competition inference/fusion logic stay outside public history.

> **Portfolio review complete through Stage 104; private research remains ongoing.** The project retains a verified external macro ROC-AUC of **0.943** and progressed the same 4,349-study scanner-grouped research population from **0.7943834 to 0.7978448** through winner-informed cross-slice context modeling. A later neighbor-context probe reached **0.7978946**, but its paired uncertainty interval crossed zero, so it is preserved as inconclusive rather than over-promoted.

## 30-second overview

| | |
|---|---|
| **Problem** | Multi-label abnormality detection from heterogeneous knee MRI studies |
| **My ownership** | Data contracts, validation, modeling, inference, cloud execution, failure recovery, experiment design, reproducibility, and publication controls |
| **Scale** | 4,407-study canonical cache; 4,349 grouped development rows; 59 scanner groups |
| **System** | Heterogeneous parent + anatomy qualification + sequence-context research + winner-technique gap analysis |
| **Engineering** | SageMaker + private S3, resumable runners, immutable manifests, parity gates, telemetry, cost bounds, CI |
| **Research discipline** | Matched controls, grouped validation, paired uncertainty, negative-result retention, explicit promotion/kill gates |
| **Current research best** | **0.7978946** point estimate; **0.7978448** is the better-supported recent gain |
| **External record** | **0.943 macro ROC-AUC**, tracked separately from internal development evidence |

### What employers should notice

- **I treated the project as a research system, not a model demo.** Data identity, scanner grouping, checkpoint lineage, runtime state, evaluation membership, and publication policy are first-class.
- **I separated engineering correctness from predictive progress.** Inference parity and cache equivalence are not mislabeled as score improvements.
- **I turned winner research into a capability roadmap.** The public inventory covers **9 prior competitions, 15 top-solution lineages, and 37 technique families** before new training is approved.
- **I improved the full-cohort research system with a controlled mechanism.** Cross-slice context moved the grouped macro AUC from **0.7943834 to 0.7978448**.
- **I did not overstate a later micro-gain.** Stage 104 produced a slightly higher point estimate but crossed zero under paired uncertainty.
- **I made failure reusable.** Avoidable implementation failures became regression tests before the next cost-bearing run.
- **I protect the competitive implementation.** Aggregate evidence and reproducibility contracts are public; raw MRI, row-level predictions, weights, runners, cloud paths, and exact competition logic are not.

## Verified evidence

| Evidence boundary | Verified state |
|---|---:|
| External macro ROC-AUC record | **0.943** |
| Canonical exact-window cache | **4,407 studies / 69.14 GiB** |
| Grouped research rows | **4,349 non-gold / 58 fully labeled audit rows** |
| Scanner groups | **59; zero cross-fold leakage** |
| Stage 84 research baseline | **0.7943834** |
| Stage 102 ordered-context research result | **0.7978448** |
| Stage 104 highest research point estimate | **0.7978946, inconclusive increment** |
| Winner Technique Inventory | **9 competitions / 15 lineages / 37 technique families** |
| High-confidence transfer checklist | **29 mechanisms: 8 full / 11 partial / 6 missing / 4 blocked** |
| Anatomy reference qualification | **9 structures; mean Dice 0.9118** |
| Native parent branch | **20 trained members / 200 window evaluations** |
| A5 parent branch | **5/5 trained folds** |
| Raptor diagnostic views | **4/4 on explicitly incomplete input scope** |
| CoAt-family execution | **8/8 source/checkpoint gates; 7/7 trained predictions** |
| Geometry audit | **2,287 headers + 93 images; zero flags in inspected scope** |

Internal grouped metrics are model-selection evidence and are not presented as interchangeable with the external score.

## Research decisions that matter

| Question | Decision |
|---|---|
| Expand fixed spatial bias? | **No.** Valid negative result. |
| Replace task-aligned work with frozen orthopedic foundation features? | **No.** Valid negative matched screen. |
| Is DICOM geometry the likely missing capability? | **No evidence in inspected scope.** |
| Can the anatomy route segment its reference knee reliably? | **Yes for the reference pilot.** Native-transfer truth remains limited. |
| Does learned cross-slice context add complementary disease signal? | **Yes in grouped development.** Full-cohort macro AUC improved by about 0.00346. |
| Promote the tiny Stage 104 neighbor-context increment? | **No.** Paired uncertainty crosses zero. |
| How are new ideas selected now? | **Winner research → gap analysis → ranking → bounded experiment.** |

## Start here

### 2-minute recruiter review
1. README
2. [Employer case study](docs/EMPLOYER_CASE_STUDY.md)
3. [Notebook 14](notebooks/14_winner_transfer_and_context_modeling.ipynb)

### 10-minute ML engineering review
1. [System architecture](docs/ARCHITECTURE.md)
2. [Reproducibility boundary](docs/REPRODUCIBILITY.md)
3. [Project status](docs/PROJECT_STATUS.md)
4. [Parent reconstruction frontier](docs/PARENT_RECONSTRUCTION_FRONTIER.md)

### 15-minute applied research review
1. [Research timeline](docs/RESEARCH_TIMELINE.md)
2. [Context-modeling frontier](docs/CONTEXT_MODELING_FRONTIER.md)
3. [Winner-transfer frontier](docs/WINNER_TRANSFER_FRONTIER.md)
4. [Anatomy-aware transfer program](docs/ANATOMY_AWARE_TRANSFER_PROGRAM.md)

## Technical stack

**Modeling:** Python, PyTorch, scikit-learn, DINO-style vision encoders, RadImageNet transfer, CoAtNet-family models, cross-slice sequence modeling, attention pooling, calibration, residual modeling, ensembling.

**Medical imaging:** DICOM metadata/geometry, multi-plane MRI, 2.5D and volumetric representations, anatomy-aware localization, segmentation transfer.

**Cloud / ML engineering:** AWS SageMaker, S3, GPU inference, resumable jobs, content-addressed artifacts, immutable manifests, resource telemetry, cost guards.

**Quality / reproducibility:** scanner-grouped validation, leakage audits, paired uncertainty, numerical-parity tests, regression fixtures, CI publication gates, executed Jupyter notebooks, persistent Plotly/SVG output.

## Public reproducibility

**Five-minute review:** [reviewer guide](docs/EMPLOYER_REVIEW_GUIDE.md) → [executed Notebook 14](notebooks/14_winner_transfer_and_context_modeling.ipynb) → [synthetic metric example](examples/run_public_review.py).

The [reproduction guide](docs/REPRODUCIBILITY.md) provides a pinned CPU environment, a four-study synthetic example using the actual public twelve-target metric, the complete public test suite, and real Jupyter replay of Notebooks 12–14. No cloud account, MRI, model download, or GPU is needed.

For the standard-library publication contract, run from the repository root:

    python tools/check_current_frontier.py
    python scripts/verify_review_notebook.py

The source/output verifier checks notebook source and report fingerprints, actual plotted values, saved execution counts, and persistent Plotly/SVG output. Regenerating aggregate charts validates the public review layer; it does not independently reproduce the private experimental scores.

## Notebook guide

Notebooks 01–13 preserve the earlier research path. Notebook 00 is a **prepared, unexecuted private preflight template**, not a runnable public demo. Notebooks 12–14 have executable aggregate chart sources and a documented replay path; older notebooks are archived execution records with their original environment/data assumptions. **[Notebook 14 — Winner transfer and context modeling](notebooks/14_winner_transfer_and_context_modeling.ipynb)** is the current public entry point.

## Public repository versus private AWS workspace

**Public:** aggregate metrics and uncertainty states, architecture, public-safe winner-technique coverage, promotion/closure decisions, helpers/tests, CI, and executed aggregate notebooks.

**Private by design:** MRI/DICOM data and reports, study identifiers and scanner assignments, row-level predictions, cache shards, model weights/checkpoints, source-recovery handles, cloud paths, private runners/returns, and exact competition fusion/inference/submission implementation.

No diagnostic or clinical use is claimed.
