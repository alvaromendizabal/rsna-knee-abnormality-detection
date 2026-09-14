# RSNA Knee: evidence before scale

## Current evidence state

Prepared starter only. No project test, notebook, metadata audit, model fit, or Kaggle submission has been executed by the assistant. No AWS/GitHub account was inspected or changed for this milestone. The user reported launching `rsna-knee-abnormality-detection-dev`; actual instance settings remain user-verifiable. There is no established RSNA baseline or feature improvement in this project yet.

M01 is not an experiment estimating predictive value. It establishes the supervision and acquisition contract, provides a fixed candidate representation, and records what remains unknown. The 65 acquisition descriptors are not 65 independent signals and are not a substitute for image representations.

## Prediction and supervision contract

Official task: twelve study-level findings; the published objective is macro ROC AUC. `metrics.py` implements that definition, not a downloaded organizer scorer. Tests compare its binary AUC against the pairwise definition and exercise ties and undefined tasks. Before a real evaluation, reconcile any subsequently published organizer scorer and its handling of unusual inputs.

Reports are training-only material. Image-only inference must not require a report, gold label, post-hoc diagnosis, or an identifier shortcut. Blank clinical labels are unknown, never automatically negative. Availability of an explicit negative, positive, uncertain or unmentioned report finding is a separate modeling decision, not a CSV imputation operation. The supplied test examples are an execution/schema demonstration, not an independent validation cohort or a full hidden-test distribution. Example/train overlap, when present, is recorded rather than mistaken for a genuine held-out split.

M01 inspects label availability, not positive-label prevalence, gold correlations, weak-label accuracy, or per-report clinical content. Labels are parsed only for structural validity. Gold outcome inspection is deferred until we design the validation budget and document how repeated use of scarce annotations will be controlled.

## Validation gate before predictive research

1. Audit actual expert-label counts and partial labels. Check whether a patient linkage field or repeat-study relationship is available and permitted. A study-disjoint split is not proof of patient independence. Do not use report-text duplicates as a fabricated patient identifier.
2. Decide how scarce expert-labeled studies can support development and a final assessment. Do not hard-code a five-fold split before checking each target's class support. An infeasible final holdout should be documented, not described as untouched when it was repeatedly inspected.
3. Freeze study/group assignments in a private, versioned split manifest. Keep images and reports from the same study/group together. Record repeated patients, site/domain uncertainty and near-duplicate policies where measurable. Do not infer hospital or patient identifiers from UIDs as predictive inputs.
4. A report-labeling system tuned against gold is part of training. Cross-fit it or exclude evaluation gold from its tuning. In a conservative image-evaluation design, exclude held-out gold-study images and reports from model training. Any transductive or self-supervised exposure requires an explicit separately labeled protocol and competition-rule review.
5. Fit preprocessing statistics, learned selection, embeddings adapted on this dataset, calibration and ensemble weights only in their designated training partitions. Off-the-shelf frozen pretrained weights require license and contamination/provenance review; public availability alone is insufficient.
6. Preserve out-of-fold predictions, study order, source labels, target masks, model/code/data/split hashes and failure records. Undefined per-fold AUC stays undefined. Never silently drop a rare target and call the remaining average the official twelve-target metric. A pooled twelve-target OOF estimate is usable only if each target has both classes and the predictions satisfy the stated split protocol.

## Controlled feature investigations

Use an explicit fixed baseline, same evaluation rows, same backbone/optimization budget, same preprocessing and seed wherever feasible. Each contrast registers the family, mechanism, leakage conditions, expected information gain and decision rule before execution. Large families receive matched additions and useful removals; interactions receive a small factorial design rather than unlimited combinations.

A future results record must contain: run ID; hypothesis ID; data/split/label-source hashes; feature and model configuration; observed fits; elapsed time and resource settings; per-label and macro AUC; label support; per-fold results; paired uncertainty; inference feasibility; decision; and source artifacts. No numeric improvement threshold is fabricated before the size and uncertainty of the validation cohort are understood.

Use paired study-level bootstrap differences when studies are the defensible independent unit; use patient-cluster resampling when linkage exists. Acknowledge small-sample and adaptive-selection uncertainty. Distinguish weak-label agreement, expert-label image AUC, public leaderboard AUC and private leaderboard AUC. Do not compare MRNet's three-task evaluation with this competition's twelve-task macro AUC as though they share a benchmark.

## Prioritized rounds (prepared hypotheses, not executed experiments)

| Round | Question and proposed controlled comparisons | Gate before compute |
|---|---|---|
| M01 — this package | What supervision and plane/contrast coverage actually exist? Fixed acquisition descriptors; no disease prediction. | Synthetic tests; five CSV contracts; verified stage resume; visible saved figures. |
| M02 — supervision and validation | How should report-derived positives, negatives, uncertainty and unmentioned findings be represented? Explicit masks and evidence spans; compare carefully audited extraction policies. | Gold-use protocol, patient/repeat-study risk review, report-language review, allowed-tool/data check. No external report transfer by default. |
| M03 — bounded DICOM/representation audit | Can a small, stratified image sample be decoded, ordered and normalized reproducibly? Geometry sorting, spacing/orientation flags, fixed slice coverage, plane/contrast selection. | Actual per-file sizes, selected-image allowlist, privacy review, cache budget, codec tests; no full archive. |
| M04 — first predictive representation contrasts | Under one modest fixed image encoder: one plane versus complementary planes; uniform slices versus neighboring-slice context; fluid-sensitive and fat-suppressed choices; masked missing views. | Frozen validation; verified labels; tiny image smoke test; checkpoint replay; bounded single-fold fit. |
| M05 — anatomy and multiscale context | Do local ligament/meniscus/cartilage/marrow/fluid representations add information beyond global image context? Matched crops, scales and representation removals. | Localization correctness and inference feasibility; no assumed external segmentations or trusted medical annotations. |
| M06 — multimodal supervision and robustness | Does training-only image–report alignment or uncertainty weighting improve image-only gold AUC? Test site/quality shift and complementary interactions. | M02–M05 evidence, provenance/license review, stable evaluation, no held-out report tuning. |
| Later — evidence-driven model work | Does model capacity, optimization, calibration or OOF blending address the observed residual bottleneck? | A demonstrated need and a controlled compute budget; features remain an open research track. |

## Mechanisms and domain sources

MRNet is primary evidence for multi-plane knee MRI representations and slice aggregation, not proof that its architecture or published score transfers directly here [S3]. DICOM geometry defines spatial position/orientation and motivates checking geometric slice order rather than assuming filenames or instance numbers are anatomical order [S5]. CheXpert is evidence that report-derived uncertainty is a real supervision design issue in a different imaging domain; its policies are hypotheses for knees, not established winners [S4]. The organizer describes multi-site, multilingual training material, motivating domain and language auditing rather than assuming a homogeneous dataset [S2].

The current feature registry deliberately distinguishes acquisition availability from the actual tissue findings a model must learn. Future anatomy concepts include ligament integrity, meniscal morphology, compartment-specific cartilage changes, marrow abnormalities and joint-fluid patterns, aligned to the twelve task labels. These are research directions requiring validated representations, not clinical decision rules or deployable diagnoses.

## Competitive benchmark discipline

`configs/benchmark.json` records the official leaderboard URL and a null current top score. A precise current leader score was not extractable from the public page during preparation. Do not substitute a stale participant score, rounded third-party number, or local cross-validation score. Record a user-observed leaderboard screenshot with date, metric, public/private status, score and relevant constraints. Leaderboard improvements must be tied to the exact submitted artifact; local ablations do not establish that the project has beaten Kaggle.

## Publishing and safety

Keep all raw CSVs, reports, DICOM images, individual predictions, study IDs and fitted weights private unless their specific release is permitted. This starter does not choose a permissive repository license on the user's behalf. Review code, third-party licenses and competition terms before public publication. Executed notebooks intended for employers must contain only permissible aggregate evidence, a reproducible source lineage, and visible charts. No claim of clinical validity or deployment readiness is made.
