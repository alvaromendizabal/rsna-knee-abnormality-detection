# RSNA Knee Abnormality Detection

Research-grade MRI representation and supervision engineering for the **RSNA Knee Abnormality Detection** Kaggle competition.

> **Current phase:** feature and supervision research. The project has not yet established an official image-model AUC improvement, and no claim is made that it has reached the leaderboard frontier.

## Research objective

Build a reproducible image-only inference system for 12 knee MRI findings while rigorously testing which representations actually improve macro ROC AUC. The project emphasizes leakage-safe validation, controlled feature-family ablations, saved notebook evidence, bounded compute, and transparent negative results.

## Verified checkpoint

The current public checkpoint records the following completed work:

- audited **4,407 training studies** and **24,371 training series**;
- identified **58 fully expert-labeled studies** and preserved **4,349 studies without structured expert labels** as unknown rather than treating them as negatives;
- built a **130-column protocol/acquisition representation** (65 preserved + 65 newly investigated candidates), while explicitly recording constant candidates rather than treating feature count as progress;
- completed a real-image pilot with **140 per-series image descriptors**, **423 plane-preserving study columns**, and **8 image-context families**;
- investigated report-supervision rules on a fixed training-only sample, with reserved expert-labeled studies protected from target construction;
- tested a local multilingual-teacher pilot, which **stopped at a synthetic canary** before processing any real competition report because one expected ACL assertion state was not reproduced;
- preserved executed notebooks with saved Plotly outputs and PNG companions for review.

**Official development AUC:** not yet measured at this checkpoint.  
**Kaggle leaderboard claim:** none.  
**Model submissions:** none from this repository checkpoint.

## Why the project is feature-first

The core research question is not "which model can I try next?" but **which clinically and physically meaningful representations expose information that the model currently cannot use**. Current and planned feature families include:

1. MRI plane and contrast complementarity;
2. protocol diversity and acquisition geometry;
3. robust intensity and signal-tail descriptors;
4. spatial gradients and co-occurrence texture;
5. regional heterogeneity and multiscale context;
6. through-slice continuity and slice-position context;
7. field-of-view and anatomical localization hypotheses;
8. supervision quality, negation, uncertainty, and historical-context handling;
9. missing-view and acquisition-shift robustness;
10. later learned image embeddings and controlled ensemble diversity, only after representation gains are measured.

Feature families are promoted only through matched comparisons on the official metric. Importance values, SHAP, or feature count are treated as diagnostics—not proof of value.

## Notebook research trail

| Notebook | Purpose |
|---|---|
| `01_metadata_and_representation_audit.ipynb` | Supervision availability, schemas, joins, acquisition coverage, and leakage checks |
| `02_protocol_feature_investigation.ipynb` | Contrast-aware multi-view and protocol feature families |
| `03_image_context_feature_investigation.ipynb` | Real-image texture, slice context, geometry, and multiscale pilot |
| `04_supervision_and_validation.ipynb` | Negation, uncertainty, section/history, abstention, and evaluation protections |
| `05_multilingual_teacher_pilot.ipynb` | Local multilingual-teacher feasibility gate; stopped before real reports after a failed synthetic canary |

The notebooks are saved with visual evidence. Public figures are aggregate research outputs; raw competition images and report text are intentionally excluded.

## Engineering standards

- immutable raw-data boundary;
- explicit schemas and identifier checks;
- missing labels preserved as missing;
- restartable stage manifests and checksum validation;
- bounded runtime and memory guards;
- training-only feature construction where labels are involved;
- official macro ROC AUC reserved for score-bearing comparisons;
- negative and blocked experiments retained in the research history;
- public CI performs static source/notebook/integrity checks without requiring Kaggle data.

## Current conclusion

The metadata-only feature space is **not** considered mature, but it is also not the highest-value place to generate arbitrary new combinations. The strongest next research rounds are image-based: plane/contrast ablations, field-of-view and anatomical localization, and slice-context representations under a fixed baseline and fixed evaluation rows. Supervision quality remains a parallel dependency because only a small subset has structured expert labels.

## Data and reproducibility

Competition data, MRI files, report text, generated private model responses, model weights, checkpoints, credentials, and AWS runtime artifacts are **not distributed in this repository**. Obtain competition data through the official Kaggle competition and follow its rules.

The public repository contains research code, configurations, tests, executed aggregate notebooks, documentation, and safe figures needed to review the methodology and engineering work without redistributing restricted inputs.

## Status

Feature engineering remains open. The objective is to push toward the strongest valid comparable Kaggle performance while preserving methodological integrity, reproducibility, and transparent evidence.
