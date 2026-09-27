# Training frontier

## Why the frontier moved

The project is no longer blocked by missing cache coverage or incomplete OOF infrastructure.

The exact-window cache covers all **4,407 studies**. Scanner grouping supplies five leakage-aware folds across **4,349 non-gold rows**, with **58 expert studies retained for audit only**.

The research frontier then advanced in three material steps:

1. **Stage 43:** complete five-fold DINO OOF at **0.786557**.
2. **Stage 47:** a heterogeneous MaxViT complement improved the selected cross-fitted ensemble to **0.791208**.
3. **Stage 50:** a frozen MCL + Lateral Meniscus expert overlay improved three untouched confirmation folds from **0.795488 to 0.798017**.

Stage 54 then rejected a depth-position correction under a matched-control experiment. That direction is closed unless materially new evidence appears.

## Current best and gap

**Current strongest owned internal system:** Stage 50 two-target overlay.

- independent three-fold confirmation macro-AUC: **0.798017**
- confirmation delta versus frozen Stage-47 baseline: **+0.002529**
- descriptive five-fold grouped OOF: **0.793687**

**Historically scored public reference:** **0.933 public macro-ROC-AUC**.

**Last verified leader in the same returned leaderboard context:** **0.958**.

**Comparable historical public gap:** **0.025**.

Grouped OOF and public leaderboard AUC are different evaluation settings and are not compared numerically as if they were the same metric sample.

## Data, validation, and deployment readiness

| Capability | Verified state |
|---|---|
| Exact-window cache | **4,407 / 4,407 studies** |
| Scanner groups | **59** |
| Grouped folds | **5** |
| Fold sizes | **870 / 870 / 870 / 870 / 869** |
| Non-gold OOF rows | **4,349** |
| Expert audit-only rows | **58** |
| Gold optimizer rows | **0** |
| Stage-43 five-fold DINO OOF | **complete** |
| Stage-47 heterogeneous OOF | **complete and promoted** |
| Stage-50 independent confirmation | **complete and passed** |
| Owned checkpoint sampled replay | **15 / 15 model checkpoints covered** |
| Archived probability comparisons | **10,080 passed** |
| Exact sampled raw-image parity | **3 / 3 complete canary studies** |
| Raw-input owned-ensemble smoke | **passed on two complete studies** |
| Scored-reference identity/integration | **open** |
| Full test-like offline runtime/schema gate | **open** |

## Ranked backlog

The backlog is ordered by expected decision value and score relevance.

| Rank | Capability | Current state | Why it matters |
|---:|---|---|---|
| 1 | Scored-reference identity + integration | **Open** | The 0.933 reference is still the strongest historically scored system; Stage 50 should complement it rather than blindly replace it. |
| 2 | Complete test-like inference gate | **Open** | Series selection, whole-cohort ranking, output schema, determinism, and runtime must be validated before another submission. |
| 3 | Target-specific ROI / localization model | **Not yet implemented as a materially new capability** | Weak targets may need local anatomical evidence rather than another global-head adjustment. |
| 4 | Multi-acquisition / richer multi-plane representation | **Open research direction** | The current three-slot representation may leave complementary acquisitions unused. |
| 5 | Stronger medical-imaging pretraining / foundation transfer | **Open research direction** | Generic ImageNet/DINO priors may leave domain-specific representation quality on the table. |
| 6 | Leakage-safe residual ensemble against the scored-reference family | **Blocked on reference OOF/identity** | The remaining public gap is most plausibly attacked through complementary errors, not blind averaging. |

## Promotion logic

1. Preserve Stage 50 as the confirmed owned incumbent until a materially stronger candidate passes the same scanner-grouped evidence boundary.
2. Do not learn blend weights from the public leaderboard or test set.
3. Recover reference OOF or an equivalent leakage-safe comparison before claiming learned reference + Stage-50 weights.
4. Require new model research to introduce a meaningful capability and evaluate it with controlled ablations.
5. Keep gold/expert rows audit-only unless a separately justified experiment changes that contract.
6. Preserve negative experiments and stop directions that fail prespecified gates.
7. Require complete offline schema/runtime/lineage validation before the next submission boundary.

## Explicitly closed directions

- raw-float inference as a substitute for the cache-aligned uint8 contract;
- agreement-weighted supervision from Stage 34;
- the Stage-44 spatial direction in its tested form;
- Stage-46 ConvNeXt complement;
- the Stage-49 four-target weak-expert blend;
- ACL and Synovitis expert overlays from Stage 49;
- Stage-54 corrected depth-position head replacement;
- heavy multiprocessing and /dev/shm-dependent Studio input pipelines;
- Kaggle-hosted research/development.

## Stage 54 as a model-research example

Stage 54 used a frozen feature bank and controlled only the depth-position representation.

- reused training features: **2,048 rows**
- new held-out features: **870 rows**
- matched head fits: **2**
- epochs per head: **6**
- encoder backprop steps: **0**
- legacy head fold-0 AUC: **0.748827**
- corrected-depth head fold-0 AUC: **0.748599**
- decision: **reject early on a required per-fold condition**

The failure of the hypothesis is useful evidence: the next experiment should not be another small depth-coordinate adjustment.

## Public-repository boundary

The public repository records aggregate metrics, methodology, tests, and decisions. Raw MRI, report text, study identifiers, scanner assignments, row-level predictions, cache shards, feature banks, model checkpoints, private service logs, cloud credentials, and full return bundles stay outside Git history.

## What is not claimed

- Internal grouped OOF is not a leaderboard score.
- The 0.933 public reference is not claimed as independently trained by this project.
- The bounded raw-image canaries do not prove whole-test preprocessing coverage.
- The two-study raw-input smoke does not prove hidden-test runtime.
- Stage 54 did not improve the incumbent.
- No clinical or diagnostic claim is made.
