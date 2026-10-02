# AWS-only residual and representation frontier

## Why the strategy evolved

The project began with scored-reference recovery and broad residual screening. As the validation system matured, the research strategy shifted toward **complementary target-specific signal** and then toward **representation diversity**.

AWS/SageMaker remains the canonical environment for:

- data and cache management;
- feature extraction;
- training;
- grouped OOF validation;
- checkpointing;
- experiment state;
- diagnostics;
- executed notebooks.

The external competition platform is not a development environment. It is reserved for a final score-producing submission.

## Canonical data contract

- studies: **4,407**;
- cache size: **69.14 GiB**;
- source resolution: **336 × 336**;
- tensor layout: **NCHW**;
- grouped non-gold rows: **4,349**;
- gold audit rows: **58**;
- gold optimizer rows: **0**;
- scanner groups: **59**;
- fold sizes: **870 / 870 / 870 / 870 / 869**;
- cross-fold scanner leakage: **0**.

The public layer exposes aggregate contracts only. It does not publish study IDs, cache shards, row-level predictions, sampling schedules, checkpoints, or private inference glue.

## Confirmed target-specific residual

The most important progress since the previous publication is the independent confirmation of a narrow target-specific residual.

Five-fold aggregate OOF:

- baseline: **0.791208**;
- promoted blend: **0.793686**;
- gain: **+0.002479**.

Target-specific evidence:

- MCL: **+0.012874**;
- Lateral Meniscus: **+0.016871**;
- the remaining ten targets were protected exactly.

Every fold was positive. The component was promoted without relaxing the frozen gate.

The public repository intentionally omits its private checkpoint identities and exact blend implementation.

## Stable public control

The project's current official public-score incumbent is **0.943 macro ROC-AUC**.

A user-supplied October 1 leaderboard snapshot shows a **0.961** leader, leaving a **0.018** public gap.

The exact current public control source was recovered into AWS and pinned privately. That lets the project keep a stable score reference while all scientific iteration stays on the grouped AWS validation system.

## Closed delivery-workflow detour

Several stages tested score-delivery mechanics. They exposed brittle external orchestration and were closed without claiming a new score.

The resulting policy is intentionally strict:

> complete the model on AWS first; use the score platform only for a final frozen submission.

This prevents paid AWS instances from idling while debugging remote notebook state and keeps the scientific boundary auditable.

## Dense anatomy experiment

A later branch tested whether spatially localized dense features would add complementary signal.

The branch executed successfully under the grouped screen:

- baseline: **0.787494**;
- candidate: **0.786693**;
- delta: **−0.000801**;
- bootstrap probability of positive improvement: **7.5%**.

One target improved materially, but several others regressed enough that the aggregate branch did not justify confirmation.

Decision: **scientific negative; close at screening**.

The project does not weaken gates or add post-hoc tuning to rescue a branch after seeing the result.

## Current representation-diversity frontier

The next frontier is a frozen dense self-supervised representation plus a compact distillation head.

The public design contract is deliberately broad:

- frozen pretrained feature extractor;
- dense local feature aggregation;
- compact student/distillation bottleneck;
- target-specific multi-plane prediction head;
- fold 0/2 cross-fit screening;
- residual/prediction correlation diagnostics;
- untouched confirmation only if screening passes;
- resumable feature cache.

At this publication boundary the branch is **prepared, not executed**.

## Semi-reproducible public layer

Public artifacts include:

- aggregate score state;
- validation/fold contracts;
- promotion/closure decisions;
- executed Notebook 12;
- public helper functions;
- unit tests;
- privacy scans.

Private artifacts include:

- raw MRI and reports;
- identifiers and scanner assignments;
- row-level predictions;
- model weights;
- cache shards and memmaps;
- private runners/returns;
- competition-specific inference and submission implementation.
