# Employer case study

## Executive summary

This project demonstrates end-to-end ownership of a difficult medical-imaging ML research system: data lineage, grouped validation, heterogeneous deep-learning inference, cloud execution, failure recovery, numerical-parity testing, experiment governance, and a controlled research program for adding new spatial supervision.

The strongest verified external result retained in the public project record is **0.943 macro ROC-AUC** across twelve knee-MRI findings.

The most important portfolio signal is not one model architecture. It is the way the project turns an evolving research problem into a reproducible engineering system with explicit evidence boundaries.

## Problem

Knee MRI studies are heterogeneous:

- multiple planes and sequences;
- varying slice counts and spacing;
- target-specific pathology visibility;
- incomplete mirrored acquisitions;
- multi-label outputs with unequal difficulty.

A robust system needs more than image classification. It needs controlled study-level aggregation, exact input identity, validation that respects scanner/entity structure, and careful handling of missing acquisitions.

## My ownership

I owned the project across:

- data and metadata contracts;
- DICOM decoding and geometry checks;
- grouped/scanner-aware validation;
- image-model and residual experiments;
- heterogeneous parent reconstruction;
- GPU/CPU execution design;
- checkpoint and artifact lineage;
- cloud storage/recovery;
- runtime observability and cost controls;
- regression testing and resumability;
- experiment promotion/closure decisions;
- public/private reproducibility design.

## Core constraints

### Validation
Internal development evidence could not be represented as identical to the external evaluation. Later lineage work also showed that the fully labeled audit set had historical selection exposure for recovered components.

### Data
The scoped mirror was incomplete: not every declared acquisition was available for each study.

### Infrastructure
Large checkpoints and image artifacts had to coexist with tight local disk headroom on SageMaker Studio.

### Reproducibility
Completed expensive work needed to survive later-stage failures without being recomputed.

### Publication
The repository needed to demonstrate engineering depth without publishing restricted MRI, identifiers, private checkpoints, or competitive implementation details.

## Approach

### 1. Establish a validation contract
I built a grouped research boundary with scanner-disjoint folds and kept external performance separate from internal model-selection metrics.

### 2. Test representation hypotheses
I evaluated target-specific residuals, fixed spatial bias, foundation-model transfer, and paired image-model routes under explicit controls.

Negative results were preserved when the hypothesis failed.

### 3. Reconstruct the heterogeneous parent
Rather than continue optimizing surrogate systems, I restored the trained parent branches:

- native DINO ensemble;
- RadImageNet-family heads/layouts;
- five A5 folds;
- Raptor views;
- CoAt-family checkpoints and inference.

I also preserved the fixed fitted numerical fusion/calibration graph rather than casually refitting it.

### 4. Make recovery resumable
Large model assets were stored privately and content-addressed. Valid completed units were reused. Input signatures determined which branches needed recomputation after source changes.

### 5. Audit validation and acquisition lineage
I explicitly checked which studies were usable for independent claims and which acquisitions were actually present.

### 6. Test physical-geometry failure modes
A bounded DICOM geometry screen inspected thousands of real headers and closed that hypothesis when no actionable defect appeared.

### 7. Introduce a genuinely new capability
The next research direction became supervised anatomy-aware localization and visibility-conditioned evidence, because generic attention, multi-plane context, medical pretraining, and ensemble diversity were already represented in the parent.

## Key decisions

| Decision | Evidence | Outcome |
|---|---|---|
| Retain narrow residual modeling | Positive grouped development movement | Preserved as development challenger |
| Expand fixed spatial branch | Negative aggregate screen | Closed |
| Expand frozen orthopedic foundation features | Negative matched screen | Closed |
| Treat partial inputs as complete parent | Acquisition audit showed missing series | Rejected |
| Assume fully labeled rows are untouched | Selection lineage contradicted this | Rejected |
| Correct DICOM ordering/geometry | 2,287-header audit found zero flags | Closed for inspected scope |
| Add another generic backbone | Parent already contains strong diversity | Deprioritized |
| Qualify anatomy-aware transfer | Missing capability + source evidence | Advanced to gated reference pilot |

## Engineering highlights

### Resumability
Each expensive unit is independently reusable. A later failure does not erase earlier valid work.

### Numerical parity
Optimizations are accepted only after source-versus-optimized output differences pass explicit tolerances.

### Failure regression
Avoidable failures become deterministic regression tests before the next expensive run.

### Resource engineering
The project uses:

- private S3 for large assets;
- RAM/checkpoint streaming;
- local-disk safety reserves;
- bounded worker counts;
- GPU memory gates;
- representative short performance benchmarks;
- timestamped resource/cost telemetry.

### Evidence discipline
A successful run is not automatically a promoted model. Engineering parity, internal development improvement, and external performance are separate lifecycle states.

## Technical stack

**Languages / core:** Python, Jupyter.

**ML / CV:** PyTorch, scikit-learn, DINO-style encoders, CoAtNet-family architectures, medical-image pretraining, residual modeling, calibration, ensembling.

**Medical imaging:** DICOM metadata and geometry, multi-plane MRI, 2.5D/3D representations, anatomy localization, segmentation transfer.

**Cloud:** AWS SageMaker, S3, GPU inference, private artifact storage.

**Engineering:** deterministic tests, resumable runners, manifests, structured telemetry, CI publication gates, public/private artifact controls.

## Outcomes

Verified public-safe outcomes include:

- external macro ROC-AUC record: **0.943**;
- 4,407-study canonical cache;
- scanner-disjoint grouped research boundary;
- 20 native trained members restored;
- 5 A5 folds restored;
- 4 Raptor diagnostic views executed;
- 7 CoAt-family trained predictions executed after 8 source/checkpoint gates;
- 7-unit validation/acquisition audit completed;
- 2,287-header geometry audit completed with zero flags;
- 4-track pretrained anatomy qualification completed.

The current public state intentionally stops before claiming segmentation quality or downstream anatomy-conditioned disease improvement that has not yet been measured.

## What this demonstrates to an employer

- ownership across the full ML lifecycle;
- research judgment under imperfect evidence;
- ability to debug and recover complex model systems;
- production-aware cloud engineering;
- validation/leakage discipline;
- resource and cost awareness;
- high-quality technical communication;
- willingness to close weak ideas;
- ability to protect sensitive/private implementation while still making work reviewable.

## Review path

For a fast review: README → this case study → Notebook 13.

For ML engineering depth: add Architecture + Reproducibility + Parent Reconstruction.

For research depth: add Research Timeline + Anatomy-Aware Transfer Program.
