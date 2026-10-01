# AWS-only residual frontier

## Why this frontier exists

After the historically scored reference was recovered and validated on bounded GPU probes, development-time access to the original competition preview inputs was unavailable. Rather than move research back to Kaggle, the project preserved the reference and shifted model development entirely onto the existing AWS research boundary.

The goal is to create **residual candidates** that contribute complementary signal to a stronger parent while preserving leakage-aware validation.

## Canonical data contract

The existing exact-window cache is the source of truth:

- studies: **4,407**;
- size: **69.14 GiB**;
- source resolution: **336 × 336**;
- image tensor layout: **NCHW**;
- grouped non-gold rows: **4,349**;
- gold audit rows: **58**;
- gold optimizer rows: **0**;
- scanner groups: **59**.

The public helper module exposes only layout, size, and aggregate confirmation contracts. It does not publish study IDs, window-selection logic, row-level predictions, or the private cache.

## Failure-driven hardening

### Stage 68 — source location

The first ResNet34/224 runner assumed the exact-window cache existed as a local filesystem tree. The run stopped before fitting. The correction was to treat object storage as canonical and build a bounded local derived cache.

### Stage 69 — tensor layout

The bridge encountered the canonical tensor shape **(N, 3, H, W)**. The runner had assumed NHWC and stopped before fitting.

Both failures are preserved as regression cases.

## Stage 70 — frozen residual screen

Stage 70 executed a deliberately small **ResNet34 at 224px** on grouped folds **0 and 2** with fixed epochs, accepted report-label lineage, and zero gold optimizer rows.

Aggregate screen:

- candidate mean fold macro-AUC: **0.766232**;
- grouped control mean: **0.787827**;
- fixed 10% blend mean: **0.789156**;
- mean blend delta: **+0.001329**;
- bootstrap positive fraction: **0.9633**;
- median Spearman correlation: **0.8177**;
- worst aggregate target delta: **-0.002620**.

The frozen screen passed its preregistered gates and advanced unchanged to confirmation.

## Stage 71 — untouched confirmation folds

The same configuration ran on folds **1, 3, and 4**.

Aggregate confirmation:

- candidate mean fold macro-AUC: **0.772648**;
- grouped control mean: **0.797936**;
- fixed blend mean: **0.800373**;
- mean blend delta: **+0.002437**;
- fold deltas: **+0.002300, -0.000085, +0.005097**;
- bootstrap positive fraction: **1.000**;
- median Spearman correlation: **0.6981**;
- worst aggregate target delta: **-0.001501**.

Five of six gates passed. The failed gate was **all confirmation folds nonnegative**. The branch is therefore closed as a scientific negative result despite a positive aggregate mean.

That distinction matters: the project does not weaken a preregistered decision rule after seeing the result.

## Stage 72 — submission engineering

Once Stage 71 closed, the project moved to the actual competition-submission boundary. The engineering work focused on authentication, version-pinned code-competition submission semantics, duplicate prevention, resume behavior, and preserving the distinction between public controls and user-owned contributions.

**No new official score is claimed in this repository yet.**

## Semi-reproducible public layer

The repository includes public-safe helpers/tests for:

- public-score gap arithmetic;
- canonical NCHW/NHWC layout detection;
- canonical shape normalization;
- theoretical uint8 cache sizing;
- preregistered confirmation-gate evaluation from aggregate metrics;
- Stage 70 screen and Stage 71 confirmation state assertions;
- executed Notebook 11 outputs and privacy scans.

Private sampling schedules, checkpoints, cache shards, row-level predictions, target-level private diagnostics, credentials, return bundles, PYZ runners, and competition-specific inference glue remain outside Git history.
