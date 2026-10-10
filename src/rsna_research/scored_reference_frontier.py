from __future__ import annotations
from statistics import median


def head_call_reduction(original_calls: int, candidate_calls: int) -> float:
    if original_calls <= 0 or candidate_calls < 0 or candidate_calls > original_calls:
        raise ValueError("invalid head-call counts")
    return (original_calls - candidate_calls) / original_calls

def median_speed_ratio(baseline_seconds, candidate_seconds) -> float:
    if len(baseline_seconds) != len(candidate_seconds) or not baseline_seconds:
        raise ValueError("timing vectors must be non-empty and aligned")
    if any(x <= 0 for x in baseline_seconds) or any(x <= 0 for x in candidate_seconds):
        raise ValueError("timings must be positive")
    return median(baseline_seconds) / median(candidate_seconds)
