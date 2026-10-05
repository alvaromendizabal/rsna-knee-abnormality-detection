# Reproducibility boundary

## Goal

This repository is **semi-reproducible by design**.

It exposes enough aggregate evidence, public-safe code, tests, decision contracts, and executed notebooks for an employer or reviewer to understand how the research is conducted without publishing restricted data or competitive implementation details.

AWS/SageMaker remains the canonical research workspace.

## What is reproducible publicly

The public repository supports deterministic checks for:

- metric direction and publication contract;
- grouped-validation counts;
- retained positive/negative research decisions;
- parent reconstruction counts;
- completed audit milestones;
- anatomy-model qualification logic;
- exact parent-fallback invariants;
- privacy/publication boundaries.

The machine-readable summary lives at reports/current_frontier/results.json.

Public-safe decision helpers live under src/rsna_research/.

Tests live under tests/.

## Run the public checks

From the repository root:

    python -m unittest discover -s tests
    python tools/check_current_frontier.py

The core publication contract uses the Python standard library and does not require raw competition data, cloud credentials, model checkpoints, or network access.

## Continuous integration

.github/workflows/publication-checks.yml runs the same gates on pushes and pull requests.

The workflow verifies:

1. public-safe unit tests;
2. current-frontier machine-readable evidence;
3. notebook persistence contracts;
4. absence of common credential/private-path patterns;
5. public/private publication policy.

## Public/private split

### Public
- aggregate metrics;
- validation contracts;
- milestone counts;
- public-safe helpers;
- experiment decisions;
- architecture/research narratives;
- executed aggregate notebooks;
- CI/publication gates.

### Private
- DICOM/MRI data and reports;
- study/scanner identifiers;
- row-level predictions;
- private checkpoints and weights;
- source-recovery locators;
- cloud paths and credentials;
- exact competition fusion/inference/submission code;
- resumable private runners and return bundles.

## Why private artifacts are not required for the public checks

The public layer validates **research governance and aggregate claims**, not the hidden competition implementation.

A public check should answer:

- does the published metric contract match the documented project?
- are milestone counts internally consistent?
- are negative results still represented as negative?
- is an engineering qualification being mislabeled as a model improvement?
- would a missing anatomy route preserve the parent?
- has private material leaked into the public layer?

It should not recreate restricted data or reveal proprietary/competitive implementation.

## Evidence lifecycle

Each private AWS milestone maintains immutable run evidence, unique run IDs, logs, hashes, source identities, resource telemetry, and return bundles.

Only validated aggregate evidence crosses into GitHub.

## What this repository does not claim

This public layer does **not** claim complete historical reproduction of every private artifact, an untouched labeled confirmation cohort where lineage evidence says otherwise, complete raw acquisition coverage, a new external score when none was measured, or clinical validity.

That distinction is part of the reproducibility standard rather than a limitation to hide.
