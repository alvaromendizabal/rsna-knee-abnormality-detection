# Employer review guide

This is a completed engineering portfolio release by Alvaro Mendizabal. It combines a runnable public example with a documented record of private medical-imaging research. The [closeout](PROJECT_CLOSEOUT.md) states what was delivered and what the evidence does not establish.

## A short review

1. Read the [README](../README.md) for the problem, ownership and results.
2. Open the [architecture](ARCHITECTURE.md) and [case study](EMPLOYER_CASE_STUDY.md) for the design decisions.
3. Inspect [Notebook 14](../notebooks/14_winner_transfer_and_context_modeling.ipynb) alongside its [aggregate report](../reports/current_frontier/results.json).

The central engineering question is how to make expensive experiments traceable, recoverable and scientifically interpretable when data and model components have different provenance.

## A hands-on review

Follow the Python 3.12 setup in [Reproducibility](REPRODUCIBILITY.md), then run:

```bash
python examples/run_public_pipeline.py --output /tmp/rsna-public-demo
python -m pytest -q
python scripts/verify_review_notebook.py
```

Use the activated review environment for these commands. Open `/tmp/rsna-public-demo/report.html` and inspect its neighboring `results.json` and `synthetic_predictions.csv`.

The pipeline generates synthetic tabular features and twelve labels, separates scanner groups across five folds, learns normalization from each training fold, fits logistic models, and evaluates held-out predictions. Its manifests bind inputs, configuration, source and runtime to reusable checkpoints. A completed rerun verifies the cache and performs zero fits. The reproduction guide also demonstrates a controlled interruption after one committed fold.

These outputs are labeled **SYNTHETIC_ONLY**. They demonstrate implementation behavior; they are not patient predictions, an MRI classifier, or evidence for the historical research scores.

## What to inspect by role

| Review focus | Suggested evidence | Questions to ask |
|---|---|---|
| ML engineering | [Public pipeline](../examples/run_public_pipeline.py), tests, [architecture](ARCHITECTURE.md) | Can completed work be trusted and reused? What invalidates a checkpoint? |
| Applied research | [Context modeling](CONTEXT_MODELING_FRONTIER.md), [research timeline](RESEARCH_TIMELINE.md), aggregate report | Were comparisons made on the same population? Was uncertainty used in the decision? |
| Data and evaluation | [Reproduction boundary](REPRODUCIBILITY.md), schema/metric tests | Are groups, targets and prediction rows aligned? Which data influenced selection? |
| Delivery and maintainability | CI workflows, [publication procedure](GIT_PUBLICATION.md), [closeout](PROJECT_CLOSEOUT.md) | Are dependencies pinned, outputs verifiable and public artifacts appropriately scoped? |

## Outcomes worth discussing

The recorded cross-slice context study moved grouped macro ROC-AUC from **0.7943834 to 0.7978448** on the same 4,349-study development population. A later **0.7978946** point estimate had a paired interval that crossed zero; the incremental hypothesis remained inconclusive.

Other records preserve negative experiments and narrower engineering qualifications. For example, successful reference anatomy segmentation does not establish disease-prediction benefit, and a geometry audit only supports its inspected acquisition scope. The historical **0.943** external record is evaluated separately from the internal grouped results.

My contribution covers data/evaluation contracts, experiment orchestration, model integration and controlled extensions, recovery, testing, evidence presentation and publication controls. Existing frameworks, pretrained models and prior solution methods supplied components; the portfolio does not claim authorship of those external architectures.

## Scope of the completed release

The public code and aggregate notebook replay can be reviewed without MRI, model weights, AWS access or a GPU. Private row-level experiments cannot be independently rerun from this repository. Full raw-image test serving and clinical validity are not established, and no new submission is claimed.

Historical reports remain dated records. Their references to prepared experiments are preserved for provenance and are not commitments to continuing private work. Raw images, identifiers, private predictions, checkpoints, cloud paths and exact competition inference logic remain outside this release.
