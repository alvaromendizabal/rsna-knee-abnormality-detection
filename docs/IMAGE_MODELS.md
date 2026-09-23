# Image-model research record

## Objective and evaluation boundary

The competition objective is macro-ROC-AUC across twelve MRI findings. Brier score is used only as a probability-error diagnostic. AWS holds the private research workspace and large immutable artifacts; GitHub contains curated aggregate evidence.

## Model families and provenance

The independent DINOv2 system uses plane-preserving MRI windows, a DINOv2-Small backbone, and target-specific aggregation. Its historical diagnostic predictions are development evidence, not untouched validation.

The public Raptor branch uses a CoAtNet/RMLP backbone with 1,024-dimensional window features, target-attention pooling, and twelve target-specific outputs. The transferred checkpoint contains about 73.1 million parameters. The public source and weight dataset are attributed in [SOURCES.md](SOURCES.md); training-membership and model-selection claims from those sources are not treated as independently verified facts.

## Input fidelity and ablations

Stage 24 reconstructed a complete real study, verified DICOM identifiers/order/spacing/decoding, and reproduced the public 64-image / 42-window representation. Later stages reused encoded features to evaluate fluid-only, within-series, boundary-window, and full-input variants without unnecessary re-encoding.

Stage 25 found that full input did not outperform the fluid-only ablation on the first development cohort. Stage 26 found no macro-AUC gain from removing only boundary-crossing windows. Those branches were not expanded.

## Heterogeneous ensemble research

A 90/10 full-Raptor/DINO mixture screened positively on the original development pilot but **failed** on a separate cohort: macro-AUC fell from 0.922410 for fluid-only Raptor to 0.919150. The failed primary result remains part of the public record.

A predefined 90% fluid-only Raptor + 10% DINOv2 secondary arm scored 0.926383 on that replication cohort and later passed a separate development qualification gate. Because the weight was not learned from fold-complete OOF predictions, this evidence remained developmental rather than final.

## Stage 31 — deployment fidelity

The fixed fluid-Raptor/DINO candidate was converted into a deterministic offline inference package. After earlier packaging problems were diagnosed and corrected, the final release required a hermetic local shadow before any remote update.

The accepted offline Tesla T4 preview completed all three visible studies in **39.87 seconds**. Maximum AWS-versus-GPU differences were:

| Component | Max absolute difference | Acceptance limit |
|---|---:|---:|
| DINOv2 | 1.043e-6 | 1e-3 |
| Raptor | 5.960e-7 | 1e-4 |
| 90/10 blend | 5.782e-7 | 1e-4 |

Both actual checkpoints loaded strictly. The release produced one guarded candidate submission, **56476938**. The numerical agreement establishes implementation fidelity—not an AUC improvement.

## Stage 32 — bottleneck moved to training

The candidate remained pending in the returned Stage-32 score evidence. The scored reference remained **0.933**, versus **0.958** on the same returned leaderboard page.

More importantly, the training-frontier audit found that the accepted exact-window cache covered only **960 / 4,407 studies (21.8%)**. Current official metadata matched the accepted AWS copies, but recent release work used frozen checkpoints. A current full-data retraining result does not yet exist.

## Leading-system reproduction matrix

| Capability | Verified scope | Remaining gap |
|---|---|---|
| Public multi-model reference ensemble | Official public score 0.933; inference reproduced | Independent ensemble training not recreated |
| Raptor on AWS/Kaggle | Strict loading, real-input parity, missing-view execution, CPU/GPU parity | Strong grouped training reproduction absent |
| Independent DINOv2 | Existing trained checkpoint and verified deployment parity | Fold-complete grouped training / OOF absent |
| Window variants | Controlled cached ablations | No primary macro-AUC gain; stopped |
| Full-Raptor/DINO primary blend | Pilot + disjoint-cohort replication | Failed replication; stopped |
| Fluid-Raptor/DINO candidate | Separate qualification + deterministic release | Official score pending in Stage-32 evidence |
| Complete-data training system | Partial cache only | 3,447 studies still outside accepted cache |
| OOF ensemble | Not established | Requires grouped fold-complete predictions |

## Prioritized research decision

The next credible score-moving program is:

1. complete current-data cache coverage;
2. freeze scanner-grouped folds with expert studies audit-only;
3. reproduce a strong grouped baseline;
4. test one structurally new training mechanism at a time;
5. escalate only when the official local objective improves materially;
6. learn ensemble weights from OOF predictions.

This is a ceiling-escape decision: deployment plumbing is no longer allowed to substitute for a stronger learned system.

## Sources and limitations

See [SOURCES.md](SOURCES.md) for competition, DINOv2, Raptor, and participant-research references. Participant write-ups are treated as hypotheses to reproduce, not as our experimental results.

Run receipts and aggregate calculations for the current publication are indexed in `reports/training_frontier/results.json`. Raw images, reports, study IDs, row-level predictions, checkpoints, and private cloud logs are deliberately not redistributed.
