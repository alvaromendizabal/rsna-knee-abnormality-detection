# RSNA Knee Abnormality Detection

**Image-model research, reproducible MRI inference, and evidence-led ensemble validation.**

A notebook-first machine-learning project by **Alvaro Mendizabal**. The system predicts 12 knee MRI findings from images; reports are a training-supervision resource, not a test-time input. Work spans representation engineering, weak supervision, DINOv2 transfer learning, a public CoAtNet/Raptor transfer, and controlled heterogeneous-ensemble experiments.

> **Latest published milestone: Stage 27, September 22, 2026 UTC.** The experiment and its evidence are complete. The primary blend was rejected. Competitive development remains active; this repository does not claim a winning model or clinical readiness.

## Start here

Open **[06 — Image models and replication](notebooks/06_image_models_and_replication.ipynb)** for the current research story, saved inline Plotly figures, exact evaluation boundaries, and the decision to stop a blend that failed replication. Then read the [technical research record](docs/IMAGE_MODELS.md) for architecture, provenance, resource use, and the remaining submission gates.

## Results that must not be conflated

| Evaluation setting | System | Macro-AUROC |
|---|---|---:|
| Official public leaderboard, recorded September 22 at 02:06 UTC | Reproduced **public multi-model reference ensemble**, submission 56442573 | **0.933** |
| Same returned leaderboard page | Highest listed score | **0.958** |
| Twelve-study development pilot | Fluid-only Raptor | **0.937315** |
| Twelve different development studies | Fluid-only Raptor | **0.922410** |
| Same replication cohort | Preregistered 90% full Raptor + 10% DINOv2 | **0.919150 — rejected** |
| Same replication cohort, predefined secondary arm | 90% fluid-only Raptor + 10% DINOv2 | **0.926383 — unconfirmed candidate** |

The **0.025 public-leaderboard gap** is a dated, comparable difference. Local cohort scores are not leaderboard scores. The 0.933 result is attributed to the public reference ensemble, not an independently trained winning system or standalone Raptor. Submission 56441830 was complete but its score field was blank in the last receipt.

## What the project demonstrates

- **Data and supervision:** 4,407 training studies, 24,371 series, and 58 structured-label studies; unknown labels are not silently treated as negatives. Earlier work includes 130 protocol/acquisition columns, 140 per-series image descriptors, and 423 plane-preserving study columns.
- **Learned models and input fidelity:** a trained DINOv2 checkpoint; strict transfer of a 73.1-million-parameter CoAtNet/Raptor checkpoint; complete real-DICOM decoding and exact reference parity for a 64-image representation and 42 windows.
- **Efficient experiments:** global attention preserved across encoding microbatches; checksum-bound cached features; a four-arm window experiment without new image encoding; cached DINO predictions reused for separate-cohort ensemble replication.
- **Scientific judgment:** negative results remain visible. Lower Brier error did not rescue a failed AUROC hypothesis. Secondary results are not relabeled as primary confirmations.

## Notebook guide

[01 — Metadata](notebooks/01_metadata_and_representation_audit.ipynb), [02 — Protocol features](notebooks/02_protocol_feature_investigation.ipynb), [03 — Image context](notebooks/03_image_context_feature_investigation.ipynb), [04 — Supervision](notebooks/04_supervision_and_validation.ipynb), and [05 — Teacher feasibility](notebooks/05_multilingual_teacher_pilot.ipynb) preserve the earlier research checkpoint. Notebook 05 intentionally records a stopped synthetic canary, not completed report inference. [06 — Image models](notebooks/06_image_models_and_replication.ipynb) is the current entry point.

## Reproduce the public analysis

Public tests require only Python 3.12 or later: `python -m unittest discover -s tests -p 'test_image_models.py'` and `python tools/public_quality.py`. To rerun notebook 06, install `ipython`, `nbformat`, `nbclient`, and `ipykernel` in a separate environment, open it from this checkout, and run all cells. Its Plotly MIME outputs include embedded SVG fallbacks. It replays published aggregate evidence; it does not rerun private MRI inference.

## Public repository versus AWS workspace

**GitHub is the curated review and reproducibility layer. AWS is the canonical research workspace.** The public tree contains aggregate evidence, executed analysis, small tested analytical primitives, configurations, and documentation. Raw MRI, report text, study identifiers, per-study predictions, model weights, environments, credentials, private logs, and full return bundles remain outside Git.

See [current status](docs/PROJECT_STATUS.md), [data access](docs/DATA_ACCESS.md), and [source attribution and limitations](docs/IMAGE_MODELS.md). No diagnostic or clinical use is claimed.
