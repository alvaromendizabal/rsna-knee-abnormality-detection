# Reproducibility

The completed public release supports an offline CPU engineering demo, the public test suite and replay of selected aggregate notebooks. The private MRI experiments are represented by dated aggregate evidence; their data, weights and exact competition implementation are not distributed.

## Set up the pinned environment

Use **Python 3.12** and keep the environment and generated outputs outside the checkout. `requirements-review.txt` lists direct dependencies; `requirements-review.lock` pins transitive distributions and their hashes.

```bash
python3.12 -m venv ../rsna-public-review-env
../rsna-public-review-env/bin/python -m pip install --require-hashes -r requirements-review.lock
source ../rsna-public-review-env/bin/activate
```

Installation requires package access once. The commands below then run locally without cloud credentials, MRI, model downloads or a GPU.

## Run the public pipeline

```bash
python examples/run_public_pipeline.py --output /tmp/rsna-public-demo
```

The pipeline generates synthetic tabular features with nested patient/scanner groups, creates five scanner-disjoint folds, fits twelve logistic outputs with training-only normalization, and scores held-out predictions. The default seed is `2026`; `--seed` selects a different synthetic fixture.

Inspect:

| Output | Purpose |
|---|---|
| `report.html` | Standalone visual report of the synthetic run |
| `results.json` | Machine-readable metrics, execution state and provenance |
| `synthetic_predictions.csv` | Held-out predictions for fictional rows |
| Fold checkpoints and manifests | Committed work with fingerprints and checksums for resume validation |

All outputs are labeled **SYNTHETIC_ONLY**. These are synthetic tabular models, not an MRI classifier, clinical evidence, or a scientific reproduction of the private scores.

Run the same command again to validate and reuse all completed folds with zero additional fits. A changed input, configuration, source or runtime invalidates an incompatible cache rather than silently overwriting it; choose a new output directory for a different run.

## Demonstrate checkpoint recovery

Use a fresh output directory:

```bash
python examples/run_public_pipeline.py --output /tmp/rsna-public-resume --stop-after-fold 1
python examples/run_public_pipeline.py --output /tmp/rsna-public-resume
```

The first invocation commits one fold and exits successfully with status `PAUSED`. This is a controlled interruption demonstration. The second verifies that checkpoint and completes the remaining folds. After an unclean process kill, first verify that no run still owns the output directory, then remove only its stale `.pipeline-lock` directory before resuming.

An incompatible or corrupted cache raises `CacheValidationError` and exits with code 2.

## Check code and published evidence

```bash
python -m pytest -q
python tools/public_quality.py
python tools/check_publication_boundary.py
python tools/check_current_frontier.py
python scripts/verify_review_notebook.py
```

The smaller metric/schema example remains available:

```bash
python examples/run_public_review.py
```

It uses four fictional studies to exercise the twelve-target metric, reject invalid prediction tables and preserve an inconclusive uncertainty decision. Its illustrative 0.75 AUC is not a research result.

The notebook verifier checks source/report fingerprints, saved execution counts, plotted values and persistent Plotly/SVG outputs. Aggregate consistency is distinct from recalculating private row-level predictions.

## Optionally execute Notebooks 12–14

```bash
python scripts/execute_review_notebook.py --notebook 12 --output /tmp/rsna-review-notebooks/12.ipynb
python scripts/execute_review_notebook.py --notebook 13 --output /tmp/rsna-review-notebooks/13.ipynb
python scripts/execute_review_notebook.py --notebook 14 --output /tmp/rsna-review-notebooks/14.ipynb
```

The executor runs a real Jupyter kernel, saves the notebook, reopens it and verifies its output. The kernel needs permission to bind local sockets. In restricted environments, `--engine ipython-inprocess` executes the cells in process; that mode is explicitly separate from a Jupyter kernel run.

Notebook 12 replays historical aggregate chart values. Notebook 13 presents historical engineering priorities and completion counts. Notebook 14 checks the Stage 104 aggregate report, uncertainty state and coverage counts. None retrains private MRI models or independently verifies the underlying scores.

Notebook 00 is a prepared, unexecuted private preflight template. Notebooks 01–11 are historical execution records with their original data/environment assumptions. They are outside the clean public replay claim. The review refresh repaired the executable chart sources and saved-output consistency of Notebooks 12–14; it did not change historical metric reports.

## Evidence boundaries

| Evidence | What can be established here | What is outside the claim |
|---|---|---|
| Public pipeline | Group isolation, training/evaluation flow, validated resume and reporting on synthetic data | MRI performance or clinical validity |
| Public helpers/tests | Metric, schema, fallback, provenance and publication contracts | Private model/checkpoint equivalence |
| Aggregate notebook replay | Published values, arithmetic, plots and uncertainty decisions agree | Independent reconstruction of private predictions |
| Archived research report | Dated development outcomes and their stated scope | New experiments, a new submission or an untouched confirmation cohort |

The [aggregate snapshot](../reports/current_frontier/results.json) retains Stage 102's grouped result **0.7978448** and Stage 104's **0.7978946** inconclusive increment. The external **0.943** record is separate. The 58 fully labeled audit rows were within recovered selection lineage and are not treated as untouched confirmation.

MRI/DICOM data, identifiers, row-level research predictions, private checkpoints, cloud locations, private runners/returns and exact competition inference code remain excluded. Full raw-image test serving is not established by this release. The [closeout](PROJECT_CLOSEOUT.md) defines completion; historical preparation notes are not an ongoing work promise.
