"""Held-out probability diagnostics for the authored public example.

These summaries describe synthetic probabilities. They neither calibrate a
model on evaluation labels nor establish performance on medical images.
"""
from __future__ import annotations

import numpy as np


def training_prevalence(labels, folds):
    """Predict each held-out row using only the other folds' target frequencies."""
    labels, folds = np.asarray(labels), np.asarray(folds)
    if labels.ndim != 2 or not len(labels) or not np.isin(labels, [0, 1]).all():
        raise ValueError("Expected a nonempty binary target matrix.")
    if folds.shape != (len(labels),) or folds.dtype.kind not in "iu" or len(np.unique(folds)) < 2:
        raise ValueError("Expected aligned integer assignments for at least two folds.")
    baseline = np.empty(labels.shape, dtype=float)
    for fold in np.unique(folds):
        baseline[folds == fold] = labels[folds != fold].mean(axis=0)
    return baseline


def probability_diagnostics(labels, probabilities, baseline, scanners, targets, *, bins=10):
    """Report proper losses, a fold-trained reference and equal-width reliability.

    Brier score is the mean squared probability error. Skill is 1 - model/reference
    Brier; zero means no improvement over the reference and negative is worse.
    Log loss clips only for its logarithm. Empty reliability bins are explicit.
    Scanner summaries are descriptive slices, with no independence or CI claim.
    """
    labels = np.asarray(labels)
    probabilities, baseline = np.asarray(probabilities), np.asarray(baseline)
    scanners = np.asarray(scanners)
    if (labels.ndim != 2 or not len(labels) or labels.shape[1] != len(targets)
            or not len(targets) or len(set(targets)) != len(targets)
            or not np.isin(labels, [0, 1]).all()):
        raise ValueError("Expected binary labels with one unique name per target.")
    for values in (probabilities, baseline):
        if (values.shape != labels.shape or values.dtype.kind not in "fiu"
                or not np.isfinite(values).all() or not ((values >= 0) & (values <= 1)).all()):
            raise ValueError("Expected aligned, finite probabilities in [0, 1].")
    if scanners.shape != (len(labels),) or not all(isinstance(x, str) and x for x in scanners.tolist()):
        raise ValueError("Expected one nonempty scanner name per row.")
    if type(bins) is not int or not 2 <= bins <= 100:
        raise ValueError("Reliability bins must be an integer between 2 and 100.")

    # Probability arrays may legitimately arrive as integer 0/1 values. Loss
    # arithmetic must use floating point, including for unsigned integer inputs.
    labels = labels.astype(np.float64, copy=False)
    probabilities = probabilities.astype(np.float64, copy=False)
    baseline = baseline.astype(np.float64, copy=False)
    squared = (probabilities - labels) ** 2
    reference_squared = (baseline - labels) ** 2
    clipped = np.clip(probabilities, 1e-15, 1 - 1e-15)
    log_loss = -(labels * np.log(clipped) + (1 - labels) * np.log1p(-clipped))

    def losses(rows, column=slice(None)):
        model = float(squared[rows, column].mean())
        reference = float(reference_squared[rows, column].mean())
        return {"brier": model, "baseline_brier": reference,
                "brier_skill": 1 - model / reference if reference > 0 else None,
                "log_loss": float(log_loss[rows, column].mean())}

    per_target = {}
    for index, target in enumerate(targets):
        p, y = probabilities[:, index], labels[:, index]
        assignments = np.minimum((p * bins).astype(int), bins - 1)
        reliability = []
        for bucket in range(bins):
            mask = assignments == bucket
            count = int(mask.sum())
            reliability.append({"lower": bucket / bins, "upper": (bucket + 1) / bins,
                "count": count, "mean_probability": float(p[mask].mean()) if count else None,
                "observed_fraction": float(y[mask].mean()) if count else None})
        per_target[target] = {**losses(slice(None), index), "prevalence": float(y.mean()),
                              "mean_probability": float(p.mean()), "reliability": reliability}
    return {"evidence_type": "SYNTHETIC_ONLY", "rows": len(labels),
            "baseline": "Training-fold target prevalence; held-out labels are excluded.",
            "scope": "Descriptive held-out diagnostics; no recalibration, threshold selection, confidence interval or medical validation.",
            "bin_convention": "Equal-width [lower, upper), except the last bin includes 1.",
            "macro": losses(slice(None)), "per_target": per_target,
            "by_scanner": [{"scanner": str(scanner), "rows": int((scanners == scanner).sum()),
                            **losses(scanners == scanner)} for scanner in np.unique(scanners)]}
