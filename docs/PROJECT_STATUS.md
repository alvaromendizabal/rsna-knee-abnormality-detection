# Project status

Updated from verified returned evidence through **Stage 69 · 2026-09-29 UTC**. **Stage 70 is prepared but not yet executed.**

## Current boundary

The historically best scored system remains the **0.933 public reference**. A user-supplied September 29 leaderboard screenshot shows **0.961** at the top, giving a public-score gap of **0.028**.

No Stage 64–70 result is presented as an accuracy improvement. The work since Stage 63 has clarified the deployment boundary, closed an inappropriate development-time data-access path, and hardened the AWS-only residual-model pipeline.

## Preserved reference-runtime evidence

The Stage-63 reference result remains valid and preserved:

- **32 / 32** GPU checkpoint checks passed;
- **20** stored native fingerprints checked where available;
- controlled trained-head optimization preserved exact final output;
- median **1.2738× head-only speed ratio** on the bounded benchmark;
- complete real-image historical reference replay remains unproven.

The 0.933 reference remains the mandatory scored control for future public-score claims.

## Stages 64–67 — reference preview path closed during development

The project attempted to turn the recovered reference into a real-image regression check. The important outcomes were engineering and process decisions, not model results.

- Stage 65 stopped during packaged tests before inference.
- Stage 66 repaired reader dependencies but exposed an import-shadowing issue in the live Python environment.
- Stage 67 passed **284 self-tests**, reused the recovered reference assets, and reached the first competition-data request.
- That request was denied; **0 bytes** of competition preview data were downloaded and **0 model fits** ran.

Because AWS is canonical and Kaggle is reserved for the submission boundary, the development-time preview-acquisition path is now closed rather than repeatedly retried.

## Stages 68–70 — AWS-only residual-model transition

The next strategy is to produce a small, efficient candidate branch whose purpose is **complementarity with the 0.933 program**, while keeping validation leakage-aware.

### Stage 68

Prepared a ResNet34/224 screen on scanner-grouped folds. It failed before training because the runner assumed the exact-window cache was a local filesystem tree. The canonical cache is in object storage.

- model fits: **0**;
- failure class: **SOURCE_STATE**;
- scientific hypothesis: **not evaluated**.

### Stage 69

Added an S3-derived-cache bridge. It failed during the first cache pilot because the canonical image array is stored as **NCHW**, while the runner assumed NHWC.

- model fits: **0**;
- failure class: **SCHEMA**;
- scientific hypothesis: **not evaluated**.

### Stage 70

Prepared a source-layout recovery that accepts the canonical **(N, 3, H, W)** contract and normalizes it internally without changing pixel values. The scientific screen remains frozen: ResNet34, 224px, folds 0 and 2, fixed epochs, accepted report labels, zero gold optimizer rows.

**Stage 70 has not run yet.** No candidate AUC, complementarity gain, or submission claim exists.

## Canonical AWS research boundary

- exact-window cache: **4,407 studies / 69.14 GiB**;
- cache tensor layout: **NCHW**;
- grouped non-gold rows: **4,349**;
- gold audit rows: **58**;
- scanner groups: **59**;
- gold optimizer rows: **0**.

The public repository exposes these contracts and aggregate decisions, not identifiers, cache shards, row-level predictions, or weights.

## Current deployment and modeling gates

Completed:

- scored-reference asset/runtime recovery;
- bounded GPU reference checkpoint validation;
- scanner-grouped research folds;
- accepted report-label lineage;
- AWS-only residual-model protocol;
- canonical cache location/layout hardening.

Open:

1. execute Stage 70 and obtain the first actual small-CNN screening result;
2. confirm only if the frozen screen passes its complementarity gates;
3. compare preserved MCL/Lateral and MaxViT components only under reference-aware, leakage-safe logic;
4. freeze one materially distinct candidate;
5. validate complete AWS inference/schema/lineage/runtime;
6. enter Kaggle only at the actual submission boundary.

See [AWS residual frontier](AWS_RESIDUAL_FRONTIER.md), [Scored-reference frontier](SCORED_REFERENCE_FRONTIER.md), and [Notebook 10](../notebooks/10_aws_only_residual_frontier.ipynb).
