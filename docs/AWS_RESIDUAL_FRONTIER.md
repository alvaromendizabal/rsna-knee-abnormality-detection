# AWS-only residual frontier

## Why the strategy changed

After the scored-reference runtime was recovered and validated on bounded GPU probes, development-time access to the original competition preview inputs was unavailable. Rather than move research back to Kaggle, the project preserved the reference and shifted model development entirely onto the existing AWS research boundary.

The goal is to create **residual candidates** that are useful because they provide complementary signal, not because they look impressive in isolation.

## Canonical data contract

The existing exact-window cache is the source of truth for this research frontier:

- studies: **4,407**;
- size: **69.14 GiB**;
- source resolution: **336 × 336**;
- image tensor layout: **NCHW**;
- grouped non-gold rows: **4,349**;
- gold audit rows: **58**;
- gold optimizer rows: **0**;
- scanner groups: **59**.

The public helper module exposes only the layout/size contracts needed to reproduce the engineering checks. It does not publish study IDs, window-selection logic, row-level predictions, or the private cache.

## Failure-driven hardening

### Stage 68 — source location

The first ResNet34/224 runner assumed the exact-window cache existed as a local filesystem tree. The run stopped before fitting a model. The correction was to treat S3/object storage as canonical and build a bounded local derived cache.

### Stage 69 — tensor layout

The S3 bridge then encountered the canonical tensor shape **(N, 3, H, W)**. The runner had assumed NHWC and stopped before fitting a model.

Stage 70 corrects only that layout assumption. The NCHW tensor is normalized internally by axis order; pixel values are not changed. The scientific experiment remains frozen.

## Stage 70 experiment contract

Stage 70 is prepared to screen a deliberately small **ResNet34 at 224px** on grouped folds **0 and 2**, using fixed epochs and the accepted report-label lineage. It is a candidate-complement experiment for the 0.933 program, not a replacement for the public reference.

The runner is designed to:

- stream canonical source studies from object storage;
- materialize only the bounded 224px derived cache needed for the experiment;
- resume at the study level;
- benchmark local I/O concurrency;
- train fixed-epoch screening folds;
- compare candidate predictions with preserved OOF models for redundancy and complementarity;
- stop on explicit promotion or kill gates.

**Stage 70 has not executed yet.** No candidate metric is published here.

## Semi-reproducible public layer

The repository includes public-safe helpers/tests for:

- public-score gap arithmetic;
- canonical NCHW/NHWC layout detection;
- canonical shape normalization;
- theoretical uint8 derived-cache sizing;
- Stage 67–70 state assertions;
- persisted Notebook 10 outputs and privacy scans.

Private sampling schedules, checkpoints, cache shards, row-level predictions, and competition-specific inference glue remain outside Git history.
