"""Public-safe aggregate helpers for the current RSNA research frontier.

The functions operate on aggregate metrics only. They intentionally do not expose
study identifiers, predictions, private weights, cache shards, or submission logic.
"""
from __future__ import annotations
from math import isfinite
from typing import Mapping

def public_score_gap(incumbent: float, leader: float) -> float:
    if not all(isfinite(x) and 0.0 <= x <= 1.0 for x in (incumbent, leader)):
        raise ValueError("scores must be finite probabilities")
    return round(float(leader) - float(incumbent), 12)

def aggregate_gain(candidate: float, baseline: float) -> float:
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

def promoted_residual_summary(
    *,
    baseline: float,
    candidate: float,
    all_folds_positive: bool,
    protected_target_count: int,
) -> dict[str, object]:
    gain = aggregate_gain(candidate, baseline)
    return {
        "gain": gain,
        "all_folds_positive": bool(all_folds_positive),
        "protected_target_count": int(protected_target_count),
        "promoted": gain > 0.0 and bool(all_folds_positive) and int(protected_target_count) >= 1,
    }
