# Training frontier

## Mandatory public control

This historical snapshot records the project’s scored reference at **0.933 public macro-ROC-AUC**. Later project evidence is summarized in [Project status](PROJECT_STATUS.md).

Internal grouped metrics are used for research decisions and are not treated as public-score equivalents.

## Strategy after Stage 67

Development-time access to the original competition preview inputs was blocked. Rather than move research back to Kaggle, the project preserved the recovered reference assets and shifted to **AWS-only residual modeling**.

The key question for every new branch is now:

> Does this model contribute stable, leakage-aware signal that is sufficiently different from the existing system to justify confirmation and later reference-level integration?

Standalone score is necessary evidence, but not the objective by itself.

## Current research boundary

| Capability | State |
|---|---|
| Historical scored reference | **0.933** |
| Reference GPU checkpoint validation | **32 / 32 passed** |
| Canonical exact-window cache | **4,407 studies / 69.14 GiB** |
| Canonical cache layout | **NCHW** |
| Grouped non-gold rows | **4,349** |
| Gold audit-only rows | **58** |
| Gold optimizer rows | **0** |
| Stage-68 small-CNN screen | **not evaluated; source-location failure** |
| Stage-69 small-CNN screen | **not evaluated; cache-layout failure** |
| Stage-70 recovery | **prepared, not executed** |

## Ranked backlog

| Rank | Capability | Current state | Decision value |
|---:|---|---|---|
| 1 | ResNet34/224 residual screen | **Stage 70 prepared** | Establish whether a deliberately small CNN adds complementary signal before expanding the search. |
| 2 | Full-fold confirmation of the frozen small CNN | **blocked on screen result** | Prevent tuning after seeing confirmation folds. |
| 3 | Physical sampling / bagged-slice representation | **planned** | Introduce materially different anatomical evidence if the baseline CNN is redundant. |
| 4 | EfficientNet-B0 matched architecture comparison | **planned** | Test a second efficient family without changing multiple factors simultaneously. |
| 5 | MCL/Lateral residual comparison | **preserved** | Reuse independently confirmed target-specific signal only if it remains complementary to the scored-reference program. |
| 6 | MaxViT residual comparison | **preserved** | Reuse heterogeneous complementarity only under reference-aware evidence. |
| 7 | Test-time augmentation | **last** | Potential incremental gain with direct inference-runtime cost. |

## Promotion logic

1. Keep **0.933** as the public-score control.
2. Preserve scanner-group boundaries and zero gold optimizer rows.
3. Use candidate OOF predictions for learned research decisions.
4. Do not manufacture reference OOF lineage where it has not been proven.
5. Treat any fixed reference-preserving overlay without comparable OOF as heuristic until an official scored result exists.
6. Change one major modeling factor at a time during the small-model frontier.
7. Confirm a frozen configuration on untouched folds before considering submission integration.
8. Validate AWS inference, schema, lineage, determinism, and runtime before Kaggle execution.
9. Keep Kaggle as the final submission/inference surface, not the development environment.

## Explicitly closed or deferred paths

- development-time Kaggle preview acquisition;
- raw-float substitution for the exact cache contract;
- the tested Stage-44 spatial direction;
- Stage-46 ConvNeXt complement in its tested form;
- Stage-49 four-target weak-expert blend;
- ACL and Synovitis expert overlays from Stage 49;
- Stage-54 corrected-depth head replacement;
- heavy shared-memory multiprocessing in Studio;
- rejected encode-once inference shortcut.

## Public-repository boundary

GitHub records aggregate metrics, contracts, failure modes, tests, and decisions. Raw MRI, identifiers, row-level predictions, cache shards, exact sampling implementation, weights, calibration assets, private cloud paths, and full competition glue stay private.
