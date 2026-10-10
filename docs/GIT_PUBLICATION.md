# Public release procedure

This procedure publishes the reviewed engineering portfolio. The public release scope is defined in [Project closeout](PROJECT_CLOSEOUT.md); historical milestone instructions do not govern the current release workflow.

## Inspect the intended checkout

Run from the repository root:

```bash
git status --short --branch
git remote -v
git diff --stat
git diff --check
```

Confirm the branch and public destination before publication, preserve unrelated work, and inspect the actual changed files. Use a reviewed feature branch and pull request. Remote configuration must not contain embedded credentials.

## Validate the public artifacts

Use the hash-locked Python 3.12 environment in [Reproducibility](REPRODUCIBILITY.md):

```bash
python -m pytest -q
python tools/public_quality.py
python tools/check_publication_boundary.py
python tools/check_current_frontier.py
python scripts/verify_review_notebook.py
python examples/run_public_pipeline.py --output /tmp/rsna-public-release-check
```

Review the generated HTML and JSON outside the checkout. Check the intentional pause/resume path when checkpoint code changes. Changes to the aggregate notebook sources also require the documented real-kernel replay of the affected Notebooks 12–14.

CI checks and local tests provide evidence for the public layer. They do not establish private MRI inference correctness or authorize publishing private artifacts.

## Review the staged boundary

Stage only the source, tests, documentation, assets and configuration that have been inspected. Use explicit file paths with `git add --`; do not use a broad staging command as a substitute for reviewing the file list.

Then inspect:

```bash
git diff --cached --stat
git diff --cached --check
python tools/check_publication_boundary.py
git diff --cached
git status --short
```

The release may include aggregate reports, public helpers, synthetic examples, executed aggregate notebooks, SVG assets and CI definitions. Preserve the original dates and interpretation of historical evidence; a presentation refresh is not a new experiment.

Exclude:

- MRI/DICOM files, radiology reports, study/patient identifiers and scanner assignments;
- row-level research predictions, cache shards, model weights and private checkpoints;
- credentials, signed URLs, cloud resource locations and private source-recovery handles;
- private runners, execution bundles and exact competition inference/fusion/submission implementation;
- generated environments, caches and local demo checkpoints or predictions.

The demo's generated rows are fictional, but generated files still belong outside the checkout. `.gitignore` is a supporting control; it does not inspect files that were already tracked. Review notebook outputs as well as their source cells.

## Commit and publish the reviewed branch

Once the staged diff matches the public release scope and the checks pass:

```bash
git commit -m "Complete engineering portfolio release"
git push --set-upstream origin HEAD
```

Open a pull request against the intended default branch, inspect the rendered README and diagrams, and require the publication and public-quality checks to pass before merging. Resolve a rejected push through ordinary history inspection and integration; this procedure does not use a force push, history rewrite or destructive cleanup.

The release description should identify the runnable synthetic pipeline, verified aggregate notebooks, documentation and test coverage. State the evidence boundary and link to [Project closeout](PROJECT_CLOSEOUT.md). Do not imply a new competition submission, clinical deployment or scientific result from publishing the repository.
