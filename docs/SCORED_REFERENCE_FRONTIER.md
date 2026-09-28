# Scored-reference frontier

## Objective

The current deployment and improvement program is anchored to the historically best scored RSNA system in this project: a **0.933 public macro-ROC-AUC multi-branch reference**. The historical leader in the last recorded comparable leaderboard context is **0.958**.

The purpose of the reference-recovery program is not to publish private competition assets. It is to make the strongest scored system auditable, testable, restartable, and fast enough to serve as the control for new experiments.

## Architecture boundary

The private reference combines multiple MRI representation families rather than a single network. The public repository intentionally summarizes these only at a high level:

- transformer-based MRI members;
- an additional multi-fold image family;
- a RadImageNet-based branch with calibration;
- a convolutional/attention-based Raptor branch;
- final rank-based aggregation.

Exact private checkpoints, source-specific paths, calibration assets, and proprietary competition glue remain outside Git history.

## Recovery milestones

### Source and provenance

The reference source and historical score receipts were recovered first, making it possible to distinguish the 0.933 stack from the weaker owned branch and to identify its model-resource families without executing unsafe fallbacks.

### Asset assembly and CPU audit

The assembled snapshot contains **36 selected asset paths** and **32 weight files**, totaling about **3.28 GB**. CPU-side restricted-loading checks verified checkpoint structure and tensor sanity without changing the model weights.

### GPU runtime isolation

The recovered reference requires a newer model registry than the installed environment provides. Instead of upgrading the canonical environment or hot-reloading incompatible packages inside one process, the GPU continuation selects a pinned runtime in isolation.

Stage 63 then passed **32 / 32 GPU checkpoint checks** and checked **20 stored native fingerprints** where available.

This establishes loader/runtime readiness for the assembled snapshot. It does not prove that every historical scored-run byte has been recovered, and it does not yet reproduce the full calibrated reference on real MRI inputs.

## Runtime optimization evidence

A source-derived optimization removes five diagnostic-only head-prediction calls in the RadImageNet stage while retaining the heads that contribute to final predictions.

- original head calls: **20**;
- candidate head calls: **15**;
- trained heads loaded: **15**;
- measured GPU trials: **3**;
- exact final values and CSV bytes: **yes, all trials**;
- median head-only speed ratio: **1.2738×**;
- real-image feature parity: **not yet verified**;
- end-to-end notebook speedup: **not yet verified**;
- activated in the incumbent: **no**.

This is a correctness-gated optimization candidate, not a production-speed claim.

## Reusing earlier model research

Earlier work is retained as candidate evidence rather than discarded:

- the independently confirmed MCL and Lateral Meniscus experts remain potential residual additions;
- the MaxViT branch remains a potential heterogeneous residual complement;
- denser anatomical coverage is being transferred as a controlled change to the original reference’s Raptor branch;
- the existing ranking, checkpoint, resume, and protected-target tests are reused.

Old blend weights are **not** copied onto the 0.933 reference. They were selected against another baseline and require new reference-level evidence.

## Next reproducibility gate

Stage 64 is prepared to replay the complete reference on the original visible MRI preview cases. Acceptance requires numerical reproduction of the saved control before candidate outputs are interpreted.

The preview cohort is a deployment regression gate, not an accuracy benchmark. It cannot establish an AUC improvement or justify a leaderboard claim.

## Public reproducibility boundary

This repository makes the following aspects reproducible with aggregate/synthetic evidence:

- score-boundary arithmetic;
- recovery/readiness counts;
- head-call reduction and timing calculations;
- quality checks for persisted notebooks and public artifacts;
- privacy scans and source-code syntax checks.

It deliberately does **not** publish the private checkpoint files, patient data, row-level predictions, exact private assembly paths, or enough competition-specific source to clone the full submission stack verbatim.
