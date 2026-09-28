# Training frontier

## The baseline is the scored reference

The project’s historically strongest public result is the reproduced **0.933 multi-branch reference**. The last recorded leader in the same returned leaderboard context is **0.958**, leaving a historical gap of **0.025**.

The owned DINO/MaxViT research branch remains valuable, but it is no longer treated as the baseline for public-score improvement work. Future gains must be evaluated against the complete scored reference or described explicitly as separate internal research.

## What has already been learned

The owned branch established several reusable lessons:

- heterogeneous models can improve a stronger branch through complementary errors;
- target-specific experts can help when frozen and confirmed independently;
- whole-cohort ranking and protected-target invariance need explicit tests;
- raw-input parity, strict checkpoint lineage, resumability, and bounded execution are deployment requirements;
- several near-duplicate or harmful directions should remain closed rather than repeatedly retrained.

Those lessons transfer as **engineering and candidate-design principles**, not as automatic blend weights or preprocessing rules.

## Scored-reference readiness

| Capability | Verified state |
|---|---|
| Historically scored reference | **0.933 public macro-ROC-AUC** |
| Last recorded leader | **0.958** |
| Selected reference asset paths | **36** |
| Audited reference weight files | **32** |
| GPU checkpoint checks | **32 / 32 passed** |
| Stored native fingerprints checked | **20** |
| GPU runtime | **isolated and passing** |
| Trained Rad heads loaded | **15** |
| Controlled Rad final output | **exact across all three trials** |
| Head-only speed ratio | **1.274×** |
| Complete real-image reference reproduction | **open** |
| Reference-level accuracy improvement | **not established** |
| Submission-ready candidate | **no** |

## Ranked backlog

| Rank | Capability | Current state | Decision value |
|---:|---|---|---|
| 1 | Complete real-image reference replay | **Stage 64 prepared** | Establish the actual 0.933 recipe as the executable control before interpreting any candidate. |
| 2 | Real-feature Rad runtime parity | **Prepared** | Determine whether the 20→15 head-call reduction is safe and useful on actual image features. |
| 3 | Original-Raptor coverage experiment | **Prepared for diagnostic replay** | Apply denser evidence to the original reference branch while holding the rest of the scored stack fixed. |
| 4 | MCL/Lateral residual candidate against full reference | **Code preserved, weights not transferred** | Test whether independently confirmed expert signal remains complementary to the stronger reference. |
| 5 | MaxViT residual candidate against full reference | **Code preserved, not promoted** | Reuse proven heterogeneous complementarity only if it improves the complete reference control. |
| 6 | Stronger target-specific / medical-pretraining capability | **Future research** | Introduce materially new signal only after the scored reference is reproducible end to end. |

## Promotion logic

1. The complete scored reference is the control for public-score improvement work.
2. Require real-image control reproduction before interpreting candidate deltas.
3. Do not transfer old blend weights from a weaker baseline without reference-level evidence.
4. Preserve each branch’s original preprocessing unless a controlled experiment explicitly changes it.
5. Require exact output parity before activating a speed-only optimization.
6. Learn weights only from leakage-safe predictions; never tune against the public leaderboard.
7. Keep audit-only expert studies out of optimizer/model-selection logic unless a new protocol is explicitly justified.
8. Require complete output, lineage, determinism, and runtime gates before another submission.

## Directions that remain closed in their tested forms

- raw-float inference as a substitute for the cache-aligned owned-model contract;
- agreement-weighted supervision from Stage 34;
- the tested Stage-44 spatial direction;
- Stage-46 ConvNeXt complement;
- Stage-49 four-target weak-expert blend;
- ACL and Synovitis expert overlays from Stage 49;
- Stage-54 corrected-depth head replacement;
- heavy multiprocessing / shared-memory Studio input pipelines;
- the rejected encode-once inference shortcut;
- Kaggle-hosted research and training.

## Public-repository boundary

GitHub records aggregate metrics, validation rules, tests, runtime decisions, and research conclusions. Raw MRI, identifiers, row-level predictions, cache shards, feature banks, checkpoint files, full private source, cloud credentials, and private return bundles stay outside Git history.

## What is not claimed

- Stage 63 does not improve the public score.
- A 1.274× head-only ratio is not a 1.274× end-to-end notebook speedup.
- The assembled reference snapshot is not claimed to prove complete historical binary identity.
- Stage 64 is prepared, not completed.
- No clinical or diagnostic claim is made.
