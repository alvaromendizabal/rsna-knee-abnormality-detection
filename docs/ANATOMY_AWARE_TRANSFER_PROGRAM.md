# Anatomy-aware transfer program

## Research question

Once the scored parent was treated as the control rather than replaced by a surrogate, the next question became:

> **What capability is still materially missing from a system that already has attention, medical pretraining, slice/depth information, multi-plane aggregation, multiple resolutions, and model diversity?**

A review of strong prior medical-imaging systems pointed repeatedly to the same answer:

**explicit anatomical localization, visibility-aware supervision, and local evidence fused with global context.**

The goal is not to copy another competition solution literally. The goal is to translate durable mechanisms into a knee-specific, leakage-aware experiment.

## Recurring mechanisms from prior medical-imaging systems

Across prior RSNA and related medical-imaging work, several patterns appeared repeatedly:

### Coarse-to-fine localization
Strong systems often localize a clinically relevant structure or region before asking the final classifier to solve the full task.

The transfer principle is:

- learn where useful anatomy is;
- concentrate high-capacity classification on that evidence;
- retain global context so local crops do not remove important information.

### Visibility-aware supervision
A structure being visible is not the same as a pathology being present.

Useful systems model this explicitly by:

- learning or estimating visibility;
- masking auxiliary losses where supervision is unknown;
- aggregating evidence only where the relevant structure is present;
- avoiding the assumption that an unannotated region is a disease negative.

### Local + global fusion
Localized evidence is strongest when combined with global context.

For knee MRI this supports:

- region-conditioned features;
- global study context;
- target-specific fusion rather than one universal spatial policy.

### Multiple localization hypotheses
Localization itself can be uncertain.

Instead of collapsing immediately to one predicted point or box, a robust inference path can preserve a small number of plausible regions and combine their downstream evidence.

### Segmentation-pretrained local specialists
Dense anatomical supervision can make local features more useful than generic pretrained embeddings.

This remains a later-stage direction because it requires compatible labeled anatomy and a stronger geometry/data contract.

## Why this is different from earlier spatial experiments

An earlier fixed spatial branch was a scientific negative.

That experiment answered a narrower question:

> does generic fixed spatial bias add enough complementary signal?

It did not establish whether **learned, annotation-supervised anatomy** can help.

The current program therefore avoids claiming that generic attention and supervised localization are interchangeable.

## Current priority order

### 1. Anatomy-localized global/local residual
Immediate priority.

Concept:
- preserve the parent prediction;
- attach a small residual path;
- compare a matched global-only branch against the same branch with anatomical region pooling;
- isolate the value of localization rather than the value of adding another model.

### 2. Visibility-aware auxiliary supervision
Immediate priority.

Concept:
- add an auxiliary task only where spatial labels are valid;
- mask unknown or non-exhaustive labels;
- use visibility to control local evidence aggregation;
- retain study-level disease supervision for the primary task.

### 3. Cross-plane anatomical consistency and localization uncertainty
High priority.

Concept:
- use physical geometry where supported;
- link evidence across sagittal/coronal/axial views;
- preserve more than one plausible region when localization confidence is limited.

### 4. Segmentation-pretrained local 3D specialist
Conditional later priority.

Prerequisites:
- compatible 3D inputs;
- legitimate anatomical labels;
- validated geometry;
- memory/throughput benchmark on the available GPU.

## Experimental discipline

The anatomy-aware program is designed to isolate mechanism-level contributions.

Controls should separate:

- adding a new residual branch;
- adding localization;
- adding visibility-aware auxiliary supervision;
- adding multiple localization hypotheses.

Shared preprocessing, seeds, optimization schedules, and trainable capacity should be matched as closely as practical.

Low-confidence or missing localized evidence should fall back toward the parent rather than forcing a new branch to dominate.

## External supervision principles

Candidate anatomical sources are useful only when their images, labels, and transforms are valid for the intended experiment.

The program therefore requires:

- legitimate image access;
- source/version provenance;
- patient/source overlap audit;
- conservative pathology taxonomy;
- exact annotation-to-image pairing;
- transform tracking through crop/flip/resize/slice selection;
- unknown labels preserved as unknown;
- no automatic conversion of broad pathology names into more specific competition targets.

A missing annotation is not treated as proof that pathology is absent.

## Validation principles

The primary metric remains unweighted macro ROC-AUC across all twelve targets.

Important rules:

- compare matching subjects and targets;
- keep grouped/scanner boundaries intact;
- keep learned preprocessing inside the proper training partition;
- use paired evidence for parent-versus-challenger comparisons;
- retain valid small positive aggregate movement as evidence;
- inspect target-level regressions and fold dispersion;
- treat uncertainty intervals crossing zero as inconclusive rather than automatically negative;
- reject any result with leakage, population mismatch, or invalid input identity regardless of apparent score.

## What stays private

The public repository describes the research contract, not the competitive implementation.

Private details include:

- exact model/fusion weights;
- private source handles;
- checkpoint identities;
- row-level predictions;
- sensitive training schedules;
- competition-specific inference code;
- unreleased localization heuristics.

## Employer-facing takeaway

This research program demonstrates a deliberate ceiling-escape process:

1. audit what the incumbent already contains;
2. study strong external systems for mechanisms rather than brands;
3. identify a genuinely missing capability;
4. translate it into a controlled experiment;
5. preserve attribution with matched controls;
6. keep data/validation provenance stricter than the modeling idea itself.

That process is reusable well beyond this competition: it is how a production ML team should decide whether a new architecture or supervision source is actually worth adding to an already strong system.
