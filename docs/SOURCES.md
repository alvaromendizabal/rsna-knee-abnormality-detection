# Research sources

Reference date: **2026-09-23**. Sources document the recorded model lineage and public numerical/data contracts; they do not replace executed project evidence.

| ID | Primary source | Used for / limitation |
|---|---|---|
| S1 | [Kaggle competition overview and evaluation](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/overview/evaluation) | Official twelve-target macro-ROC-AUC objective and submission context. |
| S2 | [Kaggle data page](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/data) | Competition data contract. Actual file identity is verified separately in project evidence. |
| S3 | [Competition rules](https://www.kaggle.com/competitions/rsna-knee-abnormality-detection/rules) | External-data and notebook constraints. |
| S4 | [DINOv2 paper](https://arxiv.org/abs/2304.07193) | Self-supervised vision backbone used by the independent image branch. |
| S5 | [Raptor CoAtNet source notebook](https://www.kaggle.com/code/hdhsjdjd/rsna-knee-raptor-coatnet) | Public inference/training mechanism studied and independently adapted. |
| S6 | [Raptor weight dataset](https://www.kaggle.com/datasets/dreaddevelopment/raptor-knee-widedense) | Public checkpoint provenance; source claims about training membership remain source claims. |
| S7 | [Attention-based deep multiple-instance learning](https://proceedings.mlr.press/v80/ilse18a.html) | Attention pooling background. |
| S8 | [DICOM PS3.3 Image Plane Module](https://dicom.nema.org/medical/dicom/current/output/chtml/part03/sect_C.7.6.2.html) | Physical image orientation/position semantics used in geometry-aware preprocessing. |


## Evidence boundary

The public repository distinguishes:

- **external source claims** — attributed above;
- **public reference controls** — clearly separated from the private model;
- **our executed evidence** — aggregate metrics and receipts promoted only after returned runs verify them.
