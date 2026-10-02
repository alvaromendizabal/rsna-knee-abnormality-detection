# Project status

Updated from verified aggregate evidence through **Stage 80 · 2026-10-02 UTC**. Stage 81 is prepared but has not been executed.

## Current boundary

The current official public-score incumbent is **0.943 macro ROC-AUC**. A user-supplied October 1 leaderboard snapshot shows **0.961** at the top, so the current public-score gap is **0.018**.

The current owned internal grouped OOF incumbent is **0.793686 macro ROC-AUC**. That number is internal model-selection evidence and is **not directly comparable** with the public 0.943.

## Validation contract

The research boundary remains:

- canonical exact-window cache: **4,407 studies / 69.14 GiB**;
- image cache layout: **NCHW**;
- grouped non-gold rows: **4,349**;
- audit-only gold rows: **58**;
- scanner groups: **59**;
- fold sizes: **870 / 870 / 870 / 870 / 869**;
- scanner groups crossing folds: **0**;
- gold optimizer rows: **0**.

These contracts are unchanged by the later frontier work.

## Stages 73–74 — target-specific residual confirmed and promoted

The earlier broad residual branch had been closed under a preregistered gate. The next frontier narrowed the question to targets with reproducible residual headroom.

A current-hardware revalidation then independently confirmed the target-specific residual on all five folds. Aggregate full-OOF evidence:

- current internal baseline: **0.791208**;
- promoted internal blend: **0.793686**;
- full-OOF gain: **+0.002479**;
- MCL gain: **+0.012874**;
- Lateral Meniscus gain: **+0.016871**;
- all five fold gains: **positive**;
- all other ten targets: **protected exactly**.

This component was promoted because it survived screening, untouched confirmation, bootstrap checks, and full-OOF reconstruction without relaxing the frozen decision rule.

The public repository records only aggregate evidence; row-level predictions, exact checkpoints, weights, and competition-specific inference remain private.

## Stage 75 — public control source recovered into AWS

The exact current public control source corresponding to the **0.943** official incumbent was recovered and pinned inside the private AWS workspace.

That recovery matters operationally because future model work can be compared against a stable external control without turning the score platform into the research environment.

The source binary identity and private integration details remain outside this repository.

## Stages 76–79 — submission workflow closed and boundary tightened

Several delivery-engineering attempts exposed brittle assumptions around remote notebook and private-asset orchestration.

Those attempts did **not** produce a new official score. They were closed, and the project boundary was tightened:

> substantive research stays on AWS; the external competition platform is reserved for a final score-producing submission only.

This is treated as an engineering lesson rather than a modeling result. The public repository intentionally omits platform credentials, private asset handles, runner internals, and submission glue.

## Stage 80 — dense anatomy branch executed and closed negative

Stage 80 tested a new spatial/anatomy representation family on the grouped AWS boundary.

The experiment ran successfully after one implementation bug was converted into a regression test. Screening used folds 0 and 2 with cross-fit blend selection.

Aggregate result:

- screening baseline: **0.787494**;
- candidate blend: **0.786693**;
- macro delta: **−0.000801**;
- fold 0 delta: **+0.000209**;
- fold 2 delta: **−0.001234**;
- bootstrap positive fraction: **0.075**;
- 95% delta interval: approximately **[−0.00208, +0.00035]**.

Selected target-level movement included:

- Lateral OA: **+0.00530**;
- Synovitis: **−0.00783**;
- Effusion: **−0.00334**;
- Lateral Meniscus: **−0.00333**.

Decision: **close the branch at screening**. Confirmation folds were not run.

This is a successful scientific execution with a negative result, not an execution failure.

## Stage 81 — next representation frontier prepared

The next AWS-only branch targets representation diversity rather than further tuning the closed Stage-80 idea.

The public description is intentionally high-level:

- frozen dense self-supervised image features;
- compact distillation bottleneck;
- target-specific multi-plane aggregation;
- cross-fit screening before any confirmation spend;
- prediction/residual correlation diagnostics against the current incumbent;
- resumable feature caching.

At this publication boundary Stage 81 is **prepared, tested, and not yet executed**. No accuracy claim is made.

## Current next step

1. execute Stage 81 entirely on AWS;
2. if screening is scientifically negative, close it without micro-tuning;
3. if it passes, complete untouched confirmation and five-fold OOF;
4. retain only genuinely complementary target/model components;
5. reserve the score platform for a final frozen candidate.

See [AWS residual frontier](AWS_RESIDUAL_FRONTIER.md) and [Notebook 12](../notebooks/12_owned_residual_and_representation_frontier.ipynb).
