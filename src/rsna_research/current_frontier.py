"""Finite, scope-preserving comparisons for retained grouped MRI evidence."""
from __future__ import annotations
from math import isfinite

def aggregate_gain(candidate: float, baseline: float) -> float:
    if not all(isfinite(x) and 0.0 <= x <= 1.0 for x in (candidate, baseline)):
        raise ValueError("scores must be finite probabilities")
    return float(candidate) - float(baseline)

def retention_state(*, candidate: float, baseline: float, valid: bool = True) -> str:
    if not valid:
        return "INVALID"
    gain = aggregate_gain(candidate, baseline)
    if gain > 0.0:
        return "RETAIN_POSITIVE"
    if gain < 0.0:
        return "SCIENTIFIC_NEGATIVE"
    return "INCONCLUSIVE"

def paired_interval_state(*, lower: float, upper: float, delta: float) -> str:
    values = (float(lower), float(upper), float(delta))
    if not all(isfinite(v) for v in values):
        raise ValueError("interval values must be finite")
    if lower > upper:
        raise ValueError("lower cannot exceed upper")
    if delta > 0.0 and lower > 0.0:
        return "POSITIVE_SUPPORTED"
    if delta < 0.0 and upper < 0.0:
        return "NEGATIVE_SUPPORTED"
    return "INCONCLUSIVE"
