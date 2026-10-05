# RSNA Knee Abnormality Detection

[![Publication checks](https://github.com/alvaromendizabal/rsna-knee-abnormality-detection/actions/workflows/publication-checks.yml/badge.svg)](https://github.com/alvaromendizabal/rsna-knee-abnormality-detection/actions/workflows/publication-checks.yml)

**MRI image-model research with leakage-aware validation, multi-branch parent reconstruction, anatomy-aware representation learning, and production-style ML engineering on AWS.**

A notebook-first machine-learning project by **Alvaro Mendizabal** for twelve knee-MRI findings. AWS/SageMaker is the canonical private research environment; this repository is the curated employer-facing and semi-reproducible layer. Raw MRI, identifiers, row-level predictions, private checkpoints, recovery bundles, and competition-specific inference glue stay outside Git history.

> **Latest verified publication boundary: AWS research through Stage 96 anatomy qualification.** The project retains a verified external macro ROC-AUC of **0.943**, has restored the major trained parent branches on the available input scope, completed validation/acquisition and geometry audits, and advanced into a gated anatomy-localization program without claiming unmeasured score gains.

## Start here

1. **[Project status](docs/PROJECT_STATUS.md)** — current verified state, completed milestones, and next decision.
2. **[Parent reconstruction frontier](docs/PARENT_RECONSTRUCTION_FRONTIER.md)** — how the heterogeneous parent system was restored without publishing private weights.
3. **[Anatomy model qualification](docs/ANATOMY_MODEL_QUALIFICATION.md)** — the public-safe contract for qualifying a pretrained knee localizer before downstream integration.
4. **[Anatomy-aware transfer program](docs/ANATOMY_AWARE_TRANSFER_PROGRAM.md)** — controlled localization, visibility, and local/global fusion research.
5. **[Reproducibility boundary](docs/REPRODUCIBILITY.md)** — what is reproducible publicly, what remains private, and why.
6. **[AWS research frontier](docs/AWS_RESIDUAL_FRONTIER.md)** — grouped validation, residual modeling, negative-result discipline, and AWS-only execution.

## Current verified evidence

| Evidence boundary | Verified state |
|---|---:|
| External macro ROC-AUC | **0.943** |
| Canonical exact-window cache | **4,407 studies / 69.14 GiB** |
| Grouped research rows | **4,349 non-gold / 58 fully labeled audit rows** |
| Scanner groups | **59; zero cross-fold leakage** |
| Native parent branch | **20 trained members / 200 window evaluations** |
| A5 parent branch | **5/5 trained folds** |
| Rad parent branch | **3 source layouts / multiple trained heads** |
| Raptor diagnostic views | **4/4 completed on explicitly incomplete input scope** |
| Recovered CoAt-family execution | **8/8 source/checkpoint gates; 7/7 predictions** |
| Validation/acquisition audit | **7/7 units completed** |
| Geometry audit | **2,287 headers + 93 images; zero flags in inspected scope** |
| Anatomy qualification | **4/4 tracks completed; real segmentation pilot is next** |

Internal grouped metrics are model-selection evidence and are not presented as interchangeable with the external score.

## What this project demonstrates

- **End-to-end ML ownership:** data contracts, preprocessing, validation, training, inference, checkpoint lineage, cost controls, diagnostics, and publication boundaries are treated as one system.
- **Leakage-aware evaluation:** scanner-grouped folds, audit-only rows, exact metric contracts, and explicit separation between development and external evaluation.
- **Multi-branch system reconstruction:** trained DINO, RadImageNet, A5, Raptor, and CoAt-family components are restored as a coherent parent rather than treated as disconnected experiments.
- **Failure-driven engineering:** dependency, tensor-layout, disk-budget, authentication, cloud-permission, and numerical-equivalence failures become deterministic regression tests.
- **Scientific negative results:** well-executed ideas are closed when evidence is weak instead of being rescued with post-hoc tuning.
- **Ceiling-escape research:** external medical-imaging ideas are translated into mechanism-level localization and visibility hypotheses instead of copied by model name.
- **Cost-aware GPU execution:** large assets stream from private storage, expensive work resumes from checkpoints, and bounded runs preserve completed computation.
- **Semi-reproducible publication:** aggregate evidence, decision contracts, public-safe helpers, CI, and executed notebooks are visible while competition-sensitive implementation remains private.

## Research progression

### 1. Validation and residual modeling
The project established a grouped validation boundary and demonstrated that target-specific residual modeling can preserve complementary signal without forcing one global policy across all findings.

### 2. Representation-diversity experiments
Fixed spatial bias and frozen foundation-model transfer were tested under the same discipline and retained as useful negative evidence where they failed.

### 3. Parent-system reconstruction
The research shifted from surrogate systems to the scored parent. Major trained branches were restored with strict state loading, numerical-parity checks, input signatures, content-addressed recovery, and resumability.

### 4. Validation, acquisition, and geometry audits
The project audited historical selection membership, missing acquisitions, and DICOM geometry. The result is deliberately conservative: incomplete-input outputs stay incomplete, and no untouched fully labeled confirmation cohort is invented.

### 5. Anatomy-aware transfer
A pretrained knee anatomy route passed metadata, coordinate, and exact-parent-fallback qualification. The next bounded milestone is real frozen-model reference inference before any anatomy-conditioned disease model is allowed to advance.

## Public reproducibility

The public layer is dependency-light and designed to fail loudly when the published evidence drifts.

Run:

    python -m unittest discover -s tests
    python tools/check_current_frontier.py

GitHub Actions runs the same publication gates on pushes and pull requests. See [Reproducibility](docs/REPRODUCIBILITY.md).

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
- [12 — Owned residual and representation frontier](notebooks/12_owned_residual_and_representation_frontier.ipynb)
- **[13 — Parent reconstruction and anatomy qualification](notebooks/13_parent_reconstruction_and_anatomy_qualification.ipynb)** — current public entry point

## Public repository versus private AWS workspace

**Public**
- aggregate validation and reconstruction evidence
- architecture and research narratives
- promotion/closure decisions
- public-safe helper code and tests
- CI publication gates
- executed aggregate notebooks

**Private by design**
- MRI/DICOM data and reports
- study identifiers and scanner assignments
- row-level OOF/test predictions
- cache shards and memmaps
- model weights/checkpoints
- private source-recovery handles
- cloud paths and credentials
- return bundles and orchestration packages
- exact competition inference/submission implementation

No diagnostic or clinical use is claimed.
