# Case study · medical-imaging ML systems

## Executive summary

This project explores twelve findings in knee MRI while treating data identity, evaluation design, and recoverable execution as first-class engineering problems. The work spans Python research tooling, DICOM audits, scanner-grouped validation, heterogeneous PyTorch models, AWS execution, and evidence-based experiment decisions.

The public release gives a reviewer two complementary views: recorded aggregate research evidence and an independently runnable synthetic engineering pipeline. The latter demonstrates contracts and recovery without access to MRI, trained models, or private inference logic.

## My ownership

I designed the research workflow and its validation, execution, and publication controls: data contracts and joins; grouped splits; model reconstruction and numerical-parity checks; resumable artifact handling; experiment interpretation; and the review experience in this repository. The original dataset, pretrained model families, and published methods are external contributions credited in [Sources](SOURCES.md).

## Core constraints

| Constraint | Engineering response |
|---|---|
| Scanner-specific acquisition patterns | Grouped evaluation; audit scanner membership across folds |
| Incomplete source acquisitions | Explicit coverage checks and scoped restoration claims |
| Large artifacts and limited local storage | Reusable work units, manifests, streaming, resource telemetry |
| Repeated development-set inspection | Separate development evidence from independent confirmation |
| Restricted data and private implementation | Publish aggregate evidence and a separate synthetic demonstration |

## Key decisions

| Decision | Evidence | Result |
|---|---|---|
| Preserve scanner separation | 59 scanner groups; zero groups crossing folds | Retained validation boundary |
| Stop fixed spatial and frozen-feature routes | Negative matched comparisons | Avoided further spending on those hypotheses |
| Investigate image geometry | 2,287 headers and 93 decoded images; no flags within scope | Closed that hypothesis for the inspected sample |
| Add ordered cross-slice context | Same 4,349-study development population | Macro AUC improved from 0.7943834 to 0.7978448 |
| Promote a narrow neighbor-context extension | Point estimate 0.7978946; paired interval crossed zero | Retained as inconclusive |
| Claim a fully reconstructed image-to-output system | Compatible input coverage and evaluation independence unresolved | Claim withheld |

## Engineering highlights

**Recoverable execution.** Completed work has a compatibility contract, not just a filename. The [public pipeline](../src/rsna_review/public_pipeline.py) makes this inspectable: deterministic data, train-only normalization, scanner-disjoint folds, atomic checkpoints, content hashes, and resume rejection when inputs or implementation change.

**Numerical and scientific gates.** Schema validation, target ordering, finite probability checks, and paired uncertainty serve different purposes. A successful execution does not establish a meaningful model improvement. [Notebook 14](../notebooks/14_winner_transfer_and_context_modeling.ipynb) retains the inconclusive result and its interval.

**Reviewable evidence.** Hash-locked dependencies and CI execute the synthetic demo and replay three aggregate notebooks. Publication checks also inspect candidate files for restricted artifacts and concrete credential patterns. These controls reduce accidental disclosure; they do not replace a human review.

## Technical stack

- **Research:** Python, Jupyter, PyTorch, scikit-learn; multi-plane DICOM/MRI and anatomy-transfer studies.
- **Infrastructure:** AWS SageMaker, S3, GPU execution, resumable artifacts and resource telemetry.
- **Public review:** NumPy, pandas, pytest, Plotly, Jupyter, HTML/SVG reports, GitHub Actions.

## Outcomes

The recorded external result is **0.943 macro ROC-AUC**. Separately, the grouped development comparison improved by **0.0034614**, from **0.7943834 to 0.7978448**. These evaluation settings are not interchangeable. The 58 fully labeled audit rows are not an untouched confirmation set, and scanner separation alone does not eliminate every source of bias.

The anatomy route passed a nine-structure reference pilot with mean Dice approximately **0.9118**. Native-domain transfer remains exploratory. No diagnostic use or clinical readiness is claimed.

## What this demonstrates to an employer

The core contribution is a disciplined way to build and inspect ML systems under imperfect data and constrained compute: verify identities, isolate evaluation assumptions, preserve completed work, retain negative evidence, and make claims traceable to artifacts.

Start with the [review guide](EMPLOYER_REVIEW_GUIDE.md), run the [CPU demonstration](REPRODUCIBILITY.md), or inspect the [architecture](ARCHITECTURE.md). The [closeout record](PROJECT_CLOSEOUT.md) defines the completed public scope and the research limits at publication.
