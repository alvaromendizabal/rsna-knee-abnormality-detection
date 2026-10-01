# Project status

Updated from verified returned evidence through **Stage 72 · 2026-10-01 UTC**.

## Current boundary

The historically best scored system remains the **0.933 public reference**. A user-supplied September 29 leaderboard screenshot shows **0.961** at the top, giving a public-score gap of **0.028**.

Stages 70–71 are internal grouped model-selection evidence, not substitutes for the public score. Stage 72 is submission-boundary engineering; no new leaderboard result is claimed until Kaggle returns one.

## Preserved reference-runtime evidence

The Stage-63 reference result remains valid and preserved:

- **32 / 32** GPU checkpoint checks passed;
- **20** stored native fingerprints checked where available;
- controlled trained-head optimization preserved exact final output;
- median **1.2738× head-only speed ratio** on the bounded benchmark;
- complete historical binary identity remains unproven.

The 0.933 reference remains the mandatory scored control for public-score claims.

## Stages 64–69 — development boundary and failure-driven hardening

The reference-preview path was closed during development after source access was unavailable in AWS. The project then moved entirely onto the private AWS cache/fold boundary.

- Stage 67 passed **284 self-tests** and reached the competition-data boundary, then stopped without downloading competition preview data.
- Stage 68 stopped before fitting because the cache location assumption was wrong.
- Stage 69 stopped before fitting because the canonical cache tensor layout was **NCHW**, not NHWC.

Those failures became regression gates rather than ad-hoc patches.

## Stage 70 — residual screen passed

Stage 70 executed the frozen ResNet34/224 screen on grouped folds 0 and 2.

Aggregate result:

- candidate mean fold macro-AUC: **0.766232**;
- grouped control mean: **0.787827**;
- fixed blend mean: **0.789156**;
- fixed blend delta: **+0.001329**;
- paired bootstrap positive fraction: **0.9633**;
- median Spearman correlation: **0.8177**;
- worst aggregate target delta: **-0.002620**.

All frozen screening gates passed, so the exact configuration advanced to untouched confirmation folds 1, 3, and 4.

## Stage 71 — independent confirmation completed

Stage 71 completed the same frozen configuration on folds 1, 3, and 4.

Aggregate result:

- candidate mean fold macro-AUC: **0.772648**;
- grouped control mean: **0.797936**;
- fixed blend mean: **0.800373**;
- mean fixed-blend delta: **+0.002437**;
- fold deltas: **+0.002300, -0.000085, +0.005097**;
- paired bootstrap positive fraction: **1.000**;
- median Spearman correlation: **0.6981**;
- worst aggregate target delta: **-0.001501**.

Five of six confirmation gates passed. The preregistered rule required **every confirmation fold to be nonnegative**. Fold 3 missed that requirement by roughly 8.5e-5, so the ResNet34 branch was **not promoted**.

This is treated as a valid scientific negative result: the aggregate signal is interesting, but the frozen promotion contract takes precedence over post-hoc interpretation.

## Stage 72 — submission boundary

Stage 72 moved from research into submission engineering.

The work hardened:

- Kaggle CLI discovery/bootstrap;
- OAuth authentication;
- duplicate-submission checks;
- code-competition kernel/version submission semantics;
- bounded polling and resume behavior;
- explicit separation between an external public control and user-owned model contributions.

At the time of this publication, **no new Stage-72 official score has been produced**. The 0.933 scored reference remains the official best.

## Canonical AWS research boundary

- exact-window cache: **4,407 studies / 69.14 GiB**;
- cache tensor layout: **NCHW**;
- grouped non-gold rows: **4,349**;
- gold audit rows: **58**;
- scanner groups: **59**;
- gold optimizer rows: **0**.

The public repository exposes contracts, aggregate evidence, and decision logic—not identifiers, cache shards, row-level predictions, private sampling schedules, weights, or submission glue.

## Current next step

1. obtain a fresh official Kaggle score from the hardened submission boundary;
2. keep the 0.933 control unchanged unless the official result improves it;
3. prioritize already-confirmed target-specific residual evidence before starting another broad architecture search;
4. continue to require leakage-safe grouped evidence before promoting new components.

See [AWS residual frontier](AWS_RESIDUAL_FRONTIER.md), [Scored-reference frontier](SCORED_REFERENCE_FRONTIER.md), and [Notebook 11](../notebooks/11_residual_confirmation_and_submission_boundary.ipynb).
