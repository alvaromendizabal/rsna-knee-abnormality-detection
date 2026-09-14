# Feature research roadmap

Feature engineering remains open until the major high-value MRI representation families have been tested through controlled ablations.

| Priority | Family | Primary hypothesis | Promotion evidence |
|---|---|---|---|
| 1 | Plane + contrast complementarity | Different planes/contrasts expose different lesion morphology | Macro AUC addition/removal gain on identical rows and budget |
| 2 | Slice context + position | Through-slice continuity distinguishes focal findings from noise | Stable per-finding and macro AUC improvement |
| 3 | Anatomical field of view | Ligament, meniscus, OA and effusion tasks benefit from different spatial emphasis | Matched whole-knee vs localized-view ablation |
| 4 | Geometry/acquisition robustness | Spacing, orientation and protocol variation modulate representation quality | Robustness gain without leakage or site proxy dependence |
| 5 | Multiscale texture/context | Fine morphology and coarse structural context are complementary | Addition/removal gain after fixed baseline |
| 6 | Missing-view robustness | Explicit missing-view handling is better than implicit zero filling | Stable gain under view-drop stress tests |
| 7 | Learned embeddings | Pretrained image representations may capture morphology handcrafted summaries miss | Controlled encoder comparison under same folds |
| 8 | Ensemble diversity | Complementary models can help after individual representations are validated | OOF-only ensemble gain and diversity diagnostics |

No family is promoted merely because it creates many columns or receives high feature importance.
