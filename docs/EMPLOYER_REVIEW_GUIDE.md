# Employer review guide

This repository is intentionally deep. This page gives reviewers a fast path based on role.

## Recruiter / talent partner — 2 minutes

Read:

1. [README](../README.md)
2. [Employer Case Study](EMPLOYER_CASE_STUDY.md)
3. [Notebook 14](../notebooks/14_winner_transfer_and_context_modeling.ipynb)

Key signal: **end-to-end ownership of a complex medical-imaging ML research system on AWS.**

## ML engineering manager — 10 minutes

Read:

1. [System Architecture](ARCHITECTURE.md)
2. [Reproducibility Boundary](REPRODUCIBILITY.md)
3. [Project Status](PROJECT_STATUS.md)
4. [Parent Reconstruction Frontier](PARENT_RECONSTRUCTION_FRONTIER.md)

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

1. [Research Timeline](RESEARCH_TIMELINE.md)
2. [Context Modeling Frontier](CONTEXT_MODELING_FRONTIER.md)
3. [Winner Transfer Frontier](WINNER_TRANSFER_FRONTIER.md)
4. [Anatomy-Aware Transfer Program](ANATOMY_AWARE_TRANSFER_PROGRAM.md)
5. [Notebook 14](../notebooks/14_winner_transfer_and_context_modeling.ipynb)

Look for:

- leakage-aware grouped validation;
- matched controls;
- paired uncertainty;
- negative-result discipline;
- mechanism-driven research;
- explicit promotion/closure gates;
- separation of engineering parity from predictive evidence;
- winner-derived capability ranking before compute spend.

## Hands-on review — 5 minutes after environment setup

1. Run the [synthetic example](../examples/run_public_review.py): it exercises the public twelve-target metric, rejects invalid submission inputs, and keeps a positive but uncertain increment inconclusive.
2. Follow [the replay commands](REPRODUCIBILITY.md) to regenerate the three recent aggregate notebooks in a clean kernel.
3. Inspect the [current aggregate report](../reports/current_frontier/results.json) and [source/output verifier](../src/rsna_review/evidence.py).

The synthetic fixture's 0.75 AUC is illustrative and is never a project result. The 0.943 external record and grouped development values remain separate. Complete reviewability at Stage 104 does not claim full parent parity, clinical deployment, or completion of the prepared Stage 105 experiment.

## Interview discussion map

### “Tell me about a technically difficult ML project.”
Use the parent reconstruction + sequence-modeling story: heterogeneous model families, fixed fusion logic, incomplete inputs, storage pressure, source/runtime parity, and a controlled full-cohort research improvement.

### “How do you avoid overfitting experiments?”
Use scanner-grouped validation, selection-lineage audits, matched controls, fixed evaluation rules, paired uncertainty, and retention of negative/inconclusive results.

### “How do you design reliable ML infrastructure?”
Use resumable units, immutable manifests, content-addressed assets, telemetry, resource/cost guards, regression fixtures, and one-return packaging.

### “How do you decide what to try next?”
Use the Winner Technique Inventory: audit strong prior solutions, normalize mechanism families, map capability gaps, rank them, then run bounded controlled transfers.

### “Give an example of a modeling idea that actually helped.”
Use Stage 102 cross-slice context: the same 4,349-study grouped research metric moved from **0.7943834 to 0.7978448**.

### “Give an example of not overclaiming.”
Use Stage 104: the point estimate rose to **0.7978946**, but the paired interval crossed zero, so it was preserved as inconclusive rather than promoted.

### “How do you balance reproducibility with sensitive/private work?”
Use the AWS-canonical / GitHub-curated split and the automated privacy/publication gates.

## What is intentionally not public

The repository does not expose raw MRI, identifiers, row-level predictions, checkpoints, private source handles, private runners, cloud paths, or exact competition fusion/inference logic.

That boundary is part of the engineering design, not missing documentation.
