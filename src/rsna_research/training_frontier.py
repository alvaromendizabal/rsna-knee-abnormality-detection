"""Small public analytical helpers for the current RSNA training frontier."""
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


def score_delta(candidate: float, baseline: float) -> float:
    if not all(isfinite(x) and 0.0 <= x <= 1.0 for x in (candidate, baseline)):
        raise ValueError("scores must be finite probabilities")
    return candidate - baseline


def candidate_state(score: Optional[float], incumbent: float) -> str:
    if score is None:
        return "UNSCORED"
    if not isfinite(score) or not 0.0 <= score <= 1.0:
        raise ValueError("invalid candidate score")
    if not isfinite(incumbent) or not 0.0 <= incumbent <= 1.0:
        raise ValueError("invalid incumbent score")
    return "ABOVE_INCUMBENT" if score > incumbent else "AT_OR_BELOW_INCUMBENT"
