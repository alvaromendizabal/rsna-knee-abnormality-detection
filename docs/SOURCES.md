# Research sources

Access/reference date: **2026-09-12**. URLs may evolve. This source list is not evidence that the user's account, data, or notebooks were inspected.

| ID | Primary source | Used for / limitation |
|---|---|---|
| S1 | [Kaggle: official data description](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/data) and [overview](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/overview) | CSV contract, train-only reports, twelve targets, macro AUC. Actual file contents must pass the user's audit. |
| S2 | [RSNA, AI Challenge: Knee MRI, August 5, 2026](https://www.rsna.org/news/2026/august/ai-challenge-knee-mri) | Organizer's multi-site, multilingual dataset context. Collection-level counts need not equal the currently downloadable training CSV. |
| S3 | [Bien et al., MRNet, PLOS Medicine, 2018](https://journals.plos.org/plosmedicine/article?id=10.1371/journal.pmed.1002699) | Knee MRI multi-plane/slice representations and study/patient partitioning considerations. Different tasks and evaluation; no direct score comparison. |
| S4 | [Irvin et al., CheXpert, 2019](https://arxiv.org/abs/1901.07031) | Report-label uncertainty as a supervision issue. Chest imaging, not knee MRI; proposed transfer must be tested. |
| S5 | [DICOM PS3.3, Image Plane Module](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.2.html) | Spatial position and orientation semantics for future geometry-aware slice ordering. M01 does not read DICOM pixels or headers. |
| S6 | [Plotly: renderers](https://plotly.com/python/renderers/) | Inline `plotly_mimetype` display in JupyterLab. User must save and reopen notebooks to inspect persistence. |
| S7 | [Official Kaggle CLI documentation](https://github.com/Kaggle/kaggle-cli/blob/main/docs/README.md) and [competition commands](https://github.com/Kaggle/kaggle-cli/blob/main/docs/competitions.md) | Token authentication and per-file download. Never omit the filename flag; no full-data fallback. |
| S8 | [Kaggle package, PyPI](https://pypi.org/project/kaggle/2.2.4/) | Pinned CLI release. Pinning is not evidence that this environment was executed or resolved here. |
| S9 | [Competition rules](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/rules) and [leaderboard](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/leaderboard) | User must review current constraints. Precise current leading score remains unverified. |

Participant observations, not substituted for primary evidence: a [first-hand data audit](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/discussion/734055) reported sparse gold labels; this package measures the counts rather than hard-coding that report. A [participant write-up](https://huggingface.co/blog/bishnoiyash/rsna-competetion) describes a validation contamination correction; no score from that write-up is used as the current leaderboard target.
