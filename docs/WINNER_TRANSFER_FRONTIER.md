# Winner-transfer research frontier

## Why this exists

Once a medical-imaging system already includes multiple pretrained encoders, attention, multi-plane evidence and ensemble diversity, progress should not default to arbitrary architecture churn.

This project therefore treats prior high-performing medical-imaging solutions as a **capability inventory**:

**research → normalize mechanisms → map current coverage → rank gaps → controlled transfer experiment**

The objective is to acquire useful capabilities, not copy competition code.

## Audit breadth

The current public-safe inventory contains:

- **9 prior competitions**
- **15 independent top/winning solution lineages**
- **37 normalized mechanism families**

The reviewed work spans classification, detection, segmentation, multi-label prediction, slice-sequence aggregation, anatomical localization, volumetric modeling, and weak supervision.

## Repeated mechanism families

Recurring patterns include:

- anatomical localization / ROI routing;
- auxiliary segmentation or localization;
- adjacent-slice or sequence context;
- study-level aggregation;
- multi-view / multi-plane fusion;
- domain-specific pretraining;
- fold/model diversity;
- label-noise or pseudo-label handling;
- visibility-conditioned evidence;
- coarse-to-fine inference.

Repeated appearance is evidence, not proof that a mechanism transfers unchanged to knee MRI.

## Current capability coverage

Among **29 high-confidence transferable mechanisms**:

| Status | Count |
|---|---:|
| Fully implemented | **8** |
| Partially implemented | **11** |
| Missing | **6** |
| Blocked | **4** |

This is a research checklist, not a percentage of winning performance reproduced.

## What the inventory changed

The audit changed the project from “try another model” into a mechanism-driven queue.

Cross-slice context was promoted because it appeared repeatedly in strong medical-imaging solutions and addressed a real study-level representation gap. Generic backbone swaps were deprioritized because the parent already had representation diversity. Learned anatomical localization remains high-value but is constrained by supervision legitimacy.

## Evidence ladder

Transfer candidates are ranked using:

1. repeated use across independent strong solutions;
2. documented ablation in a high-performing solution;
3. success in an analogous MRI/3D task;
4. success in related medical imaging;
5. peer-reviewed evidence;
6. strong internal error-analysis motivation;
7. speculative but mechanism-backed ideas.

## What has transferred successfully

### Cross-slice context

The full-cohort grouped research result improved:

- retained system: **0.7943834**
- sequence-context system: **0.7978448**

### Neighbor-context extension

A later correction reached **0.7978946**, but paired uncertainty crossed zero.

Decision:

- preserve the point estimate;
- do not claim the mechanism is established;
- close micro-tuning of the exact tested configuration.

## What remains strategically important

Public-safe high-level gaps still include:

- learned anatomy-aware localization with a global fallback;
- visibility-aware auxiliary supervision;
- training-side robustness to weak labels;
- target-specific evidence routing;
- stronger local 3D evidence when supervision and compute justify it.

Some remain blocked by trustworthy-supervision constraints. A high priority does not override an invalid experiment.

## Public/private boundary

Public GitHub contains mechanism families, aggregate outcomes, ranking logic, and decision rules.

Private AWS retains exact adaptations, model weights, study-level predictions, training artifacts, source handles, and competition inference/submission logic.
