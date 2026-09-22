# Project status

Updated from the verified Stage-27 return, completed **2026-09-22 02:06:39 UTC**.

## Completed publication milestone

Stage 27 executed 32 successful gates and 278 regression tests on 12 studies disjoint from the original twelve-study pilot. Runtime was 649.953 seconds. All 1,769 DICOM inputs were reused from local storage; 504 Raptor windows were newly encoded. There were no training fits, GPU launches, new cloud jobs, package installations, submissions, or S3 writes.

**Experiment outcome: STOP_FIXED_BLEND_DIRECTION.** The primary full-Raptor/DINO blend lost 0.003260 AUROC against fluid-only Raptor. Its lower Brier score does not change that decision. The predefined fluid-Raptor/DINO secondary arm gained 0.003974 AUROC, but selecting it now is exploratory and requires a new, fixed-cohort test.

## Competition state

The last recorded public score is **0.933** for the reproduced public reference ensemble (submission 56442573), compared with **0.958** on the same returned leaderboard page. Snapshot: 2026-09-22 02:06 UTC. Submission 56441830 was complete with a blank score. Neither result should be resubmitted merely to refresh its status.

## Next decision

Freeze the 90% fluid-Raptor / 10% DINO candidate and test it on eligible structured-label studies not used in either preceding cohort. Do not tune new weights or pool cohorts to rescue a failed primary result. Qualification still requires adequate class support, compatible end-to-end inference, missing-view handling, exact model provenance, competition-rule checks, and one guarded submission identity.

The publication milestone is complete; the competitive research program and submission qualification are not. See [the current notebook](../notebooks/06_image_models_and_replication.ipynb) and [research record](IMAGE_MODELS.md).
