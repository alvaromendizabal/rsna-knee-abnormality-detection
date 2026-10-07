# Employer case study

## Executive summary

This project demonstrates end-to-end ownership of a difficult medical-imaging ML research system: data lineage, grouped validation, heterogeneous deep-learning reconstruction, anatomy-aware representation learning, winner-informed sequence modeling, cloud execution, failure recovery, numerical-parity testing, experiment governance, and public/private reproducibility controls.

The strongest verified external result retained in the public project record is **0.943 macro ROC-AUC** across twelve knee-MRI findings.

The strongest portfolio signal is the system of evidence, not one architecture.

## My ownership

I owned the project across:

- data and metadata contracts;
- DICOM decoding and geometry checks;
- scanner-grouped validation;
- image-model and residual experiments;
- heterogeneous parent reconstruction;
- anatomy-model qualification;
- cross-slice sequence modeling;
- winner-solution research and capability mapping;
- GPU/CPU execution design;
- checkpoint/artifact lineage;
- cloud storage and recovery;
- observability and cost controls;
- regression testing and resumability;
- model promotion/closure decisions;
- public/private reproducibility design.

## Core constraints

**Validation:** internal development evidence is not represented as identical to external evaluation.

**Data:** the scoped mirror has incomplete acquisitions.

**Infrastructure:** large checkpoints and image artifacts must coexist with tight local disk headroom on SageMaker.

**Reproducibility:** completed expensive work must survive later-stage failures.

**Publication:** the repository must demonstrate depth without publishing MRI, identifiers, row-level predictions, private weights, or exact competition implementation.

## Approach

### 1. Establish a validation contract
Scanner-grouped folds and explicit evidence classes prevent leakage and score-setting confusion.

### 2. Preserve negative results
Fixed spatial bias, frozen foundation transfer, and a geometry-defect hypothesis were retained as valid negative evidence rather than tuned until favorable.

### 3. Reconstruct the heterogeneous parent
The major trained branches were restored while preserving the fitted numerical aggregation/calibration.

### 4. Make recovery resumable
Large private artifacts are content-addressed and completed work is reused.

### 5. Audit acquisition and selection lineage
The project explicitly identified incomplete inputs and historical selection exposure instead of inventing clean validation membership.

### 6. Qualify anatomy
A pretrained knee-anatomy route passed a nine-structure reference pilot with mean Dice above 0.91. Native-transfer truth remains limited.

### 7. Import a proven mechanism instead of swapping another backbone
A mandatory review of prior strong medical-imaging solutions produced a capability inventory. Cross-slice context emerged as a credible gap.

The full-cohort grouped research comparison improved from **0.7943834 to 0.7978448**.

### 8. Treat uncertainty as part of the decision
A later explicit neighbor-context extension reached **0.7978946**, but its paired interval crossed zero.

Decision: preserve the result, do not over-promote it, and move to a materially different capability.

## Key decisions

| Decision | Evidence | Outcome |
|---|---|---|
| Expand fixed spatial branch | Negative aggregate screen | Closed |
| Expand frozen orthopedic foundation features | Negative matched screen | Closed |
| Treat partial acquisitions as complete | Acquisition audit contradicted this | Rejected |
| Treat fully labeled audit rows as untouched | Selection lineage contradicted this | Rejected |
| Correct DICOM ordering/geometry | 2,287-header audit found zero flags | Closed for inspected scope |
| Add another generic backbone | Parent already contains strong diversity | Deprioritized |
| Qualify anatomy transfer | Reference segmentation gate passed | Preserved enabling capability |
| Add ordered cross-slice context | Full-cohort grouped improvement | Retained |
| Promote tiny Stage 104 increment | Paired interval crossed zero | Not promoted |
| Choose future experiments ad hoc | Winner inventory now exists | Replaced by ranked capability process |

## Engineering highlights

### Resumability
Each expensive unit is independently reusable.

### Numerical parity
Optimizations and exports are accepted only after explicit output-equivalence gates.

### Failure regression
Avoidable failures become deterministic tests before another cost-bearing run.

### Resource engineering
The system uses private object storage, streaming/checkpoint recovery, disk reserves, GPU memory gates, bounded execution, and cost telemetry.

### Evidence discipline
A successful run is not automatically a promoted model. Engineering parity, development movement, uncertainty, and external performance are separate lifecycle states.

### Winner-informed prioritization
The public-safe capability inventory spans **9 competitions, 15 top-solution lineages, and 37 technique families**.

## Technical stack

**Core:** Python, Jupyter, PyTorch, scikit-learn.

**Medical imaging:** DICOM metadata/geometry, multi-plane MRI, 2.5D/3D representations, anatomy localization, segmentation transfer.

**Cloud:** AWS SageMaker, S3, GPU inference, private artifact storage.

**Engineering:** deterministic tests, resumable runners, manifests, telemetry, CI publication gates.

## Outcomes

- external macro ROC-AUC record: **0.943**
- 4,407-study canonical cache
- scanner-disjoint grouped research boundary
- heterogeneous parent branches restored
- 2,287-header geometry audit with zero flags
- nine-structure anatomy reference qualification above 0.91 mean Dice
- full-cohort context-modeling gain from **0.7943834 to 0.7978448**
- inference/export parity qualification
- Stage 104 point estimate **0.7978946**, correctly retained as inconclusive
- Winner Technique Inventory covering **9 competitions / 15 lineages / 37 mechanism families**

## What this demonstrates to an employer

- ownership across the full ML lifecycle;
- research judgment under imperfect evidence;
- ability to debug and recover complex model systems;
- production-aware cloud engineering;
- validation/leakage discipline;
- cost awareness;
- rigorous negative-result handling;
- ability to translate external research into controlled internal experiments;
- strong technical communication;
- protection of sensitive implementation while keeping work reviewable.

## Review path

Fast review: [README](../README.md) → this case study → [executed Notebook 14](../notebooks/14_winner_transfer_and_context_modeling.ipynb).

Hands-on review: [synthetic metric example](../examples/run_public_review.py) and [pinned notebook replay](REPRODUCIBILITY.md). The public portfolio is complete through Stage 104; the prepared next private experiment remains unexecuted in this publication.

ML engineering depth: Architecture + Reproducibility + Project Status.

Research depth: Context Modeling Frontier + Winner Transfer Frontier + Research Timeline.
