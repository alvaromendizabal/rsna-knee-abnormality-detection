"""Small public analytical helpers for the Stage-32 training frontier."""
from __future__ import annotations

from math import isfinite
from typing import Optional


def coverage_fraction(cached: int, total: int) -> float:
    if total <= 0 or cached < 0 or cached > total:
        raise ValueError("invalid coverage counts")
    return cached / total


def leaderboard_gap(reference: float, leader: float) -> float:
    if not all(isfinite(x) and 0.0 <= x <= 1.0 for x in (reference, leader)):
        raise ValueError("scores must be finite probabilities")
    return leader - reference


def parity_ratio(observed: float, tolerance: float) -> float:
    if not isfinite(observed) or observed < 0 or not isfinite(tolerance) or tolerance <= 0:
        raise ValueError("invalid parity values")
    return observed / tolerance


def candidate_state(score: Optional[float], incumbent: float) -> str:
    if score is None:
        return "PENDING"
    if not isfinite(score) or not 0.0 <= score <= 1.0:
        raise ValueError("invalid candidate score")
    if not isfinite(incumbent) or not 0.0 <= incumbent <= 1.0:
        raise ValueError("invalid incumbent score")
    return "ABOVE_INCUMBENT" if score > incumbent else "AT_OR_BELOW_INCUMBENT"
