# Project status

Updated from verified Stage-31 and Stage-32 returns through **2026-09-23 00:52 UTC**.

## Stage 31 — deployment fidelity and guarded release

The frozen **90% fluid-only Raptor + 10% DINOv2** candidate completed a hermetic local shadow and an offline Tesla T4 preview. Both actual checkpoints loaded strictly and all three visible test studies executed.

Maximum AWS-versus-T4 probability differences were:

- DINOv2: **1.043e-6** (limit 1e-3)
- Raptor: **5.960e-7** (limit 1e-4)
- fixed blend: **5.782e-7** (limit 1e-4)

The preview took **39.87 seconds**. Exactly one guarded candidate submission was requested: **56476938**. Stage 31 performed no training fits and did not repeat the existing scored reference submission.

## Stage 32 — score reconciliation and ceiling-escape audit

All eight read-only gates passed. Submission 56476938 remained **pending** through the returned score-poll window. The scored incumbent remained the reproduced public multi-model reference ensemble at **0.933**, versus **0.958** on the same returned leaderboard page.

Stage 32 also established the current training bottleneck:

- official training studies: **4,407**
- accepted exact-window cache: **960**
- coverage: **21.8%**
- remaining studies: **3,447**
- completed cache shards: **3 / 14**
- current official metadata matched the accepted AWS copies
- recent release stages used frozen checkpoints; **no current full-data retraining has been verified**

This changes the research priority. Deployment fidelity is no longer the main missing capability. Complete-data, scanner-grouped validation and fold-complete OOF predictions are.

## Next gate — not yet completed

The next data-readiness milestone is prepared outside the public repository: finish the exact-window cache, build a scanner-group catalog, freeze leakage-safe grouped folds, and smoke-test the cache/fold join before a new model fit.

**This repository does not claim that Stage 33 completed.** An earlier preflight exposed a local-path assumption and a corrected handoff was prepared; only executed, returned evidence will be promoted into the public record.

## Current competitive state

- Scored reference: **0.933 public macro-ROC-AUC**
- Returned leader: **0.958**
- Comparable dated gap: **0.025**
- Candidate 56476938: **pending in Stage-32 evidence**
- Stage-31 release branch: engineering-complete, score unresolved
- Next score-moving program: complete-data grouped training and OOF evaluation

See [Notebook 07](../notebooks/07_deployment_and_training_frontier.ipynb), [Training frontier](TRAINING_FRONTIER.md), and [Image-model record](IMAGE_MODELS.md).
