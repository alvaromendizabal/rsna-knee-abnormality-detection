# Anatomy-aware transfer program

## Research question

Once the scored parent was treated as the control rather than replaced by a surrogate, the core question became:

> **What capability is still materially missing from a system that already has attention, medical pretraining, depth information, multi-plane aggregation, multiple resolutions, and model diversity?**

A review of strong medical-imaging systems repeatedly pointed to:

**explicit anatomical localization, visibility-aware supervision, and local evidence fused with global context.**

The goal is not to copy another solution literally. The goal is to translate durable mechanisms into a knee-specific, leakage-aware experiment.

## Recurring mechanisms

### Coarse-to-fine localization
Learn where useful anatomy is, concentrate downstream capacity on that evidence, and retain global context so local crops do not erase important information.

### Visibility-aware supervision
Structure visibility is not pathology presence. Auxiliary supervision must be masked where labels are unknown or non-exhaustive, and local evidence should be aggregated only when the relevant structure is visible.

### Local + global fusion
Localized evidence should complement, not replace, study-level context.

### Multiple localization hypotheses
Localization can be uncertain. A robust path can preserve a small fixed set of plausible regions rather than collapsing immediately to one coordinate.

### Segmentation-pretrained local specialists
Dense anatomical supervision can yield more task-useful local features than generic frozen embeddings, but only after geometry, source, and validation contracts are qualified.

## Why this differs from earlier spatial experiments

An earlier fixed spatial branch was a scientific negative.

That experiment answered a narrower question: does generic fixed spatial bias add enough complementary signal?

It did **not** test learned, annotation-supervised anatomy.

The current program therefore treats generic attention, fixed regions, and supervised localization as distinct hypotheses.

## Current qualification state

The project has completed the metadata/geometry qualification stage for a public pretrained knee-anatomy candidate.

Verified public-safe evidence:

- two pretrained checkpoint metadata payloads were inspected;
- both identify a full-resolution 3D configuration;
- nine foreground anatomy labels are represented;
- three image-coordinate adapters were validated;
- exact parent fallback was checked against ten saved component arrays;
- no trained segmentation Dice or downstream disease AUC is claimed yet.

This candidate is **qualified for a bounded reference pilot**, not promoted.

See [Anatomy model qualification](ANATOMY_MODEL_QUALIFICATION.md).

## Controlled downstream design

### A0 — unchanged parent
The scored parent remains the control.

### A1 — matched global-only residual
Add comparable trainable capacity without anatomy.

### A2 — anatomical regional pooling
Use the same residual branch with supervised anatomical regions. A2 minus A1 isolates localization rather than the value of adding another model.

### A3 — visibility-aware auxiliary supervision
Add masked anatomical/visibility supervision to A2. A3 minus A2 isolates the auxiliary-supervision contribution.

### A4 — fixed multiple proposals
Reuse A3 weights and combine a small fixed set of localization proposals. A4 minus A3 isolates proposal uncertainty without another fit.

## Parent-preserving fallback

Low-confidence or unavailable anatomical evidence must fall back exactly to the parent.

Public-safe qualification code in src/rsna_research/anatomy_qualification.py captures the same philosophy:

- finite bounded segmentation metrics;
- predeclared reference-quality thresholds;
- exact fallback equality;
- explicit lifecycle states.

The competitive feature/fusion implementation remains private.

## External supervision principles

Candidate anatomical sources are useful only when their images, labels, and transforms are valid for the intended experiment.

Required checks include legitimate image access/licensing, source provenance, overlap audit, conservative pathology taxonomy, exact annotation-to-image pairing, transform tracking, and unknown labels preserved as unknown.

A missing annotation is never treated as proof that pathology is absent.

## Validation principles

The primary competition metric remains unweighted macro ROC-AUC across twelve targets.

Important rules:

- compare matching subjects and targets;
- keep grouped/scanner boundaries intact;
- fit learned preprocessing only in the proper training partition;
- use paired evidence for parent-versus-challenger comparisons;
- retain valid small positive aggregate movement as evidence;
- inspect target-level regressions and fold dispersion;
- reject leakage or provenance violations regardless of apparent score.

The fully labeled audit set has historical selection exposure for recovered components and is not described as untouched confirmation.

## What stays private

The public repository describes the research contract, not the competitive implementation.

Private details include exact fusion weights, row-level predictions, private checkpoints, cloud/source handles, sensitive training schedules, competition-specific inference code, and unreleased localization heuristics.

## Employer-facing takeaway

This program demonstrates a deliberate ceiling-escape process:

1. audit what the incumbent already contains;
2. research mechanisms rather than model brands;
3. identify a genuinely missing capability;
4. qualify external components before expensive integration;
5. translate the capability into matched controls;
6. preserve exact fallback behavior;
7. keep validation provenance stricter than the modeling idea itself.
