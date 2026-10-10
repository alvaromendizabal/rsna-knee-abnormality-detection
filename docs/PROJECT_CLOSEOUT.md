# Project closeout

**Status: engineering portfolio release complete.**

This release presents Alvaro Mendizabal's work on an auditable medical-imaging ML research system. It closes the public portfolio work with runnable examples, tests, aggregate evidence and explicit limitations.

## Delivered scope

| Deliverable | Review path |
|---|---|
| Concise project and ownership narrative | [README](../README.md), [employer review guide](EMPLOYER_REVIEW_GUIDE.md), [case study](EMPLOYER_CASE_STUDY.md) |
| System design and evidence boundaries | [Architecture](ARCHITECTURE.md), [reproduction guide](REPRODUCIBILITY.md) |
| Interactive browser trainer | [Browser demo](https://alvaro-rsna-engineering-lab.tartmacaw2.chatgpt.site): generated cohort, actual logistic training, fold progress, pause/resume and result export |
| Offline CPU engineering pipeline | [Public pipeline](../examples/run_public_pipeline.py): synthetic grouped data, twelve logistic outputs, validated checkpoints and HTML reporting |
| Testable aggregate evidence | [Dated report](../reports/current_frontier/results.json), [Notebook 14](../notebooks/14_winner_transfer_and_context_modeling.ipynb), [notebook verifier](../scripts/verify_review_notebook.py) |
| Release controls | Hash-locked dependencies, public tests, CI workflows and [publication procedure](GIT_PUBLICATION.md) |

I built the browser trainer to make learning and held-out evaluation directly inspectable. I built the CPU pipeline to expose scanner-group isolation, training-only normalization, atomic fold checkpoints, cache validation and recovery. It labels its data and outputs **SYNTHETIC_ONLY**. Running it does not require or produce patient data, MRI inference or evidence for the private research metrics.

## Recorded research outcomes

The retained aggregate snapshot covers verified research through Stage 104. On the same 4,349-study scanner-grouped development population, ordered context moved macro ROC-AUC from **0.7943834 to 0.7978448**. The later neighbor-context estimate of **0.7978946** had an incremental paired interval crossing zero and remains inconclusive.

The historical external **0.943** macro ROC-AUC record is reported separately. Internal development metrics, engineering parity checks, anatomy reference segmentation and synthetic demo metrics are different evidence classes. None is a substitute for another.

Negative experiments and unsuccessful hypotheses remain part of the record. Keeping them makes the selection process visible and avoids presenting every completed engineering task as a predictive improvement.

## Authored contribution

I designed the data and evaluation contracts, ran controlled representation studies, integrated the model families, and built cloud execution, recovery, artifact provenance, tests and the public review layer. The [source record](SOURCES.md) preserves credits for the frameworks, pretrained architectures and published methods used in the system.

Private execution evidence is summarized through public-safe aggregates. Raw MRI/DICOM data, identifiers, row-level research outputs, checkpoints, private runtimes and tuned research inference logic are outside the release.

## Completion and limits

Completion refers to the portfolio deliverables and their documented public checks. Full raw-image test serving is not established, this release is not a clinical product. The labeled audit rows in the retained research record do not constitute an untouched confirmation cohort.

Historical reports and older notebooks retain their original dates and language, including references to experiments that were prepared at that time. They are preserved records, not a current roadmap or a promise of continued private research. This closeout defines the release scope while preserving the recorded research findings.

Future repository maintenance can address public documentation, dependency compatibility or defects in the runnable examples. Such maintenance should preserve the evidence boundary and the historical interpretation of results.
