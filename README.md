# Knee MRI: reliable multi-label modeling

**Medical-imaging ML · scanner-aware validation · recoverable inference**

![Knee MRI engineering](docs/assets/portfolio-hero.svg)

A twelve-finding MRI project with scanner-disjoint evaluation, ordered cross-slice
context, and strict separation between model quality, inference equivalence, and
clinical validity. The public release contains the numerical and data contracts,
a fitted CPU reference, a browser training demonstration, and reproducible final
aggregate analysis—without publishing patient data or the private model recipe.

| Evidence | Recorded result and scope |
|---|---|
| External evaluation | **0.943** macro ROC-AUC; historical external record |
| Grouped development | **4,349 studies**, **59 scanner groups**, zero cross-fold scanner overlap |
| Ordered context | **0.7943834 → 0.7978448** on the same grouped development population |
| Narrower extension | **0.7978946** point estimate; paired interval crossed zero, so the increment remains inconclusive |

[Case study](docs/EMPLOYER_CASE_STUDY.md) · [Architecture](docs/ARCHITECTURE.md) ·
[Review guide](docs/EMPLOYER_REVIEW_GUIDE.md) · [Reproduce](docs/REPRODUCIBILITY.md) ·
[Final scope](docs/PROJECT_CLOSEOUT.md) ·
[Interactive engineering lab](https://alvaro-rsna-engineering-lab.tartmacaw2.chatgpt.site)

## Run the public review

```bash
python3 -S review/run.py --output /tmp/rsna-review --with-node
python3 -S review/run.py --output /tmp/rsna-review --with-node --check
```

Python 3.11+ and Node.js are sufficient for the walkthrough, evidence verification,
and browser-training contracts. Open the generated `index.html` to inspect each
engineering decision, its implementation, and the tests behind it.

For actual CPU fitting, install the hash-pinned [requirements-review.lock](requirements-review.lock)
and run [examples/run_public_pipeline.py](examples/run_public_pipeline.py). It fits
12 logistic models on authored features, evaluates scanner-disjoint folds, reports
AUC/Brier/log loss and reliability counts, and can resume verified checkpoints.
**All public training outputs are `SYNTHETIC_ONLY`; they are not MRI performance.**

## Maintained implementation

| Component | Why it is here |
|---|---|
| `src/rsna_knee/schema.py` | Twelve-label order, missing-label semantics, safe metadata joins |
| `src/rsna_research/pixels.py` | Physical slice ordering, safe DICOM decoding and within-series normalization |
| `src/rsna_research/image_models.py` | Stable global attention pooling across encoding microbatches |
| `src/rsna_research/comparison.py` | Paired grouped uncertainty without resampling individual correlated rows |
| `src/rsna_review/public_pipeline.py` | Fitted CPU reference, group isolation, train-only preprocessing and exact resume |
| `src/rsna_review/diagnostics.py` | Probability diagnostics against training-fold prevalence |
| `notebooks/01_context_evaluation.ipynb` | Executed final-result arithmetic, population counts and uncertainty plots |

The final result does not depend on the retired experiment launchers or old AWS
spaces. The public data/recovery contracts and reference examples are independently
testable. Restricted MRI/DICOM files, study identifiers, private predictions,
weights, tuned inference recipes and private checkpoints are excluded.
The external and grouped development scores are **not directly comparable**.
[Sources and attribution](docs/SOURCES.md) remain explicit. This is research
software, not a diagnostic device or a clinically validated service.
