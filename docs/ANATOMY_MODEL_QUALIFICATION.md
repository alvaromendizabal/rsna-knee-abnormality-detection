# Anatomy model qualification

## Purpose

This milestone qualifies a pretrained knee-anatomy segmenter as a **research dependency**, not as a promoted disease model.

The public repository exposes the qualification contract and aggregate evidence while keeping private checkpoints, raw images, cloud paths, and competition-specific integration code outside Git history.

## Verified qualification evidence

Stage 96 completed **4/4 qualification tracks**.

Public-safe findings:

- two pretrained checkpoint metadata payloads were reviewed;
- both identify a full-resolution 3D configuration;
- the published label contract contains **9 foreground anatomical structures**;
- **3 coordinate adapters** were validated for project image geometry;
- exact parent-fallback behavior was checked against **10 saved component arrays**;
- no real segmentation Dice is reported yet;
- no disease AUC is attributed to the anatomy model.

A configuration-name discrepancy in a sidecar was resolved conservatively by trusting serialized checkpoint metadata over a folder label. The public repository records the principle, not private checkpoint identities.

## Why a qualification stage exists

External pretrained models are not accepted merely because the architecture looks relevant, the training domain is medical, a repository name says knee, or weights load successfully.

A useful localizer must pass distinct gates:

1. **source identity** — checkpoint and metadata agree;
2. **serialization safety** — loading is restricted and reviewed;
3. **architecture contract** — state keys/shapes match the expected runtime;
4. **coordinate contract** — model-space and image/patient-space mappings are explicit;
5. **reference quality** — a provided labeled example clears a predeclared segmentation gate;
6. **parent protection** — missing/disabled localization leaves parent predictions exactly unchanged.

## Public reference-quality gate

The public-safe helper defines the frozen engineering gate:

- exactly **9** foreground structures;
- mean foreground Dice **>= 0.85**;
- every individual foreground Dice **>= 0.50**;
- all values finite and bounded in [0, 1].

These are project pilot thresholds, not a claim of clinical adequacy and not an author-published standard.

The gate is frozen before real reference inference. A negative result should reject or re-diagnose the route rather than trigger repeated threshold tuning.

## Lifecycle

The public lifecycle is explicit:

**QUALIFICATION_INCOMPLETE → QUALIFIED_FOR_REFERENCE_PILOT → REFERENCE_GATE_PASSED or REFERENCE_GATE_REJECTED**

Only a passed reference gate permits exploratory native-image transfer.

A passed reference gate still does not mean disease-target performance improved, an external score improved, source-domain overlap is resolved, or the anatomy-conditioned classifier is promoted.

## Parent protection

The anatomy route is additive.

When a route is disabled, a region is missing, or visibility is insufficient, the disease prediction must remain exactly equal to the parent output.

The public helper demonstrates the invariant without revealing private fusion implementation.

## Next private AWS milestone

The next bounded run is intentionally four-part:

1. load one pinned frozen checkpoint;
2. measure reference-case Dice;
3. only if the reference gate passes, segment one existing sagittal series;
4. derive ROI/visibility evidence while re-proving parent preservation.

No classifier fitting is required for this qualification step.

## Employer-facing takeaway

This stage demonstrates how to introduce third-party pretrained AI into an existing high-performing system without skipping provenance, compatibility, safety, validation, or rollback contracts.

The model is treated as a dependency to qualify, not a result to advertise.
