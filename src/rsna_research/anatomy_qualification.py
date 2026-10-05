"""Public-safe qualification helpers for anatomy-localization research.

This module encodes aggregate engineering gates only. It intentionally contains no
private checkpoint identities, raw images, row-level predictions, cloud paths,
or competition-specific fusion logic.
"""
from __future__ import annotations

from math import isfinite
from statistics import fmean
from typing import Mapping, Sequence

FOREGROUND_LABEL_COUNT = 9
REFERENCE_MEAN_DICE_MIN = 0.85
REFERENCE_PER_STRUCTURE_DICE_MIN = 0.50


def reference_quality_gate(
    dice_by_label: Mapping[str, float],
    *,
    required_labels: int = FOREGROUND_LABEL_COUNT,
    mean_threshold: float = REFERENCE_MEAN_DICE_MIN,
    per_structure_threshold: float = REFERENCE_PER_STRUCTURE_DICE_MIN,
) -> dict[str, float | int | bool]:
    """Evaluate a frozen aggregate reference-segmentation quality gate."""
    if int(required_labels) <= 0:
        raise ValueError("required_labels must be positive")
    if len(dice_by_label) != int(required_labels):
        raise ValueError("reference gate requires the complete foreground label set")

    values = [float(v) for v in dice_by_label.values()]
    if not all(isfinite(v) and 0.0 <= v <= 1.0 for v in values):
        raise ValueError("Dice values must be finite and within [0, 1]")
    if not 0.0 <= float(mean_threshold) <= 1.0:
        raise ValueError("mean_threshold must be within [0, 1]")
    if not 0.0 <= float(per_structure_threshold) <= 1.0:
        raise ValueError("per_structure_threshold must be within [0, 1]")

    mean_dice = float(fmean(values))
    min_dice = float(min(values))
    passed = (
        mean_dice >= float(mean_threshold)
        and min_dice >= float(per_structure_threshold)
    )
    return {
        "label_count": len(values),
        "mean_dice": mean_dice,
        "min_dice": min_dice,
        "mean_threshold": float(mean_threshold),
        "per_structure_threshold": float(per_structure_threshold),
        "passed": passed,
    }


def exact_fallback_unchanged(
    parent: Sequence[float],
    fallback: Sequence[float],
) -> bool:
    """Return True only when a disabled/missing anatomy route preserves outputs exactly."""
    p = tuple(float(v) for v in parent)
    f = tuple(float(v) for v in fallback)
    if len(p) != len(f) or not p:
        return False
    if not all(isfinite(v) for v in p + f):
        raise ValueError("predictions must be finite")
    return p == f


def qualification_state(
    *,
    tracks_completed: int,
    tracks_total: int,
    real_inference_completed: bool,
    reference_gate_passed: bool | None = None,
) -> str:
    """Return the public lifecycle state for the anatomy dependency."""
    completed = int(tracks_completed)
    total = int(tracks_total)
    if total <= 0 or completed < 0 or completed > total:
        raise ValueError("invalid qualification progress")

    if completed != total:
        return "QUALIFICATION_INCOMPLETE"
    if not real_inference_completed:
        if reference_gate_passed is not None:
            raise ValueError("reference result cannot exist before real inference")
        return "QUALIFIED_FOR_REFERENCE_PILOT"
    if reference_gate_passed is None:
        raise ValueError("completed reference inference requires a gate result")
    return "REFERENCE_GATE_PASSED" if reference_gate_passed else "REFERENCE_GATE_REJECTED"
