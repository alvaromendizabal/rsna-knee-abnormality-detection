# Project status

Updated from verified returned evidence through **Stage 63 · 2026-09-28 UTC**.

## Current boundary

The historically best scored system remains the **0.933 public reference**. The project has now recovered and GPU-validated the assembled multi-branch reference runtime far enough to move from asset/runtime recovery into **real-image control reproduction**.

No Stage 55–63 result is presented as an accuracy improvement. Their value is that the correct scored baseline is now the object being verified and optimized.

## Preserved model-research evidence

The owned research branch remains useful as complementary evidence and candidate components:

- Stage 43 five-fold DINO grouped OOF: **0.786557**;
- Stage 47 DINO + MaxViT grouped OOF: **0.791208**, delta **+0.004650**, improving all five folds;
- Stage 50 frozen MCL + Lateral Meniscus overlay: independent confirmation **0.795488 → 0.798017**, delta **+0.002529**, improving folds 1, 3, and 4;
- Stage 54 corrected-depth head: **rejected** against its matched control; incumbent unchanged.

These results do not establish a gain over the 0.933 public reference. Their transferable components are treated as future residual candidates against that full reference, not as replacements for it.

## Stage 55–61 — reference-source and asset recovery

The project recovered the scored-reference source/receipts, distinguished the reference from the weaker owned branch, assembled its required model-resource families, and moved approximately **3.28 GB across 36 selected asset paths** into a checksum-bound snapshot.

Reference assets are kept private. The public record exposes only aggregate counts and engineering decisions.

The accepted CPU audit covered **32 weight files**. It used restricted checkpoint loading, tensor-finiteness checks, source-derived task-head checks, and version-aware runtime handling. No new training was performed.

## Stage 63 — GPU reference readiness complete

Stage 63 reused the accepted CPU proofs and exercised the assembled reference models on one NVIDIA L40S.

Verified aggregate result:

- reference weight files: **32**;
- GPU checkpoint checks: **32 / 32 passed**;
- stored native fingerprints checked where available: **20**;
- device: **NVIDIA L40S**;
- selected isolated runtime: **timm 1.0.20** with PyTorch **2.8.0**;
- model fits: **0**;
- complete real-image reference reproduction: **not yet complete**;
- submission ready: **false**.

The runtime was isolated instead of hot-reloading incompatible library versions inside a process. This preserves the installed environment while allowing the recovered reference architectures to load reproducibly.

## Reference-specific runtime optimization

A source-derived RadImageNet-head optimization removes five diagnostic-only head-prediction calls while preserving the contributing heads, calibration logic, and ranking path.

Stage 63 loaded **15 trained heads** and measured three controlled GPU trials:

| Trial | Original head seconds | Candidate head seconds | Final output |
|---:|---:|---:|---|
| 1 | 0.026731 | 0.023506 | exact |
| 2 | 0.026663 | 0.020932 | exact |
| 3 | 0.026521 | 0.020787 | exact |

Median head-only speed ratio: **1.2738×**.

This is **not** an end-to-end notebook speed claim. Encoder features and upstream predictions were synthetic in this benchmark, real-image parity is still open, and the optimization is not automatically activated.

## Historical public-score context

- reproduced public reference: **0.933 public macro-ROC-AUC**;
- last recorded leader in the same returned context: **0.958**;
- historical comparable gap: **0.025**;
- independent DINO public score: **0.820**.

These figures are historical. A future submission requires a refreshed official-state check at the submission boundary.

## Current deployment gates

Completed:

- assembled scored-reference asset snapshot;
- accepted CPU audit across 32 reference weight files;
- isolated GPU runtime selection;
- 32 / 32 GPU checkpoint checks;
- 20 stored native fingerprints checked where available;
- trained-head differential benchmark with exact final output on controlled features.

Still open:

1. reproduce the complete calibrated reference on **real MRI inputs**;
2. measure the Rad optimization on **real image features** and preserve exact final output;
3. evaluate fixed reference-level candidate changes against the same complete reference control;
4. validate the final offline wrapper: schema, whole-cohort ranking, determinism, lineage, runtime, and no silent fallbacks;
5. only then cross the competition submission boundary.

## Next milestone — Stage 64

Stage 64 is **prepared but not yet executed**. Its job is to run the complete reference on the original visible MRI preview cases, require numerical reproduction of the saved control, time the head optimization on real features, and generate controlled Raptor-coverage diagnostics.

Three preview cases are a regression/deployment gate, not an accuracy evaluation. No improvement over 0.933 is claimed until comparable scored evidence exists.

See [Scored-reference frontier](SCORED_REFERENCE_FRONTIER.md), [Notebook 09](../notebooks/09_scored_reference_recovery_and_runtime.ipynb), and [Training frontier](TRAINING_FRONTIER.md).
