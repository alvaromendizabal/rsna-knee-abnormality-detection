# Project status

Updated from verified returned evidence through **2026-09-24 02:47 UTC**.

## Stage 33 — full cache and grouped-fold contract complete

The training-data bottleneck identified in Stage 32 is closed.

- official training studies: **4,407**
- accepted exact-window cache: **4,407 / 4,407 (100%)**
- completed cache shards: **14 / 14**
- accepted cache size: **69.14 GiB**
- unexpected decode failures: **0**
- scanner groups: **59**
- grouped folds: **5**
- non-gold rows assigned to folds: **4,349**
- fold sizes: **870 / 870 / 870 / 870 / 869**
- expert audit rows: **58**
- gold optimizer rows: **0**
- scanner-group leakage: **false**

The cache/fold loader smoke test passed. Raw cache shards, study identifiers, scanner catalog rows, and fold-row assignments remain private.

## Stage 34 — matched one-fold training advancement

Stage 34 was the first new-weight training milestone after the earlier Stage-11 checkpoint. Both arms began from the same epoch-2 checkpoint and used the same finalized scanner-grouped fold-0 split.

| System | Grouped fold-0 macro-AUC |
|---|---:|
| Stage-11 epoch-2 start | 0.760266 |
| Matched epoch-3 baseline | **0.763762** |
| Agreement-weighted epoch-3 candidate | 0.762969 |

The agreement-weighted candidate trailed the matched baseline by **0.000793**, so the supervision-consistency direction was stopped. Gold audit rows were not used for model selection and contributed zero optimizer rows.

## Stage 36 — official code-submission result

The retained epoch-3 baseline was packaged as dynamic image-only code inference, passed strict checkpoint/schema/range/runtime gates, and produced one guarded submission: **56507693**.

Its official public score completed at **0.820**.

This result is materially below both the reproduced public multi-model reference at **0.933** and the **0.958** leader on the returned leaderboard context. It therefore does not replace the 0.933 reference as the project’s best scored system.

## Current competitive state

- Reproduced public reference: **0.933 public macro-ROC-AUC**
- Returned leader: **0.958**
- Comparable reference-to-leader gap: **0.025**
- Independent DINOv2 epoch-3 official score: **0.820**
- Full exact-window data contract: **complete**
- Scanner-grouped fold contract: **complete**
- Fold-complete OOF training: **not yet complete**

## Active frontier

The next score-moving program is deliberately structural rather than cosmetic:

1. prove cached-versus-direct model-logit equivalence before relying on the 69 GiB cache for five-fold fitting;
2. resolve whether increasing trainable DINO depth improves the matched grouped baseline;
3. train a scanner-grouped five-fold OOF baseline on all 4,349 non-gold studies;
4. test stronger geometry / slice-selection families against that OOF baseline;
5. learn heterogeneous ensemble weights only from fold-complete OOF predictions.

In-flight Stage-37/38 work is not promoted here as a result until returned evidence passes its gates.

See [Notebook 07](../notebooks/07_deployment_and_training_frontier.ipynb), [Training frontier](TRAINING_FRONTIER.md), and [Image-model record](IMAGE_MODELS.md).
