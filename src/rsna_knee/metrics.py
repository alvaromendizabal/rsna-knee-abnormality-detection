"""Strict 12-target macro AUC and submission validation; no model predictions made."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .schema import ContractError, LABELS, STUDY

def binary_auc(y_true, y_score) -> float:
    y, p = np.asarray(y_true, dtype=float), np.asarray(y_score, dtype=float)
    if y.ndim != 1 or p.shape != y.shape or not y.size:
        raise ContractError("AUC requires equal nonempty one-dimensional arrays.")
    if not np.isfinite(y).all() or not np.isfinite(p).all():
        raise ContractError("AUC does not accept unknown/NaN/infinite values.")
    if not np.isin(y, [0, 1]).all() or not ((p >= 0) & (p <= 1)).all():
        raise ContractError("AUC requires binary labels and probabilities in [0, 1].")
    positive, negative = int(y.sum()), int((y == 0).sum())
    if positive == 0 or negative == 0:
        raise ContractError("AUC undefined: both classes are required.")
    ranks = pd.Series(p).rank(method="average").to_numpy()
    return float((ranks[y == 1].sum() - positive * (positive + 1) / 2) / (positive * negative))

def macro_auc_12(truth: pd.DataFrame, predictions: pd.DataFrame) -> dict:
    """Published metric definition, not downloaded organizer scorer source.

    Requires all 12 labels to be evaluable. Never silently skip an undefined task.
    Input index must be unique study IDs, identically ordered in both frames.
    """
    if list(truth.columns) != LABELS or list(predictions.columns) != LABELS:
        raise ContractError("Metric needs the exact twelve ordered target columns.")
    if not truth.index.equals(predictions.index) or not truth.index.is_unique:
        raise ContractError("Metric indexes must be identical and unique.")
    per_label = {name: binary_auc(truth[name], predictions[name]) for name in LABELS}
    return {"macro_auc_12": float(np.mean(list(per_label.values()))),
            "per_label_auc": per_label, "n_labels": 12, "n_studies": len(truth)}

def validate_submission(predictions: pd.DataFrame, template: pd.DataFrame) -> None:
    if list(predictions.columns) != [STUDY, *LABELS] or list(template.columns) != [STUDY, *LABELS]:
        raise ContractError("Submission schema/order differs from the template.")
    if predictions.empty or len(predictions) != len(template):
        raise ContractError("Submission row count differs or is zero.")
    for frame in (predictions, template):
        ids = frame[STUDY].astype("string")
        if ids.isna().any() or ids.str.strip().eq("").any() or ids.duplicated().any():
            raise ContractError("Missing, blank or duplicate submission identifier.")
    if predictions[STUDY].astype(str).tolist() != template[STUDY].astype(str).tolist():
        raise ContractError("Submission identifiers/order differ from the template.")
    try:
        values = predictions[LABELS].to_numpy(dtype=float)
    except (ValueError, TypeError) as exc:
        raise ContractError("Non-numeric submission values.") from exc
    if not np.isfinite(values).all() or not ((values >= 0) & (values <= 1)).all():
        raise ContractError("Submission probabilities must be finite and in [0, 1].")
