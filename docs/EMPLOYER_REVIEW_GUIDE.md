# Employer review guide

This repository is intentionally deep. This page gives reviewers a fast path based on role.

## Recruiter / talent partner — 2 minutes

Read:

1. README — 30-second overview and evidence table.
2. Employer Case Study — executive summary, ownership, outcomes.
3. Notebook 13 — visual summary of the current research frontier.

Key signal: **end-to-end ownership of a complex medical-imaging ML system on AWS.**

## ML engineering manager — 10 minutes

Read:

1. System Architecture
2. Parent Reconstruction Frontier
3. Reproducibility Boundary
4. Project Status

Look for:

- resumability;
- checkpoint and input lineage;
- numerical-parity gates;
- GPU/storage/resource engineering;
- failure regression;
- cloud artifact design;
- CI/publication controls.

## Applied scientist / data scientist — 15 minutes

Read:

1. Research Timeline
2. Anatomy-Aware Transfer Program
3. Anatomy Model Qualification
4. AWS Research Frontier
5. Notebook 13

Look for:

- leakage-aware validation;
- matched controls;
- negative-result discipline;
- mechanism-driven research;
- explicit lifecycle/promotion gates;
- uncertainty around validation membership;
- separation of engineering parity from predictive evidence.

## Interview discussion map

### “Tell me about a technically difficult ML project.”
Use the parent reconstruction story: multiple model families, fixed fusion logic, incomplete inputs, storage pressure, and source/runtime parity.

### “How do you avoid overfitting your experiments?”
Use scanner-disjoint grouped validation, selection-lineage audits, matched controls, frozen gates, and retention of negative results.

### “How do you design reliable ML infrastructure?”
Use resumable units, immutable manifests, content-addressed assets, telemetry, resource/cost guards, regression fixtures, and one-return packaging.

### “How do you decide what to try next?”
Use the missing-capability analysis: the parent already contained generic attention and representation diversity, so research moved toward supervised anatomical localization rather than another backbone swap.

### “How do you handle failed experiments?”
Show Stage 80, Stage 83, and Stage 95. Correct execution + negative evidence is preserved as a successful scientific result.

### “How do you balance reproducibility with sensitive/private work?”
Use the AWS-canonical / GitHub-curated split and the automated privacy/publication gates.

## What is intentionally not public

The repository does not expose raw MRI, identifiers, row-level predictions, checkpoints, private source handles, private runners, or exact competition fusion logic.

That boundary is part of the engineering design, not missing documentation.
