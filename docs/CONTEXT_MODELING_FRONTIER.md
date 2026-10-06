# Cross-slice context modeling frontier

## Research question

Does explicitly modeling ordered evidence across MRI windows add complementary disease signal beyond the retained heterogeneous system and frozen image representations?

## Validation design

The public result uses the same **4,349-study scanner-grouped development population** as the retained research baseline.

The comparison preserves fold membership, target ordering, training-only learned preprocessing, protected outputs, and the separation between internal grouped evidence and external recorded performance.

## Stage 101 — initial controlled screen

A bounded held-out screen compared an orderless matched control with an ordered context model.

Result: both added complementary signal, and ordered context provided the stronger aggregate development result.

## Stage 102 — full-cohort cross-fit

| System | Macro ROC-AUC |
|---|---:|
| Retained Stage 84 research system | **0.7943834** |
| Stage 102 ordered-context system | **0.7978448** |

Gain: **+0.0034614** on the same development population.

The recorded experiment improved across all five folds while preserving the protected-target contract.

## Stage 103 — integration qualification

The trained context system then passed full-cohort exported-prediction parity and fixed cache-canary checks.

No additional predictive gain was claimed.

## Stage 104 — explicit neighbor-context probe

| System | Macro ROC-AUC |
|---|---:|
| Stage 102 ordered context | **0.7978448** |
| Matched Stage 104 control | **0.7978797** |
| Stage 104 neighbor-context candidate | **0.7978946** |

The neighbor candidate's gain over Stage 102 was about **+0.0000499**, but its paired 90% uncertainty interval crossed zero.

Decision:

- retain the point estimate;
- do not promote it as established improvement;
- close repeated micro-tuning of this exact mechanism;
- move to a materially different ranked capability.

## Why this is portfolio-relevant

The sequence shows a disciplined research loop:

1. identify a mechanism from strong prior medical-imaging work;
2. isolate it with a matched control;
3. prove a development signal before expanding compute;
4. confirm it with full-cohort cross-fitting;
5. qualify inference parity separately;
6. test a narrower extension;
7. reject over-promotion when uncertainty becomes inconclusive.

## Evidence boundary

These are weak-label grouped research metrics.

They are not directly comparable with the external **0.943** record, not clinical validation, and not evidence of complete raw-input submission parity.
