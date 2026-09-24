# Training frontier

## Why the frontier moved again

Stage 32 identified incomplete training-data coverage as the highest-value blocker. Stage 33 closed that blocker: the exact-window cache now covers all **4,407 training studies**, and the project has a frozen five-fold scanner-group contract with **59 scanner groups**, **4,349 non-gold optimization rows**, and **58 expert audit-only rows**.

Stage 34 then showed that the existing DINO branch can still improve under matched continuation training, but only modestly: grouped macro-AUC increased from **0.760266** at epoch 2 to **0.763762** at epoch 3. A supervision-consistency weighting hypothesis scored **0.762969** and was stopped.

Stage 36 supplied the most important external calibration: the independently trained epoch-3 DINO system scored **0.820 public AUC**. That result is far below the reproduced **0.933** multi-model reference, so small continuation gains alone are not a credible route to the top of the leaderboard.

## Current best and gap

**Current scored incumbent:** reproduced public reference ensemble, **0.933 public macro-ROC-AUC**.

**Returned leaderboard leader:** **0.958** on the same dated leaderboard context.

**Comparable gap:** **0.025**.

**Independent DINOv2 code submission:** **0.820** (`56507693`). It is a useful measurement of the independently trained branch, not an improvement over the incumbent.

## Data and validation readiness

| Capability | Verified state |
|---|---|
| Exact-window cache | **4,407 / 4,407 studies, 14 / 14 shards** |
| Cache size | **69.14 GiB** |
| Unexpected decode failures | **0** |
| Scanner groups | **59** |
| Grouped folds | **5** |
| Fold sizes | **870 / 870 / 870 / 870 / 869** |
| Non-gold optimization rows | **4,349** |
| Expert audit-only rows | **58** |
| Gold optimizer rows | **0** |
| Scanner-group leakage | **0 groups crossing folds** |

This is now a data-complete training program. The remaining gap is model quality and OOF evidence, not missing cache coverage.

## Ranked research backlog

The backlog is ordered by expected information and score value, not convenience:

| Rank | Capability | Current state | Priority |
|---:|---|---|---:|
| 1 | Cache-vs-direct model-logit equivalence | Required before cache-backed five-fold training | 9.8 |
| 2 | Trainable-depth capacity decision | Last-4 versus last-6 DINO blocks; no public result claimed yet | 9.5 |
| 3 | Scanner-grouped five-fold OOF baseline | Data/folds ready; fold-complete training not yet finished | 9.5 |
| 4 | Geometry and slice-selection upgrade | Next structural family if capacity change is insufficient | 9.0 |
| 5 | Target-specific spatial / ROI modeling | Not yet implemented for weak target families | 8.3 |
| 6 | OOF heterogeneous ensemble | Deferred until fold-complete predictions exist | 8.1 |

## Promotion logic

1. Require cached-versus-direct numerical equivalence before training from cached tensors at scale.
2. Keep single-variable capacity tests matched to the existing grouped fold and promote only material gains.
3. Train all five scanner-group folds once the representation contract is cleared.
4. Save fold-complete OOF predictions for every promoted model family.
5. Compare geometry, slice-selection, ROI, and supervision changes against the same grouped OOF boundary.
6. Learn ensemble weights only from OOF predictions; do not reuse exposed development cohorts as an optimization target.
7. Treat the 0.933 and 0.958 public scores as leaderboard evidence, not as interchangeable with local grouped AUC.

## What is explicitly stopped

- agreement-weighted pseudo-label confidence after its matched Stage-34 loss;
- the failed primary full-Raptor/DINO blend from the earlier disjoint-cohort replication;
- more deployment-only work as a substitute for model advancement;
- duplicate submissions of already-scored or unresolved releases.

## Public-repository boundary

The public repository records aggregate metrics, methodology, tests, and decisions. Raw MRI, report text, study identifiers, scanner assignments, row-level predictions, cache shards, model checkpoints, private service logs, and cloud credentials stay outside Git history.

## What is not claimed

- The 0.820 DINO leaderboard score is **not** compared directly to local grouped AUC as if they were the same evaluation.
- The 0.933 public reference is **not** claimed as independently trained by this project.
- Stage-37/38 outcomes are **not** claimed until their returned evidence passes validation.
- No clinical or diagnostic claim is made.
