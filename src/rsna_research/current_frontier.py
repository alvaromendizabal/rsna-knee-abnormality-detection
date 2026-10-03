"""Public-safe aggregate helpers for the current RSNA research frontier.

The functions operate on aggregate evidence only. They intentionally do not expose
study identifiers, predictions, private weights, cache shards, source handles,
cloud paths, or submission logic.
"""
from __future__ import annotations

from math import isfinite
from typing import Mapping


def aggregate_gain(candidate: float, baseline: float) -> float:
    """Return candidate minus baseline after validating probability-like scores."""
    if not all(isfinite(x) and 0.0 <= x <= 1.0 for x in (candidate, baseline)):
        raise ValueError("scores must be finite probabilities")
    return float(candidate) - float(baseline)


def screening_state(
    *,
    macro_gain: float,
    fold_gains: Mapping[str | int, float],
    bootstrap_positive_fraction: float,
    minimum_macro_gain: float = 0.0,
    minimum_bootstrap: float = 0.5,
) -> str:
    """Return ADVANCE or CLOSE for a bounded aggregate screening experiment."""
    values = [float(v) for v in fold_gains.values()]
    if not values:
        raise ValueError("fold_gains cannot be empty")
    if not isfinite(macro_gain):
        raise ValueError("macro_gain must be finite")
    if not 0.0 <= float(bootstrap_positive_fraction) <= 1.0:
        raise ValueError("invalid bootstrap probability")
    if (
        float(macro_gain) > float(minimum_macro_gain)
        and float(bootstrap_positive_fraction) >= float(minimum_bootstrap)
        and sum(v > 0.0 for v in values) >= (len(values) + 1) // 2
    ):
        return "ADVANCE"
    return "CLOSE"


def retention_state(*, candidate: float, baseline: float, valid: bool = True) -> str:
    """Classify aggregate evidence without treating every retained result as promoted."""
    if not valid:
        return "INVALID"
    gain = aggregate_gain(candidate, baseline)
    if gain > 0.0:
        return "RETAIN_POSITIVE"
    if gain < 0.0:
        return "SCIENTIFIC_NEGATIVE"
    return "INCONCLUSIVE"


def parent_reconstruction_summary(
    *,
    native_members: int,
    native_windows: int,
    a5_folds: int,
    rad_layouts: int,
    recovered_asset_bytes: int,
) -> dict[str, int | bool]:
    """Validate and summarize public-safe parent reconstruction counts."""
    values = {
        "native_members": int(native_members),
        "native_windows": int(native_windows),
        "a5_folds": int(a5_folds),
        "rad_layouts": int(rad_layouts),
        "recovered_asset_bytes": int(recovered_asset_bytes),
    }
    if any(v < 0 for v in values.values()):
        raise ValueError("reconstruction counts must be non-negative")
    return {
        **values,
        "core_trained_branches_restored": (
            values["native_members"] > 0
            and values["native_windows"] > 0
            and values["a5_folds"] == 5
            and values["rad_layouts"] > 0
        ),
    }
