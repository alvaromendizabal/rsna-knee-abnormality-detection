"""Fixed acquisition descriptors, not yet proven disease predictors."""
from __future__ import annotations
import numpy as np
import pandas as pd
from .schema import ContractError, PLANES, STUDY

def acquisition_features(studies: pd.DataFrame, series: pd.DataFrame) -> pd.DataFrame:
    """Validated descriptors only; report/label columns are never accessed.

    An absent acquisition slot has count zero. This does not impute clinical labels.
    No dataset-fitted transform, feature selection, or disease prediction occurs here.
    """
    index = pd.Index(studies[STUDY].astype(str), name=STUDY)
    if not len(index) or not index.is_unique:
        raise ContractError("Feature rows require unique, nonempty study IDs.")
    if set(series[STUDY].astype(str)) - set(index):
        raise ContractError("Orphan series cannot enter a representation.")
    def counts(mask=None):
        selected = series if mask is None else series.loc[mask]
        return selected.groupby(STUDY).size().reindex(index, fill_value=0).to_numpy(dtype=float)
    total = counts()
    if (total == 0).any():
        raise ContractError("A study has no series; do not fabricate a representation.")
    features = {"series_count": total}
    for plane in PLANES:
        key, n = plane.lower(), counts(series["Anatomical_Plane"].eq(plane))
        features[f"{key}_count"], features[f"{key}_present"], features[f"{key}_fraction"] = n, (n > 0).astype(float), n / total
    for flag, key in (("Fluid_Sensitive", "fluid_sensitive"), ("Fat_Suppression", "fat_suppression")):
        n = counts(series[flag].eq(1))
        features[f"{key}_count"], features[f"{key}_present"], features[f"{key}_fraction"] = n, (n > 0).astype(float), n / total
    for fluid in (0, 1):
        for fat in (0, 1):
            mask = series["Fluid_Sensitive"].eq(fluid) & series["Fat_Suppression"].eq(fat)
            n, key = counts(mask), f"fluid{fluid}_fat{fat}"
            features[f"{key}_count"], features[f"{key}_present"] = n, (n > 0).astype(float)
            for plane in PLANES:
                m, slot = counts(mask & series["Anatomical_Plane"].eq(plane)), f"{plane.lower()}_{key}"
                features[f"{slot}_count"] = m
                features[f"{slot}_present"] = (m > 0).astype(float)
                features[f"{slot}_fraction"] = m / total
    features["planes_available"] = sum(features[f"{p.lower()}_present"] for p in PLANES)
    features["all_three_planes_present"] = (features["planes_available"] == 3).astype(float)
    features["plane_contrast_slots_available"] = sum(features[f"{p.lower()}_fluid{f}_fat{s}_present"]
                                                    for p in PLANES for f in (0, 1) for s in (0, 1))
    disagree = counts(series["Fluid_Sensitive"].ne(series["Fat_Suppression"]))
    features["fluid_fat_disagreement_count"], features["fluid_fat_disagreement_fraction"] = disagree, disagree / total
    result = pd.DataFrame(features, index=index)
    if not np.isfinite(result.to_numpy()).all():
        raise ContractError("Non-finite acquisition features.")
    return result

def feature_dictionary(columns) -> pd.DataFrame:
    return pd.DataFrame([{"feature": name, "family": "acquisition_coverage",
        "source": "per-study series descriptors", "available_at_inference": True,
        "uses_report_or_label": False, "learned_transform": False,
        "role": "coverage/quality candidate, not a proven disease predictor",
        "predictive_ablation_status": "not_run"} for name in columns])
