# Imaging ML with group-aware evidence and recovery.

**Alvaro Mendizabal · Medical-imaging research / validation / reliable training**

A twelve-label knee-MRI research workflow connecting scanner-aware evaluation, image-model studies, cross-slice context, and recoverable experiments. Public demonstrations make the engineering inspectable without patient data.

[Project overview](../README.md) · [Printable inspection brief](index.html) · [Review configuration](project.json)

## Review the engineering, not just the headline

| Focus | Decision to inspect | Follow the proof |
|---|---|---|
| Data science | **Respect acquisition groups during validation.** Keep scanner groups disjoint and inspect aligned targets rather than relying on a random row split. | [Code](../src/rsna_research/protocol.py) · [Tests](../tests/test_research_protocol.py) · [Evidence](../docs/EMPLOYER_CASE_STUDY.md) |
| Applied AI | **Test cross-slice context as a controlled change.** Compare ordered context and image-model alternatives on a matched development population. | [Code](../src/rsna_research/image_models.py) · [Tests](../tests/test_image_models.py) · [Evidence](../reports/current_frontier/results.json) |
| ML engineering | **Make fold recovery content-bound.** Demonstrate checkpoint verification, corruption rejection, and completed-fold reuse in a small public pipeline. | [Code](../src/rsna_review/public_pipeline.py) · [Tests](../tests/test_public_pipeline.py) · [Evidence](../docs/REPRODUCIBILITY.md) |
| Data science | **Keep score scope and inference validity separate.** Validate twelve-label metrics, row ordering, and uncertainty decisions without treating an integration fixture as clinical evidence. | [Code](../src/rsna_knee/metrics.py) · [Tests](../tests/test_metrics_and_evidence.py) · [Evidence](../examples/run_public_review.py) |

The linked tests are review entry points, not a claim that this compact command executes the full research suite. The project’s canonical reproducibility guide describes the broader environment and tests.

## One command, an inspectable result

From a checkout with Python 3.11 or newer:

```bash
python3 -S review/run.py --output /tmp/ml-review
```

Open `/tmp/ml-review/index.html`. The directory contains an accessible HTML brief, `receipt.json`, `manifest.json`, and logs for each executed command. No Python package installation, model download, cloud credentials, or external dataset is required. On Windows, substitute a writable directory outside the checkout for `/tmp/ml-review`.

To execute the browser engine checks as well, install Node.js and use a separate output directory:

```bash
python3 -S review/run.py --output /tmp/ml-review-node --with-node
python3 -S review/run.py --output /tmp/ml-review-node --with-node --check
```

The default path does not execute Node checks and never labels them as passed. CI runs both the Python and browser checks on Python 3.11 and 3.13. It retains the exact review artifacts with the workflow run.

| Check | Runtime | Inspected entry point |
|---|---|---|
| `public-source-contracts` | python | [`tools/public_quality.py`](../tools/public_quality.py) |
| `scanner-grouped-browser-pipeline` | node | [`tools/test_public_demo.mjs`](../tools/test_public_demo.mjs) |

## What is actually reproduced

The Python check verifies public source, retained notebook evidence, and research contracts. Optional Node tests execute the synthetic browser training pipeline. Historical MRI evaluation is separate; no clinical validity is established by these demonstrations.

A repeat invocation verifies the saved bundle rather than rerunning completed checks. `--check` performs verification only. A changed linked source file, missing evidence, changed artifact, failed command, invalid path, or mismatched check mode causes a nonzero exit. Use a fresh output directory after an intentional source change; stale evidence is never silently relabeled as current.

Each command has a default 90-second deadline, configurable with `--timeout`. The runner records UTC time, interpreter version, elapsed command times, command identities, and SHA-256 hashes for its configuration, template, invoked entry points, linked implementations, tests, and evidence. Failed runs keep diagnostic logs in a separately named failed-run directory and never produce a success receipt.

The fingerprint includes the complete public-demo HTML, CSS, JavaScript and JSON scope declared in `project.json`, as well as the curated review entry points. Additions and removals within that scope invalidate an older receipt. The receipt records the actual Python/Node runtimes and binds the rendered report plus the exact command entry points, arguments and logs. A clean Git checkout produces commit-specific source links; modified checkouts are labeled. This is a declared review scope, **not every transitive dependency or every repository file**. Checksums establish consistency, not independent authentication of historical scores. The receipt records the local bytes inspected, even when a modified checkout requires branch-relative links. The static page is explicitly an inspection brief, not an execution receipt.

## Public/private boundary

MRI/DICOM images, patient or study identifiers, private prediction rows, trained weights, exact tuned inference recipes, and private GPU checkpoints remain excluded.

This review adds no training result and changes no historical score, selection decision, notebook output, source attribution, or license. A synthetic demonstration, an aggregate evidence check, public reference training, and exact private-model replay are different reproducibility levels.

## Verify the review kit itself

```bash
python3 -B -S -m unittest discover -s review -p test_run.py -v
python3 -B -S -O -m unittest discover -s review -p test_run.py
python3 -S review/run.py --check-page
```

After an intentional configuration or template change, regenerate the static brief with `python3 -S review/run.py --render`, inspect it, then run the checks above. The kit needs no JavaScript or network access to render its HTML. It uses semantic headings, keyboard-visible links, a skip link, responsive layouts, and print styling.
