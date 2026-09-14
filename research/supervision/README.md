# Supervision and validation: the next bounded research milestone

## Objective

Before training image models, establish a reproducible, report-group-separated development design and measure how report-to-target candidates change when negation, uncertainty, and clinical context are handled jointly. This is a **supervision candidate investigation**, not an image-feature AUC experiment.

The returned preceding research package is complete: 166 listed file hashes match, three executed notebooks contain 36 native Plotly payloads and 36 PNGs, and one 25-file MRI series has a completed, reused representation checkpoint. It contains no model fits and no AUC. Its earlier packaging-failure receipt is historical; the latest manifest has status `complete` and no issues. See the supplied return-review document for provenance.

The research so far contains 130 acquisition descriptors (65 old plus 65 new), 140 per-series image descriptors and a 423-column plane-preserving schema. One processed study does not support a generalization estimate. Adding more metadata combinations before examining supervision would not answer which image representation improves prediction.

## Exact location and isolation

New modules live in `research/supervision/`. Notebook 04 lives in `notebooks/`. The existing core source fingerprint covers `src/`, `scripts/`, `tests/`, and `configs/`; this milestone intentionally does not change any of them. It does not replace notebooks 00-03, the continuation helper, raw data, `.git`, checkpoints, or the Python environment.

Use the existing `.venv` and `RSNA Knee - audit` kernel. `run.py prepare` adds Matplotlib 3.10.6 only when absent, using binary packages and constraints preserving NumPy 2.2.6, pandas 2.3.3, and Plotly 6.3.0. An unexpected existing Matplotlib version causes a stop rather than a replacement. Transitive versions are recorded, not represented as a complete locked environment. There are no AWS, Kaggle, Hugging Face, LLM, submission, or Git actions.

## Scientific design

### Investigation A: frozen, outcome-blind allocation

All 58 expert-labeled studies stay sealed. Casefolded, Unicode-normalized exact report duplicates of expert reports are excluded from the training/development pool. This can conservatively exclude more than the preceding four case-sensitive duplicates; any difference is reported, not silently discarded.

Other normalized report groups are deterministically assigned to five folds before extraction. Fold zero is development-only; folds one to four supply the candidate pilot. Groups containing previously sampled image studies are forced into training so already inspected pilot data do not become purportedly untouched validation, unless the sealed-expert overlap exclusion takes precedence. Both counts are reported. The candidate pilot contains up to 256 distinct training report groups, one report per group, selected by a fixed hash ranking. All five arms use the exact same reports.

This is not patient grouping. The metadata does not establish patient/site disjointness, near-duplicate reports are not resolved, and no disease stratification is computed from the sealed gold outcomes. The split is provisional for later image validation until those dependencies are addressed. Do not describe its development fold as an independently validated clinical cohort.

### Investigation B: joint supervision and matched block removals

Five prespecified arms are implemented:

1. `mention_only`: a deliberately crude reference; any target mention becomes a positive candidate. **Not approved training labels.**
2. `joint_context`: target-specific anatomy/pathology mapping plus bounded clause scope, negation, uncertainty, and section/history filtering, evaluated together.
3. `joint_no_negation`: remove only the negation block from the full pipeline.
4. `joint_no_uncertainty`: remove only the uncertainty block.
5. `joint_no_context_gate`: remove only the section/history gate.

The vocabulary is **English-only**. Latin script is not assumed to be English. This implementation is neither a dependency parser nor a validated multilingual labeler. Its purpose is a bounded, inspectable reference and disagreement assay for subsequent multilingual-supervision development. Long-range scope, shorthand, translated terms, compound target statements, and fine clinical thresholds remain limitations. Multi-target clauses abstain conservatively rather than assigning a pathology to the wrong anatomy.

Six states are retained: positive, negative, uncertain, conflict, context-only, and unmentioned. Only the first two define a proposed binary mask, and **none of the candidates is approved for image training** until reviewed. No missing or uncertain state becomes zero or a guessed 0.5 probability. Report silence cannot be assumed to mean clinical absence.

Twelve target-specific contracts explicitly avoid shortcuts: effusion is not synovitis; marrow edema is not necessarily bone contusion; meniscal degeneration is not necessarily tear; generic osteoarthritis is not compartment-specific OA. A mention of prior ACL reconstruction is not automatically a current injury. Explicit OA vocabulary is required in this conservative prototype; isolated cartilage changes remain unresolved. These are research mappings, not definitive clinical criteria.

All positive/negative counts and differences are **candidate assignments**, not prevalence, accuracy, effect sizes, or AUC improvements. The joint and removal arms isolate how implementation blocks interact; they do not by themselves prove which block makes labels more correct. A 24-report private review queue prioritizes disagreements, so it is not a random sample from which to estimate extraction accuracy.

## Twelve saved plots on every notebook run

Each figure uses one aggregate numerical specification to generate an interactive Plotly graph and a separate Matplotlib/Agg PNG companion. The numerical-specification hash is stored in the Plotly metadata and figure receipt. The PNG is emitted as an ordinary independent notebook image output, so unsupported Plotly MIME rendering cannot hide it. This is **not** a Kaleido export of the Plotly canvas: the layouts can differ, but both show identical numeric series.

Each plot saves `.png`, `.plotly.json`, `.spec.json`, and `.html`. A local `plotly.min.js` supports offline HTML viewing. No Chrome/Kaleido installation is needed. The saved notebook must have 12 PNGs and 12 Plotly payloads; collection matches their hashes and metadata to the active figure files. Re-running notebook 04 regenerates both forms automatically. Notebooks 01-03 need not be rerun.

## Resource and checkpoint limits

- Preparation: 300-second foreground cap; optional binary renderer installation 180 seconds; synthetic tests 90 seconds externally.
- Analysis: up to 256 training report groups; five arms; 180-second worker cap, 210-second parent cap, 4 GiB memory guard; zero image transfers, model fits, or model/API calls.
- Second analysis invocation verifies checkpoint reuse and must process zero new reports.
- Collection: 90-second cap and 40 MiB uncompressed return-file cap.

These are ceilings, not measured runtimes or billing caps. Plot display time is separate. The latest returned AWS snapshot identifies `ml.m5.xlarge`, 100 GB storage, approximately 98.74 GiB free, at 2026-09-14 01:30 UTC. That is historical evidence, not a live account check. It is sufficient for this CPU metadata pilot; do not upgrade hardware.

## Execution and stop criteria

```bash
cd "$HOME/rsna-knee-abnormality-detection"
source .venv/bin/activate
python research/supervision/run.py prepare
```

Stop unless preparation completes and synthetic tests pass. Then open notebook 04, select the existing audit kernel, Restart Kernel and Run All Cells. Both analysis invocations must use the same key, the second reports zero new reports, all 12 plot pairs must be present, and the final marker must be `SUPERVISION_MILESTONE_COMPLETE`. Save, close and reopen the notebook. Do not change clinical mappings after seeing outcomes without registering a new experiment.

```bash
python research/supervision/run.py collect
```

This writes `returns/rsna-knee-supervision-return.zip`. The previous research-return ZIP remains unchanged. An existing supervision-return ZIP is moved into `returns/history/` before replacement. A complete package requires the saved notebook and matching figure evidence. A recoverable failed check yields a `partial` ZIP with safe diagnostic codes; partial is never a passing scientific result.

At any failed step:

```bash
python research/supervision/run.py diagnose
```

This attempts a source/evidence-only diagnostic snapshot under the same filename. Raw exception messages, source lines, report text, UIDs and private files are excluded. A disk-permission or full-filesystem problem can still prevent writing a ZIP; in that case preserve the printed error and `artifacts/supervision/failure.json`.

## Privacy and return contents

Split assignments, report text, row-level candidate states, and the 24-report review queue remain local in files named `.private.*`. They are intentionally not in the return allowlist. Do not upload them or publish them to GitHub. No report is sent to a model or external service. The return contains only this stage's source, aggregate diagnostics, saved notebook, figure exports, and evidence. Review the return locally before sharing; file allowlists are not a universal privacy guarantee.

## Next score-bearing milestone (not authorized by running this notebook)

After we inspect coverage, gaps, disagreement and review feasibility, select a multilingual supervision method with recorded model/version/license and permitted data handling. Establish an independently checked target source and a representative, dependency-aware image pilot. Then compare fixed-encoder representations jointly and through removals: plane coverage, contrast choice, neighboring-slice context, full field versus local context, and a combined representation. Preserve per-label and macro AUC, matching evaluation rows, compute, uncertainty, and full comparison history. Do not score model inputs made from report-derived labels against those same report labels and call it image generalization.

Ensembling is a later controlled comparison, not a replacement for representation and supervision analysis. Neither feature count nor labeler assignment count establishes movement toward the competition record. The official leading score was not retrievable in this review; the benchmark ledger deliberately leaves it null.

## Preparation honesty

The package is prepared source and an unexecuted notebook. Static syntax/structure checks are not test execution. Run the supplied synthetic tests and pilot yourself. No success, clinical accuracy, AUC, cloud action, Git publication, or submission is implied by delivery.
