# RSNA Knee Abnormality Detection

**MRI image-model research with leakage-aware validation, multi-branch parent reconstruction, anatomy-aware representation learning, and production-style ML engineering on AWS.**

A notebook-first machine-learning project by **Alvaro Mendizabal** for twelve knee-MRI findings. AWS/SageMaker is the canonical private research environment; this repository is the curated employer-facing layer. Raw MRI, identifiers, row-level predictions, private checkpoints, recovery bundles, and competition-specific inference glue stay outside Git history.

> **Latest verified publication boundary: AWS research through Stage 91 asset recovery.** The project has a verified public score of **0.943 macro ROC-AUC**, a fully grouped internal validation program, reconstructed execution paths for the major parent-model branches, and a new anatomy-aware research program derived from prior high-performing medical-imaging systems.

## Start here

1. **[Project status](docs/PROJECT_STATUS.md)** — current verified state and research decisions.
2. **[Parent reconstruction frontier](docs/PARENT_RECONSTRUCTION_FRONTIER.md)** — how the scored multi-branch system was restored and validated without publishing private weights.
3. **[Anatomy-aware transfer program](docs/ANATOMY_AWARE_TRANSFER_PROGRAM.md)** — the next research direction, grounded in recurring localization and visibility mechanisms from strong medical-imaging systems.
4. **[AWS research frontier](docs/AWS_RESIDUAL_FRONTIER.md)** — grouped validation, residual modeling, negative-result discipline, and the AWS-only execution boundary.

## Current verified evidence

| Evidence boundary | Verified state |
|---|---:|
| Public macro ROC-AUC | **0.943** |
| Canonical exact-window cache | **4,407 studies / 69.14 GiB** |
| Grouped research rows | **4,349 non-gold / 58 audit-only gold** |
| Scanner groups | **59; zero cross-fold leakage** |
| Native parent branch | **20 trained members / 200 window evaluations restored** |
| A5 parent branch | **5/5 trained folds restored** |
| Rad parent branch | **3 original layouts / multiple trained heads restored** |
| Private model/source recovery | **~2.97 GB preserved in encrypted S3 objects** |
| Current scientific frontier | **anatomy-localized global/local fusion + visibility-aware supervision** |

Internal grouped metrics are model-selection evidence and are not presented as interchangeable with the public score.

## What this project demonstrates

- **End-to-end ML ownership:** data contracts, preprocessing, validation, training, inference, checkpoint lineage, cost controls, diagnostics, and publication boundaries are treated as one system.
- **Leakage-aware evaluation:** scanner-grouped folds, audit-only rows, exact metric contracts, and explicit separation between development and external evaluation.
- **Multi-branch model reconstruction:** trained DINO, RadImageNet, A5, Raptor, and CoAt-family components are audited as parts of a scored parent rather than treated as disconnected experiments.
- **Representation and ensemble research:** specialist residuals, heterogeneous image encoders, medical pretraining, multi-plane aggregation, and complementary feature families are tested under matched controls.
- **Failure-driven engineering:** dependency, tensor-layout, disk-budget, authentication, cloud-permission, and numerical-equivalence failures are converted into deterministic regression tests.
- **Scientific negative results:** well-executed ideas are closed when evidence is weak instead of being rescued with post-hoc tuning.
- **Domain-aware frontier research:** prior medical-imaging solution patterns are translated into knee-specific localization, visibility, and local/global fusion hypotheses instead of copied mechanically.
- **Cost-aware GPU execution:** large checkpoints are streamed, expensive work is resumable, and bounded runs preserve completed computation.
- **Semi-reproducible publication:** aggregate evidence, decision logic, public helpers, and engineering contracts are visible while competition-sensitive implementation remains private.

## Research progression

### 1. Validation and residual modeling
The project established a canonical grouped validation boundary and used target-specific residual modeling to identify complementary signal instead of applying one global policy across all findings.

### 2. Representation-diversity experiments
Several image-representation families were screened under the same validation discipline. Fixed spatial attention and frozen foundation-model transfer were retained as useful negative evidence where they failed to improve the matched research reference.

### 3. Parent-system reconstruction
The research then shifted from building surrogate systems to reconstructing the actual scored parent. Major trained branches were restored with strict state loading, numerical-parity checks, signature-aware caching, and private artifact recovery.

### 4. Anatomy-aware transfer
The current frontier focuses on a recurring pattern across strong medical-imaging systems: **explicit localization, structure visibility, local/global evidence fusion, and uncertainty over plausible regions**. The goal is to add genuinely new spatial supervision to a parent that already has strong attention, medical pretraining, multi-plane context, and ensembling.

## Engineering principles

- AWS is the source of truth for computation and artifacts.
- GitHub receives only validated, public-safe milestones.
- Raw data and large/private model assets remain outside Git.
- Completed stages are resumed, not recomputed.
- Every avoidable failure becomes a regression test before the next expensive run.
- Promotion decisions are tied to a declared metric/evaluation setting.
- A small valid positive result is retained as evidence even when it is not yet sufficient for promotion.
- Partial-input predictions are never relabeled as complete-parent outputs.

## Notebook guide

The existing notebooks preserve the project’s historical research progression:

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

The latest post-Stage-80 evidence is summarized in the public docs above rather than publishing private recovery runners, source handles, model weights, or row-level outputs.

## Public repository versus private AWS workspace

**Public:**
- aggregate validation evidence
- architecture/research narratives
- promotion and closure decisions
- public-safe helper code
- unit tests and publication checks
- executed historical notebooks

**Private by design:**
- MRI/DICOM data and reports
- study identifiers and scanner assignments
- row-level OOF/test predictions
- cache shards and memmaps
- model weights/checkpoints
- private source-recovery handles
- cloud paths and credentials
- return bundles and orchestration packages
- exact competition inference/submission implementation

## Public checks

Run the aggregate test suite:

`python -m unittest discover -s tests`

Run the publication gate:

`python tools/check_current_frontier.py`

No diagnostic or clinical use is claimed.
