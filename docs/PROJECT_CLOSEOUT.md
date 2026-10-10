# Project closeout

**Status: engineering portfolio release complete.**

This release presents Alvaro Mendizabal's work on an auditable medical-imaging ML research system. It closes the public portfolio work with runnable examples, tests, aggregate evidence and explicit limitations.

## Delivered scope

| Deliverable | Review path |
|---|---|
| Concise project and ownership narrative | [README](../README.md), [employer review guide](EMPLOYER_REVIEW_GUIDE.md), [case study](EMPLOYER_CASE_STUDY.md) |
| System design and evidence boundaries | [Architecture](ARCHITECTURE.md), [reproduction guide](REPRODUCIBILITY.md) |
| Offline CPU engineering pipeline | [Public pipeline](../examples/run_public_pipeline.py): synthetic grouped data, twelve logistic outputs, validated checkpoints and HTML reporting |
| Testable aggregate evidence | [Dated report](../reports/current_frontier/results.json), [Notebook 14](../notebooks/14_winner_transfer_and_context_modeling.ipynb), [notebook verifier](../scripts/verify_review_notebook.py) |
| Release controls | Hash-locked dependencies, public tests, CI workflows and [publication procedure](GIT_PUBLICATION.md) |

The public pipeline demonstrates scanner-group isolation, training-only normalization, held-out evaluation, atomic fold checkpoints, cache validation and recovery. It labels its data and outputs **SYNTHETIC_ONLY**. Running it does not require or produce patient data, MRI inference or evidence for the private research metrics.

## Recorded research outcomes

The retained aggregate snapshot covers verified research through Stage 104. On the same 4,349-study scanner-grouped development population, ordered context moved macro ROC-AUC from **0.7943834 to 0.7978448**. The later neighbor-context estimate of **0.7978946** had an incremental paired interval crossing zero and remains inconclusive.

The historical external **0.943** macro ROC-AUC record is reported separately. Internal development metrics, engineering parity checks, anatomy reference segmentation and synthetic demo metrics are different evidence classes. None is a substitute for another.

Negative experiments and unsuccessful hypotheses remain part of the record. Keeping them makes the selection process visible and avoids presenting every completed engineering task as a predictive improvement.

## Authored contribution

The work includes data and evaluation contracts, experiment design, integration of existing model families, controlled representation studies, cloud execution and recovery, artifact provenance, tests, and the public review layer. Existing frameworks and pretrained architectures are external components; their integration is distinguished from original architecture authorship.

Private execution evidence is summarized through public-safe aggregates. Raw MRI/DICOM data, identifiers, row-level research outputs, checkpoints, private runtimes and exact competition inference logic are outside the release.

## Completion and limits

Completion refers to the portfolio deliverables and their documented public checks. Full raw-image test serving is not established, a new submission is not claimed, and this release is not a clinical product. The labeled audit rows in the retained research record do not constitute an untouched confirmation cohort.

Historical reports and older notebooks retain their original dates and language, including references to experiments that were prepared at that time. They are preserved records, not a current roadmap or a promise of continued private research. This closeout defines the release scope while preserving the recorded research findings.

Future repository maintenance can address public documentation, dependency compatibility or defects in the runnable examples. Such maintenance should preserve the evidence boundary and the historical interpretation of results.
