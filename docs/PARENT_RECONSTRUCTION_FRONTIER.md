# Parent reconstruction frontier

## Why this phase mattered

The project originally explored several owned research systems on a grouped AWS validation boundary. That work produced useful complementary components and negative results, but it was not the same thing as reconstructing the scored multi-branch parent.

The current program therefore treats the verified parent as an engineering system with multiple trained branches, preprocessing contracts, fusion logic, and input signatures that must be restored coherently.

The objective is **not** to publish private weights or reproduce the entire competition implementation in Git. The objective is to make the engineering approach legible:

1. recover the source-defined branch contracts;
2. validate trained-state loading;
3. reproduce preprocessing and inference behavior;
4. compare optimized execution against the original routine;
5. preserve outputs behind immutable input signatures;
6. recover missing private assets without duplicating completed work;
7. assemble the parent only when branch inputs are compatible.

## Reconstructed branch families

### Native DINO branch

The native image branch was restored as a multi-member ensemble with:

- **20 trained members**;
- **200 member/window evaluations**;
- source-matched image selection and preprocessing;
- strict fingerprint checks;
- checkpoint streaming rather than local checkpoint accumulation;
- reuse of completed member/window outputs.

A shared-computation optimization was accepted only after probability-level parity checks showed negligible numerical movement.

### RadImageNet-family branch

The Rad branch was restored across **three source layouts** and multiple trained heads.

Engineering work included:

- exact image-layout reconstruction;
- source-compatible DICOM decoding;
- strict model-state loading;
- feature reuse across related heads;
- serial-versus-batched parity testing;
- bounded GPU execution.

The optimized path was accepted because its numerical differences stayed inside the parent’s declared tolerance.

### A5 branch

All **five trained A5 folds** were restored.

The recovery path emphasized:

- source-defined image preprocessing;
- isolated image-library dependencies;
- strict state loading;
- reusable readout features;
- fold-level resumability;
- numerical checks between original and optimized batching behavior.

No historical-score claim is inferred from successful state loading alone.

### Raptor and CoAt families

The next recovery phase restored the three Raptor checkpoints and the principal trained assets for three CoAt-family branches into private encrypted object storage.

About **2.97 GB** of private model/source assets were preserved.

The public repository intentionally does not expose:

- source dataset handles;
- checkpoint hashes;
- private file names where disclosure would reveal competitive implementation;
- model binaries;
- return bundles;
- exact fusion weights.

## Numerical graph reconstruction

The parent is more than a collection of neural networks.

Its source contains fitted numerical logic for:

- branch-specific aggregation;
- rank-based transforms;
- calibration;
- target-specific fusion;
- branch exclusions;
- final target-level weighting.

The reconstruction program treats this logic as immutable fitted state. It is not refit casually during engineering work.

A branch is not considered interchangeable with another branch merely because they share architecture family names.

## Input signatures are part of model identity

A major finding from the reconstruction effort was incomplete raw-acquisition coverage in the mirrored diagnostic population.

That creates a subtle but important reproducibility issue: the same trained branch can produce a different result if later recovery changes the selected source series or slices.

The project therefore records input signatures and applies the following rules:

- partial-input inference is explicitly labeled as partial;
- missing acquisitions are never substituted with a different sequence;
- recovered acquisitions trigger recomputation only for affected branches;
- unaffected outputs remain reusable;
- full-parent claims require compatible branch inputs on the same cohort.

This is a stronger contract than treating a checkpoint filename as the whole model.

## Recovery engineering

The reconstruction work also hardened the operational layer.

Representative safeguards include:

- private encrypted object storage;
- create-only content-addressed recovery;
- bounded disk reserves;
- RAM-streamed checkpoint loading;
- resumable whole-file acquisition;
- dependency isolation;
- cached authentication/session reuse;
- cloud-permission diagnostics that distinguish read, write, and configuration privileges;
- manifest parsing that distinguishes real inputs, historical aliases, and generated outputs.

The design goal is to make later scientific experiments cheaper and more trustworthy by eliminating repeated infrastructure uncertainty.

## What is complete

Verified engineering milestones include:

- source-preserved parent definition;
- Rad branch execution;
- native DINO execution;
- five A5 fold executions;
- fitted numerical-graph reconstruction;
- private recovery of the major Raptor assets;
- private recovery of the principal trained assets for three CoAt families;
- signature-aware reuse contracts.

## What remains

The remaining parent-completion work is narrower:

- resolve one remaining repair-family source;
- execute Raptor under the appropriate input scope;
- review and execute recovered CoAt runtime code;
- recover missing acquisitions when permitted;
- recompute only branches whose selected inputs change;
- assemble all branches on a compatible cohort;
- establish a legitimate aligned evaluation population.

Only after that boundary is stable should new anatomy-aware branches be interpreted as improvements to the parent rather than improvements to a surrogate.

## Employer-facing takeaway

This phase demonstrates system-level ML engineering rather than isolated model training:

- reverse-engineering a heterogeneous inference graph;
- restoring multiple trained model families;
- designing numerical-parity gates;
- preserving lineage and input identity;
- streaming large artifacts under storage pressure;
- making failure recovery resumable;
- separating public reproducibility from private competition assets.

That engineering foundation is what makes the next research phase scientifically meaningful.
