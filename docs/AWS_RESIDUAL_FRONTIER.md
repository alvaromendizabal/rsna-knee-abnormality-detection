# AWS research frontier

## Research boundary

AWS/SageMaker is the canonical environment for:

- MRI data and cache management;
- feature extraction;
- model training and inference;
- grouped OOF validation;
- checkpointing and artifact lineage;
- diagnostics and profiling;
- executed notebooks;
- experiment state and return bundles.

GitHub is the curated public engineering layer. Private MRI, identifiers, row-level predictions, checkpoints, recovery handles, cloud paths, and competition-specific inference remain outside Git history.

## Canonical validation contract

The established research boundary includes:

- **4,407 studies** in the canonical exact-window cache;
- **69.14 GiB** cache size;
- **4,349 grouped non-gold rows**;
- **58 audit-only rows**;
- **59 scanner groups**;
- fold sizes **870 / 870 / 870 / 870 / 869**;
- **zero scanner groups crossing folds**;
- **zero audit-only rows used by the optimizer**.

The grouped research score is a development metric. It is not presented as interchangeable with the external public score.

## Complementary residual modeling

The project moved away from one global ensemble policy and toward **target-specific complementary signal**.

A narrow residual path was independently confirmed on the grouped boundary and later extended into a retained positive challenger.

The public lesson is methodological rather than implementation-specific:

- identify residual headroom by finding;
- require matched controls;
- protect unaffected targets;
- confirm on held-out development folds;
- retain valid small aggregate gains as evidence;
- use uncertainty and provenance for promotion decisions.

Exact blend weights, row-level predictions, and private checkpoint identities remain private.

## Representation-diversity program

### Fixed spatial branch
A dense spatial branch completed successfully but did not improve the aggregate grouped result.

Decision: **scientific negative; close the tested configuration**.

This is useful evidence because it separates generic spatial bias from the stronger hypothesis of supervised anatomical localization.

### Frozen orthopedic foundation-model route
A musculoskeletal foundation model was integrated with complete checkpoint coverage, GPU throughput checks, resumable feature caching, and matched screening.

The tested frozen feature-transfer route was a scientific negative.

Decision: **close the frozen-transfer configuration** rather than micro-tune it after observing the result.

### Task-trained paired image models
A matched task-trained pair completed as a valid research execution. The project then shifted back to the scored parent rather than continuing to optimize a surrogate system.

## Parent-first strategy

The central strategy is now:

> **freeze the verified parent as the control, reconstruct its trained branches faithfully, and introduce one new capability at a time.**

This makes attribution stronger and keeps the research tied to the system that actually produced the verified public result.

The reconstructed parent currently includes validated execution paths for:

- native multi-member DINO inference;
- RadImageNet-family heads and layouts;
- all five A5 folds;
- recovered Raptor checkpoints;
- recovered CoAt-family trained assets;
- fitted numerical fusion/calibration logic.

Full parent parity still depends on complete compatible inputs and remaining branch execution.

## Input signatures and resumability

Recent recovery work uncovered incomplete raw-acquisition coverage in the mirrored diagnostic population.

The implementation therefore treats the input signature as part of model identity.

Rules:

- completed compatible outputs are reused;
- missing acquisitions are never fabricated;
- partial-input outputs are labeled as partial;
- if recovered acquisitions change selected pixels, affected branches are recomputed;
- unaffected components remain reusable;
- checkpoints and large assets stream through bounded storage paths rather than being copied indiscriminately to Studio disk.

## Failure-driven engineering

Recent stages hardened the pipeline around real failure modes:

- isolated image-library dependencies;
- immutable numerical-parity checks;
- pandas copy-on-write behavior;
- free-space budgeting with safety reserves;
- deterministic checkpoint/fingerprint validation;
- resumable multi-stage execution;
- cached OAuth and browser-session handling;
- sanitized access diagnostics;
- private S3 destination verification;
- manifest-role classification;
- exact distinction between source inputs and generated outputs.

Each avoidable failure became a regression test before the next cost-bearing run.

## Current scientific frontier

The strongest new capability identified by the broader medical-imaging review is **supervised anatomy-aware evidence routing**.

The next work focuses on:

- explicit localization or structure-aware region pooling;
- local evidence combined with global context;
- visibility-aware auxiliary objectives;
- multi-plane anatomical consistency;
- multiple plausible localization hypotheses.

This direction complements the parent’s existing attention, medical pretraining, depth/position encoding, multi-plane fusion, and model diversity instead of duplicating them.

See [Anatomy-aware transfer program](ANATOMY_AWARE_TRANSFER_PROGRAM.md).

## Publication philosophy

This repository is intentionally semi-reproducible.

Public:
- aggregate metrics and validation contracts;
- architecture narratives;
- experiment decisions;
- public-safe helper functions and tests;
- notebook history;
- failure-mode and reproducibility practices.

Private:
- raw clinical/competition data;
- identifiers;
- row-level predictions;
- exact checkpoints and weights;
- private source handles;
- orchestration packages and return bundles;
- exact competition inference/submission implementation.
