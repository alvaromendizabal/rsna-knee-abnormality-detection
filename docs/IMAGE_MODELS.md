# Image-model research record

## Objective and execution boundary

Predict twelve MRI findings with image-only inference and macro-ROC-AUC as the competition objective. Brier score is a probability-error diagnostic, not a substitute objective. AWS holds the research workspace and large immutable assets; GitHub contains the curated public evidence. The original AWS workspace is an exported source tree without Git metadata. Publishing this record does not initialize, reset, relocate, or mirror that workspace.

## Architecture and provenance

The independent DINOv2 system uses plane-preserving MRI windows and target-specific aggregation. Its previously completed 58-study diagnostic predictions, using `uniform24`, were reused rather than running the encoder again. Historical gold-data exposure limits subsequent validation claims.

The public Raptor branch uses `coatnet_rmlp_2_rw_384.sw_in12k_ft_in1k`, 1,024-dimensional window features, layer normalization, a 256-unit target-attention network, and twelve target-specific classifier vectors. Images are encoded in small batches; normalized features are concatenated before target-wise softmax over the entire study. Independent microbatch softmax would change the model. The public audit module demonstrates the pooling and fixed-blending contracts; it is not presented as the full private training pipeline.

Checkpoint: `raptor_ft_coatnet_v4_full.pt`, 292,829,402 bytes, 73,136,096 parameters. SHA-256: `89606f05849838529e1b4658d28fb049623205d9853371548403bca460361ded`. Dataset: `dreaddevelopment/raptor-knee-widedense`; source notebook: `hdhsjdjd/rsna-knee-raptor-coatnet`. The author's dataset metadata reports CC0 and exclusion of the 58 structured-label studies from fitting; those are source claims, not independently verified training-membership or selection-exposure guarantees. The Stage-22 preview did not record weight bytes, so byte identity between that preview and the later AWS download remains unproven.

## Input-fidelity and ablation results

Stage 23 verified strict checkpoint loading and synthetic inference. Stage 24 subsequently reconstructed one complete real study from 98 DICOM files, verified identifiers, ordering, spacing, integrity, and decoding, and matched the reference's 64-image stack and 42 image windows exactly. A version-bound range reader avoided a full approximately 265 GB archive download. Stage 24's microbatch probability discrepancy was approximately 6e-8. That was an engineering test, not an accuracy result.

The representation allocates slice ranges of 18, 14, 12, 8, and 12 to five source-selected MRI series. Forty-two triplets divide into 24 purely fluid-sensitive windows, 12 purely non-fluid windows, and six mixed-series boundary windows. The 30-window arm includes mixed pixels and is not a fluid-only model.

Stage 25 compared full versus fluid-only inference on twelve labeled studies. Stage 26 reused the cached features to separate contrasts from boundary windows. Removing only boundary windows did not improve AUROC: full42 and within36 both scored 0.934711. The branch was stopped rather than expanding the dataset on a weak result.

## Heterogeneous ensemble: screening versus replication

Sixteen combinations were retrospectively screened on the original twelve studies. A 90/10 full-Raptor/DINO mixture reached 0.942041 versus 0.937315 for fluid-only Raptor. The weight was selected after reviewing those results; the pilot is not independent evidence.

Stage 27 froze that primary recipe and used twelve different eligible studies, selected by fixed identifier-hash order with explicit file-size bounds. All labels were complete, and all twelve targets contained both classes. No blend weights were fitted on replication rows. The primary recipe scored 0.919150 versus 0.922410 for fluid-only Raptor and crossed its -0.002 AUROC kill threshold. It was rejected even though Brier improved by 0.007190.

The predefined secondary fluid-Raptor/DINO blend scored 0.926383 with Brier 0.178305. Its +0.003974 AUROC signal is hypothesis-generating; it is not a successful primary confirmation. A further fixed-cohort evaluation, not another weight sweep, is the next limited test.

## Statistical limitations

Both cohorts are selected small development subsets with complete five-view inputs. They do not represent every acquisition pattern. Public-checkpoint fitting membership and best-epoch selection exposure are not independently established. DINO gold-data use also prevents untouched-holdout claims. There are no OOF or clinical-validation claims.

For the failed primary comparison, 1,000 paired study bootstrap draws produced only 464 defined twelve-target macro-AUC values; 536 lacked both classes for at least one target and were counted as undefined. The retained-draw AUC interval was [-0.034449, 0.028723]. This is conditional within-cohort sensitivity, not a confidence guarantee adjusted for historical model selection. Rare-target class support must remain visible.

## Leading-system reproduction matrix

| Component | Verified scope | Remaining gap |
|---|---|---|
| Public multi-model ensemble containing Raptor | Inference preview and official public score 0.933 | Ensemble training not recreated; not standalone Raptor |
| Raptor CoAtNet on AWS | Strict loading, complete real-input parity, global attention, labeled ablations | Broader/missing-view validation and training reproduction |
| Independent DINOv2 | Existing trained checkpoint and diagnostic predictions | Competitive multi-fold training and independent OOF complementarity |
| Window-mask variants | Four arms evaluated from cached features | No AUROC improvement for the primary boundary-removal candidate; stopped |
| Full-Raptor/DINO blend | Pilot screen followed by disjoint-cohort development replication | Failed primary replication; stopped |
| Fluid-Raptor/DINO blend | Predefined secondary arm with gains in both observed cohorts | New fixed-cohort confirmation and end-to-end submission qualification |

## Submission gate and prioritized backlog

1. Finish the fixed secondary-candidate confirmation without revisiting the 24 exposed studies. Require all twelve evaluable targets and at least six studies; otherwise record insufficient support. No automatic submission.
2. Before any new entry, bind exact checkpoints, inference strategy, preprocessing, target order, missing-view behavior, and output identifiers to a deterministic submission manifest. Validate the deployed system rather than assuming cached diagnostic predictions reproduce the existing reference ensemble.
3. The larger competitive capability gap is a strong independently trained, grouped/multi-fold image system with comparable OOF predictions and stronger supervision. That gap is not solved by a positive twelve-study diagnostic or by polishing documentation.

The dated public-leaderboard target is 0.958 versus the reference ensemble's 0.933. No public evidence establishes that the proposed blend exceeds either. Preserve both accepted submissions; status reads do not require repeat submissions.

## Sources

- Competition and metric: https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/overview/evaluation
- Raptor source: https://www.kaggle.com/code/hdhsjdjd/rsna-knee-raptor-coatnet
- Author checkpoint dataset: https://www.kaggle.com/datasets/dreaddevelopment/raptor-knee-widedense
- DINOv2: https://arxiv.org/abs/2304.07193
- Attention-based multiple-instance learning: https://proceedings.mlr.press/v80/ilse18a.html

Run receipts and aggregate calculations are indexed in `reports/image_models/results.json`. Private source returns, raw images, reports, study IDs, feature arrays, and weight bytes are deliberately not redistributed.
