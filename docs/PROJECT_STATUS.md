# Project status

Updated from verified aggregate AWS evidence through **Stage 91 asset recovery · 2026-10-03 UTC**.

## Current boundary

The strongest verified public result is **0.943 macro ROC-AUC** across twelve knee-MRI targets.

The current research program is no longer centered on building replacement systems around the internal weak-label OOF reference. The scored multi-branch parent is now the control, and new work is evaluated as a controlled addition to that system.

Internal grouped metrics remain model-selection evidence and are **not directly interchangeable** with the public score.

## Validation contract

The established research boundary includes:

- canonical exact-window cache: **4,407 studies / 69.14 GiB**;
- grouped non-gold rows: **4,349**;
- audit-only gold rows: **58**;
- scanner groups: **59**;
- fold sizes: **870 / 870 / 870 / 870 / 869**;
- scanner groups crossing folds: **0**;
- gold optimizer rows: **0**.

A later source audit showed that some recovered parent-model components used the gold subset during historical checkpoint selection. Those rows are therefore not treated as untouched confirmation for those components.

## Target-specific residual program

The research program established that narrow, target-specific residual modeling can add complementary signal without forcing one blend policy across every finding.

A later consolidated complement remained a **positive development challenger** on the grouped research boundary. It is retained as evidence rather than discarded solely because one fold moved slightly negative.

This changed the project’s promotion discipline:

- valid positive aggregate movement is retained;
- fold dispersion is inspected rather than converted into an automatic veto;
- paired evidence and uncertainty determine promotion;
- correctness or leakage failures invalidate a result regardless of score.

Exact private blend implementation, row-level predictions, and model identities remain outside the public repository.

## Representation-diversity results

### Dense spatial attention
A fixed dense spatial/anatomy branch executed successfully and produced a negative aggregate result. It was closed at screening.

**Conclusion:** fixed generic regions were not a strong enough mechanism. This result does not reject supervised anatomical localization.

### Orthopedic foundation-model transfer
A frozen musculoskeletal foundation-model feature route was implemented with complete checkpoint coverage and benchmarked on the project GPU.

The resulting feature-transfer experiment was a valid scientific negative and was closed without post-hoc rescue tuning.

**Conclusion:** domain pretraining alone was insufficient in the tested frozen-transfer configuration. The result strengthened the case for task-aligned spatial supervision instead of another frozen embedding path.

### Task-trained paired image models
A matched pair of task-trained spatial models completed successfully as an engineering/scientific experiment. The project subsequently moved away from replacement-model iteration and back to the actual scored parent.

## Parent reconstruction

The most important engineering progress since the prior publication is the restoration of the parent system’s major trained branches.

### Rad branch
The original trained RadImageNet-family execution path was restored across **three source layouts** with multiple trained heads. Serial and optimized batching paths passed numerical-parity checks.

### Native DINO branch
The native branch restored:

- **20 trained members**;
- **200 member/window evaluations**;
- original parent preprocessing/inference behavior;
- signature-aware caching and strict fingerprint checks.

### A5 branch
All **5/5 trained A5 folds** were restored with strict state loading and bounded numerical-parity checks.

### Raptor / CoAt recovery
Stage 91 recovered the three Raptor checkpoints and the principal trained assets for three CoAt-family branches into encrypted private S3 storage.

About **2.97 GB** of source/model assets were preserved without placing large private binaries in Git history.

Remaining gaps include:

- unresolved source provenance for one repair-family branch;
- denied access to missing raw acquisitions;
- real Raptor execution under complete-input signatures;
- reviewed CoAt execution;
- complete-parent integration on a legitimate aligned evaluation population.

## Input-signature discipline

A raw-data coverage audit found that the currently mirrored diagnostic population is incomplete.

The project therefore enforces a strict rule:

> partial-input predictions remain partial-input predictions.

If later recovery changes selected source pixels, only affected branches are recomputed under a new signature. Existing unaffected outputs remain reusable.

This avoids silently mixing incompatible parent states.

## Anatomy-aware research frontier

A cross-competition review of strong prior medical-imaging systems identified a recurring capability that is not yet established in the parent:

**explicit anatomical localization and visibility-aware local/global evidence fusion.**

The immediate research program prioritizes:

1. anatomy-localized residual evidence attached to the existing parent;
2. visibility-aware auxiliary supervision;
3. cross-plane localization consistency and multiple plausible region hypotheses.

The parent already contains strong attention, medical pretraining, multi-plane context, multi-resolution paths, and ensemble diversity. The next step is therefore **not** another generic attention block or backbone swap.

See [Anatomy-aware transfer program](ANATOMY_AWARE_TRANSFER_PROGRAM.md).

## Failure-driven engineering

Recent stages converted several operational failures into reusable safeguards, including:

- external dependency isolation;
- pandas copy-on-write compatibility;
- disk-budget accounting;
- resumable checkpoint streaming;
- exact input signatures;
- OAuth/session handling;
- cloud permission diagnostics;
- manifest-role validation;
- public/private artifact boundaries.

Completed work is reused rather than recomputed when a later stage fails.

## Current next step

1. resume the existing Stage 91 recovery state without repeating preserved downloads;
2. complete useful Raptor execution under clearly labeled input scope;
3. review and execute recovered CoAt-family runtime paths;
4. assemble the complete parent under compatible input signatures;
5. establish a legitimate aligned comparison population;
6. begin the controlled anatomy-aware additions.

No public improvement is claimed from asset recovery or engineering parity alone.

See:

- [Parent reconstruction frontier](PARENT_RECONSTRUCTION_FRONTIER.md)
- [Anatomy-aware transfer program](ANATOMY_AWARE_TRANSFER_PROGRAM.md)
- [AWS research frontier](AWS_RESIDUAL_FRONTIER.md)
