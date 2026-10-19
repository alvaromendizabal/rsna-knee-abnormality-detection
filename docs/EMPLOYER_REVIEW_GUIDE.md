# Technical review guide

Start with the [case study](EMPLOYER_CASE_STUDY.md), then the
[three-chart executed analysis](../notebooks/01_context_evaluation.ipynb).
The [reproduction guide](REPRODUCIBILITY.md) explains the public training path.

| Review question | Code and tests |
|---|---|
| Is acquisition leakage prevented? | `src/rsna_review/public_pipeline.py`, `tests/test_public_pipeline.py` |
| Are slices sorted by actual spatial geometry? | `src/rsna_research/pixels.py`, `tests/test_research_pixels.py` |
| Does batching change attention normalization? | `src/rsna_research/image_models.py`, `tests/test_image_models.py` |
| Are probabilities tested against a meaningful control? | `src/rsna_review/diagnostics.py`, `tests/test_probability_diagnostics.py` |
| Can corrupt work be reused? | `tests/test_public_pipeline.py`, `tests/test_metrics_and_evidence.py` |
| Can a saved chart or metric be altered undetected? | `src/rsna_review/evidence.py`, `tests/test_public_review.py` |

Only the final-result evaluation, necessary controls and maintained implementation
contracts are presented. The exact private MRI training/inference recipe is not
part of the public reference. Neither synthetic AUC nor an integration pass is
presented as clinical validation.
