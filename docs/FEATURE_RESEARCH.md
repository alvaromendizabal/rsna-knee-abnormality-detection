# Two bounded feature-research rounds

## Current evidence and scope

Prepared source, notebooks, tests and experiment definitions are not executed results. No returned M01 package or measured AUC accompanied this request. The user's reported progress is completion of setup through the start of metadata acquisition. No baseline, predictive gain, final split, or current leaderboard benchmark is inferred.

The package deliberately separates (1) correct feature construction, (2) feasibility on a small sample, and (3) predictive value on a defensible evaluation. Only the first two are actionable before the data/supervision audit is reviewed. Both rounds contain executable implementations and 12 inline Plotly figures, not just literature lists. They do not train models.

## Round 1 — protocol-aware multi-view representations

**Question:** Which complementary views and contrasts are available, and can we encode/select them consistently without report or label leakage?

Preserve the 65 M01 descriptors. Add 65 explicitly constructed descriptors across eight families: within-plane conditional contrast composition (12), plane diversity (6), contrast-pair balance (6), cross-plane agreement (9), cross-plane imbalance (12), protocol diversity (5), nonredundant selection efficiency (6), and fluid-view context (9). These total 130 columns, but redundant/constant columns are measured rather than advertised as independent information.

Use metadata from inference-available sources only. UID strings are keys, never predictor columns. Missing acquisition counts can be zero; missing disease labels are not converted to zero. All expert-labeled studies and unlabeled exact-report duplicates of them are reserved from this exploratory pool. This reservation is not an approved patient/site split and does not establish that the reserved cases are a sufficient untouched final test.

The notebook constructs features, pauses after a saved stage, resumes with checksum verification, profiles the unlabeled pool, records constants and exact duplicates, and creates a deterministic two-study pilot plan. It selects at most one preferred series per available plane, with a fixed fluid-sensitive/fat-suppressed preference and a deterministic hash tie-breaker. It does not use image labels to choose favorable examples.

**Next predictive experiment, once supervision is approved:** hold the image encoder, training rows, preprocessing, schedule and view count fixed. Compare the same image baseline with and without protocol-aware routing/missing-view context; then use planned family additions/removals. Include an acquisition-only negative-control model to diagnose shortcut learning, not as a substitute for image understanding. Evaluate acquisition/site generalization explicitly when valid identifiers become available.

## Round 2 — image-scale and through-slice representations

**Question:** Can we recover stable local and across-slice image information, preserve physical geometry, and compare a whole view with a fixed center window?

Eight families: intensity distributions, signal tails, in-plane gradients, 16-bin co-occurrence texture, image-relative patch heterogeneity, slice context, multiscale context, and physical geometry. The specified implementation produces 64 image descriptors for each of two predefined fields of view plus 12 geometry/quality descriptors: **140 per series**. A view-preserving study matrix has 420 descriptor slots plus three view-presence indicators. Missing views remain missing in that matrix; future imputation belongs inside training folds.

The complete-series reader checks UID/metadata agreement, MR modality, single-frame monochrome encoding, dimensions, spatial tags, consistent orientation/spacing, duplicated positions, excessive slice gaps, and burned-in-annotation flags. It orders slices by the normal-vector projection of ImagePositionPatient, not lexical filenames or InstanceNumber. Unsupported enhanced multi-frame MR, invalid geometry, unavailable compressed-pixel codecs, and mismatched planes stop the stage rather than trigger speculative repairs.

Normalization is fixed within each series (1st/99th percentile clipping/scaling), after modality transforms and MONOCHROME1 polarity handling. Padding remains masked. The center window uses 75% of image height/width and retains the full-view normalization. No anatomical segmentation, isotropic resampling, quantitative MRI mapping, or IBSI benchmark verification is claimed. Image-relative 3x3 patches are not named ligament/meniscus/cartilage regions.

Only one complete planned series is downloaded and processed at the first gate, with 8-96 slices, 256 MiB uncompressed download cap, 16 MiB per slice, and a 300-second local worker limit. Re-running the same notebook must reuse the saved series with zero newly computed series. Multiple planes of one study are not separate independent validation patients.

**Next predictive experiment, once supervision and an adequate sample exist:** freeze the same encoder and evaluation rows. Test full view versus full-plus-center context, single-slice versus adjacent-slice context, and protocol-aware multiview aggregation. Handcrafted descriptors are supporting probes; learned MRI representations and anatomically meaningful crops remain higher-priority later directions. Generic scalar radiomics cannot be assumed to outperform modern learned features.

## Equal experimental discipline

Each round includes a domain mechanism, inference-time availability boundary, deterministic transformations, edge-case tests, immutable inputs, keyed checkpoints, source/environment/configuration lineage, finite-value checks, family registry, 12 inline plots, explicit rejection criteria, and a bounded user-run return package. Neither round uses feature count, descriptive variation or apparent medical plausibility as proof of AUC gain.

## Supervision, metric and benchmarking gate

The existing M01 contract uses twelve targets and macro ROC AUC. The current Kaggle Data/Evaluation web pages did not expose readable bodies during this preparation, so the official scorer, current leading score, exact live rules, and inference contract were not independently revalidated. The package preserves the earlier contract and fails closed on schema mismatch. A code-ready paired, group-bootstrap holdout comparison is provided in `src/rsna_research/comparison.py`; it does not train or evaluate anything unless the user explicitly calls it with real, approved, aligned predictions.

Before fitting: inspect actual label availability and inference rules; establish patient/group handling and site robustness; freeze the evaluation row manifest; decide how scarce expert labels are protected; specify training-only report supervision; validate the metric against the competition definition; and register the matched comparisons. Never use reports as inference features when absent from evaluation. Do not auto-label unmentioned findings negative. No external report transfer, LLM API, pretrained model download, leaderboard submission or ensemble is enabled by these notebooks.

A paired holdout confidence interval is conditional on the fitted models and evaluation sample. It is not an adjustment for many adaptive trials. Undefined labels are not silently dropped. If bootstrap resampling repeatedly loses a class, the interval remains unavailable instead of manufacturing a number.

## Primary sources and what they support

1. RSNA, 2026 challenge announcement: https://www.rsna.org/news/2026/august/ai-challenge-knee-mri — knee structures, multilingual reports and multi-site data motivate image and supervision research. It does not establish the benefit of any implementation in this package.
2. Bien et al., MRNet (2018): https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1002699 — primary knee-MRI evidence motivating complementary planes and slice aggregation; different dataset/tasks, not a leaderboard comparison.
3. Pydicom pixel-data guidance: https://pydicom.github.io/pydicom/stable/guides/user/working_with_pixel_data.html — pixel decoding, transformations and codec requirements; not proof of clinical or algorithmic validity.
4. DICOM Image Plane module: https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.2.html — physical position/orientation semantics. Verify support for actual encountered image objects.
5. Zwanenburg et al., IBSI reference manual: https://arxiv.org/abs/1612.07003 — standardized definitions and benchmark verification matter; this package's image descriptors are intentionally NOT described as certified IBSI radiomics.
6. Plotly renderers: https://plotly.com/python/renderers/ — inline Plotly display. Notebook rendering still requires the user's saved-output/reopen check.

Prepared on 2026-09-12. Public-source research is separate from user data evidence. No clinical diagnostic advice is provided by this software.

## Access correction

Browser OAuth replaces manual API-token and copied-link entry. Both feature implementations remain unchanged. Image-location resolution is performed internally through the official client, with body reads still subject to the range-only guards. No new predictive result is claimed.
