# Training frontier

## Why the project is changing direction

Stages 23–31 established progressively stronger inference correctness: strict checkpoint loading, real-DICOM reference parity, cached ablations, heterogeneous-model replication, missing-view execution, exact CPU/GPU numerical contracts, and one guarded offline-GPU release.

Stage 32 identified the more important competitive bottleneck: **the learned systems have not been retrained on a complete current-data contract**.

The accepted exact-window cache contains **960 of 4,407 studies (21.8%)**. The current independent DINO branch is not a fold-complete OOF system, and the scored 0.933 reference is an externally trained multi-model ensemble rather than an independently reproduced training result.

## Current best and gap

**Current scored incumbent:** reproduced public reference ensemble, **0.933 public macro-ROC-AUC**.

**Returned leaderboard leader:** **0.958** on the same dated page.

**Comparable gap:** **0.025**.

**New release candidate:** submission **56476938**, 90% fluid-only Raptor + 10% DINOv2. Its score remained pending in Stage-32 evidence. It must not be treated as an improvement until an official score is returned.

## Missing capabilities

The ranked backlog is based on expected information/score value, not convenience:

| Rank | Capability | Current state | Priority |
|---:|---|---|---:|
| 1 | Complete exact-window training cache | 960 / 4,407 studies | 9.8 |
| 2 | Scanner-grouped five-fold OOF baseline | Not established | 9.5 |
| 3 | Training-label lineage / soft-label audit | Current labels verified; training lineage incomplete | 9.2 |
| 4 | Geometry and slice-selection ablation | Partial; no full-data matched OOF test | 8.6 |
| 5 | Target-specific spatial / ROI modeling | Not implemented for weak target families | 8.1 |
| 6 | OOF heterogeneous ensemble | Absent | 7.9 |

## New advancement

The next major experiment is not another blend-weight tweak. It adds a capability the current system does not have:

**complete-data, scanner-grouped, fold-complete validation with OOF predictions.**

That enables later ensemble weights to be learned from OOF predictions rather than exposed audit cohorts and lets geometry, supervision, or fine-tuning changes be compared against a credible grouped baseline.

## Promotion logic for the next modeling round

1. Complete and validate the current exact-window cache.
2. Freeze scanner-grouped folds with the 58 expert studies audit-only.
3. Reproduce a strong Stage-11-style baseline under the new fold contract.
4. Test one structurally new training capability against that baseline.
5. Escalate to broader/five-fold training only when the single-fold gain is material and target-level evidence supports it.
6. Learn ensemble weights only from OOF predictions.

## Public-repository boundary

The public repository records aggregate metrics, methodology, tests, and decisions. Raw MRI, report text, study identifiers, row-level predictions, cache shards, model checkpoints, private service logs, and cloud credentials stay outside Git history.

## What is not claimed

- Stage 33 is **not** reported as completed.
- Submission 56476938 is **not** reported as scored.
- CPU/GPU parity is **not** evidence of higher AUC.
- The 0.933 public reference is **not** claimed as an independently trained winning system.
- No clinical or diagnostic claim is made.
