# Image-model research record

## Objective and evaluation boundary

The competition objective is macro-ROC-AUC across twelve MRI findings. Brier score is used only as a probability-error diagnostic. AWS holds the private research workspace and large immutable artifacts; GitHub contains curated aggregate evidence.

Local scanner-grouped AUC, expert-audit diagnostics, and public leaderboard AUC are reported as distinct evaluation settings. They are not substituted for one another.

## Model families and provenance

The independent DINOv2 system uses plane-preserving MRI windows, a DINOv2-Small backbone, and target-specific aggregation. The current public record includes a matched epoch-3 training result and an official image-only code-submission score.

The public Raptor branch uses a CoAtNet/RMLP backbone with 1,024-dimensional window features, target-attention pooling, and twelve target-specific outputs. The transferred checkpoint contains about 73.1 million parameters. The public source and weight dataset are attributed in [SOURCES.md](SOURCES.md); training-membership and model-selection claims from those sources are not treated as independently verified facts.

## Input fidelity and ablations

Stage 24 reconstructed a complete real study, verified DICOM identifiers/order/spacing/decoding, and reproduced the public 64-image / 42-window representation. Later stages reused encoded features to evaluate fluid-only, within-series, boundary-window, and full-input variants without unnecessary re-encoding.

Stage 25 found that full input did not outperform the fluid-only ablation on the first development cohort. Stage 26 found no macro-AUC gain from removing only boundary-crossing windows. Those branches were not expanded.

## Heterogeneous ensemble research

A 90/10 full-Raptor/DINO mixture screened positively on the original development pilot but **failed** on a separate cohort: macro-AUC fell from 0.922410 for fluid-only Raptor to 0.919150. The failed primary result remains part of the public record.

A predefined 90% fluid-only Raptor + 10% DINOv2 secondary arm scored 0.926383 on that replication cohort and later passed a separate development qualification gate. Because the weight was not learned from fold-complete OOF predictions, this evidence remained developmental rather than final.

## Stage 31 — deployment fidelity

The fixed fluid-Raptor/DINO candidate was converted into a deterministic offline inference package. The accepted offline Tesla T4 preview completed all three visible studies in **39.87 seconds**, and CPU/GPU prediction differences were far below the predefined numerical tolerances.

The numerical agreement established implementation fidelity—not an AUC improvement. The associated Stage-31 submission completed without a published score in the evidence retained here.

## Stage 33 — complete data and grouped folds

The exact-window cache now covers **4,407 / 4,407 studies across 14 / 14 shards**. Stage 33 also froze a five-fold scanner-group split:

- 59 scanner groups;
- fold sizes 870 / 870 / 870 / 870 / 869;
- 4,349 non-gold rows assigned to folds;
- 58 expert rows held audit-only;
- zero gold optimizer rows;
- zero scanner-group leakage.

This changes the interpretation of later model experiments: the project can now move from partial-data diagnostics toward fold-complete OOF training.

## Stage 34 — matched continuation and a stopped supervision hypothesis

Both Stage-34 arms began from the same DINOv2 epoch-2 checkpoint and used the same scanner-grouped fold-0 split.

| System | Grouped fold-0 macro-AUC |
|---|---:|
| Epoch-2 starting checkpoint | 0.760266 |
| Matched epoch-3 baseline | **0.763762** |
| Agreement-weighted epoch-3 candidate | 0.762969 |

The baseline improved by about **0.00350** versus the starting checkpoint. The agreement-weighted candidate trailed the matched baseline by **0.000793**, so that supervision-consistency direction was stopped. Gold audit rows were not used for model selection.

## Stage 36 — official image-only score

The retained epoch-3 baseline was packaged for dynamic code-competition inference with strict checkpoint loading, finite/range checks, schema validation, missing-view handling, and runtime projection. The visible three-study T4 preview completed without decode failures.

Submission **56507693** then scored **0.820 public AUC**.

That official score is the strongest evidence that the independently trained DINO branch, in its current form, is not close to the project’s reproduced **0.933** multi-model reference. The result motivates structural changes and fold-complete training rather than additional deployment tuning.

## Leading-system reproduction matrix

| Capability | Verified scope | Remaining gap |
|---|---|---|
| Public multi-model reference ensemble | Official public score 0.933; inference reproduced | Independent ensemble training not recreated |
| Raptor on AWS/Kaggle | Strict loading, real-input parity, missing-view execution, CPU/GPU parity | Strong grouped training reproduction absent |
| Independent DINOv2 | New epoch-3 weights, grouped fold result, official 0.820 code-submission score | Full five-fold OOF and stronger representation absent |
| Exact-window cache | 4,407 / 4,407 studies | Cache-vs-direct model-logit equivalence still required |
| Scanner-grouped validation | Five folds, 59 scanner groups, no group leakage | Fold-complete model predictions not yet produced |
| Agreement-weighted supervision | Matched one-fold test | Underperformed; stopped |
| OOF ensemble | Not established | Requires fold-complete predictions from promoted families |

## Prioritized research decision

The next credible score-moving program is:

1. prove cache-versus-direct model-logit equivalence;
2. resolve trainable-depth capacity under a matched single-fold test;
3. train a five-fold grouped OOF baseline on all non-gold rows;
4. test geometry / slice-selection and target-specific spatial mechanisms against that baseline;
5. learn heterogeneous ensemble weights from OOF predictions only.

This is a ceiling-escape decision: complete data are now available, so infrastructure work must translate into stronger learned systems and stronger OOF evidence.

## Sources and limitations

See [SOURCES.md](SOURCES.md) for competition, DINOv2, Raptor, and participant-research references. Participant write-ups are treated as hypotheses to reproduce, not as our experimental results.

Raw images, reports, study IDs, scanner assignments, row-level predictions, checkpoints, cache shards, and private cloud logs are deliberately not redistributed.
