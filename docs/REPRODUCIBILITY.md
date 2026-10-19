# Reproduce and inspect

The public checks need no AWS resource, Kaggle credential, MRI image, or private
checkpoint. They validate the maintained engineering components and final aggregate
analysis, not the withheld competition model.

## Credential-free walkthrough

```bash
python3 -S review/run.py --output /tmp/rsna-review --with-node
python3 -S review/run.py --output /tmp/rsna-review --with-node --check
```

Python 3.11+ is required; Node.js enables actual browser-control tests. The generated
HTML binds its implementation map and outputs to source hashes. A changed source
or corrupted export is not accepted as an unchanged rerun.

## Locked Python reference

Use Python 3.12 in an isolated environment:

```bash
python -m venv /tmp/rsna-review-env
source /tmp/rsna-review-env/bin/activate
python -m pip install --require-hashes -r requirements-review.lock
python -m pip check
python -m pytest -q
python examples/run_public_pipeline.py --output /tmp/rsna-reference
```

This fits twelve logistic controls on authored, scanner-grouped features. It reports
held-out AUC, Brier score, log loss, reliability-bin counts and scanner slices,
including the training-fold prevalence baseline. It is `SYNTHETIC_ONLY`: no MRI
performance or clinical calibration is implied.

## Demonstrate verified recovery

```bash
python examples/run_public_pipeline.py --output /tmp/rsna-resume --stop-after-fold 1
python examples/run_public_pipeline.py --output /tmp/rsna-resume
python examples/run_public_pipeline.py --output /tmp/rsna-resume
```

The first call records one fold and reports `PAUSED`. The next verifies that fold
and fits the remaining ones. The third verifies and reuses every completed fold.
Tests compare resumed and fresh predictions. Configuration/source mismatches and
corrupted checkpoints raise `CacheValidationError` with exit code 2. Never remove
a lock while another process owns the output directory.

## Re-execute the final analysis

```bash
python scripts/verify_review_notebook.py
python scripts/execute_review_notebook.py --output /tmp/rsna-analysis.ipynb
python scripts/verify_review_notebook.py --notebook /tmp/rsna-analysis.ipynb
python tools/check_publication_boundary.py
```

The executor uses a real clean Jupyter kernel, saves outputs, reopens them and
verifies source/report fingerprints, plotted values, execution counts and three
persistent Plotly/SVG pairs. A restricted environment may use the explicitly labelled
`--engine ipython-inprocess` alternative. These charts recompute the original
published aggregates, not private row-level predictions or bootstrap samples.

The [recorded report](../reports/current_frontier/results.json) remains unchanged:
ordered context improved grouped AUC from **0.7943834 to 0.7978448**. The subsequent
**0.7978946** point estimate has an inconclusive interval. The external **0.943**
record is a different setting. The 58 audit rows are not untouched confirmation.

[Publication boundary](GIT_PUBLICATION.md) · [Final scope](PROJECT_CLOSEOUT.md)
