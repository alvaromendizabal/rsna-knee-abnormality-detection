# Project status

Updated from verified returned evidence through **2026-09-27 05:19 UTC**.

## Current research boundary

The project now has a complete scanner-grouped training/validation contract, a heterogeneous five-fold OOF ensemble, an independently confirmed two-target overlay, sampled checkpoint parity across all owned model families, and an exact sampled raw-input path.

The current strongest owned **internal** system is the Stage 50 two-target overlay. The strongest historically scored external/public reference remains 0.933. These numbers belong to different evaluation settings and are reported separately.

## Stage 43 — five-fold DINO incumbent

The DINO branch reached a complete scanner-grouped five-fold OOF boundary:

- non-gold OOF rows: **4,349**
- scanner-group folds: **5**
- grouped OOF macro-AUC: **0.786557**
- gold optimizer rows: **0**

This became the protected incumbent for heterogeneous complement research.

## Stage 47 — heterogeneous MaxViT complement promoted

A MaxViT/CoAtNet-style branch was weaker on its own but sufficiently complementary to DINO to improve the cross-fitted ensemble.

| System | Five-fold grouped OOF macro-AUC |
|---|---:|
| Stage 43 DINO incumbent | 0.786557 |
| Stage 47 selected DINO + MaxViT blend | **0.791208** |
| Delta | **+0.004650** |

The blend improved all five folds, introduced no target collapse worse than 0.01, and retained nonzero MaxViT contribution on eight targets.

## Stage 50 — MCL + Lateral Meniscus overlay independently confirmed

Stage 49 screened four targeted experts on folds 0 and 2. The full four-target blend was rejected, but MCL and Lateral Meniscus showed enough promise to freeze a narrower overlay before evaluating untouched folds 1, 3, and 4.

Frozen overlay:

- MCL: **30% expert / 70% Stage-47 incumbent**
- Lateral Meniscus: **40% expert / 60% Stage-47 incumbent**
- all other ten targets: **unchanged Stage-47 predictions**
- confirmation epoch: fixed in advance
- gold optimizer rows: **0**

Confirmation results:

| Confirmation setting | Macro-AUC |
|---|---:|
| Stage-47 baseline | 0.795488 |
| Stage-50 candidate | **0.798017** |
| Delta | **+0.002529** |

All three confirmation folds improved:

- fold 1: **+0.002051**
- fold 3: **+0.004988**
- fold 4: **+0.001428**

The descriptive five-fold Stage-50 OOF is **0.793687** versus **0.791208** for Stage 47. Because the five-fold value includes the two screening folds, it is not presented as a fully nested independent estimate.

## Stages 51–53 — inference and raw-input validation

Deployment work then moved from saved OOF evidence toward a reproducible AWS inference chain.

Verified bounded evidence now includes:

- **10,080 sampled archived-probability comparisons** across all 15 owned DINO / MaxViT / expert checkpoints;
- complete saved-ensemble arithmetic reconstruction across **4,349** studies;
- exact uint8 raw-image reconstruction on **3 / 3 complete canary studies**;
- raw-input smoke through all **15 owned checkpoints** on two complete studies;
- **1,080** raw-input probability values produced under whole-cohort ranking semantics;
- protected-target invariance retained where required.

These checks validate bounded samples. They do not establish hidden-test runtime, complete test-like series selection, or scored-reference integration.

## Stage 54 — depth-position hypothesis rejected cleanly

Stage 54 resumed 2,048 previously extracted feature rows, completed the remaining 870 validation rows, and trained two matched six-epoch heads. The image encoder was frozen and received zero optimizer steps.

| Fold-0 system | Macro-AUC |
|---|---:|
| Frozen parent head | 0.747798 |
| Matched legacy-depth head | **0.748827** |
| Corrected relative-depth head | 0.748599 |
| Stage-50 incumbent boundary | 0.788045 |
| Legacy-depth 10% overlay | 0.787949 |
| Corrected-depth 10% overlay | 0.788083 |

The corrected head failed a condition required to hold on every screening fold: it did not beat the matched legacy-depth control. The experiment therefore ended with a **valid early rejection** rather than spending another fold of GPU time. The incumbent was not modified.

The run completed in approximately **10.0 minutes** on one NVIDIA L40S and recorded about **$0.47** of process-time compute at the contemporaneous SageMaker JupyterLab rate. This is a project estimate, not an AWS invoice.

## Historical public-score context

- reproduced public reference: **0.933 public macro-ROC-AUC**
- last verified leader in the returned leaderboard context: **0.958**
- comparable historical gap: **0.025**
- independent Stage-36 DINO code submission: **0.820**

Internal grouped OOF and public leaderboard AUC are not treated as interchangeable.

## Current deployment gates

Completed:

- cache-aligned preprocessing contract;
- all 15 owned checkpoint sampled parity checks;
- sampled raw-image parity;
- bounded raw-input owned-ensemble smoke.

Still open:

1. recover and verify the complete **0.933 scored-reference identity**;
2. establish a leakage-safe or explicitly heuristic **reference + Stage-50 integration** and freeze it honestly;
3. validate **test-like series selection** beyond bounded raw canaries;
4. validate complete offline **output schema, cohort ranking, determinism, and runtime**;
5. only then cross the final competition submission boundary.

## Current research frontier

The next modeling work should introduce a materially new capability rather than repeat the rejected depth-head adjustment. Highest-value candidates include target-specific ROI/localization or multi-acquisition representations that are meaningfully different from the previously rejected spatial/depth variants, stronger medical-imaging pretraining, and heterogeneous residual modeling evaluated against the same scanner-grouped OOF boundary.

See [Notebook 08](../notebooks/08_heterogeneous_ensemble_and_deployment_validation.ipynb) and [Training frontier](TRAINING_FRONTIER.md).
