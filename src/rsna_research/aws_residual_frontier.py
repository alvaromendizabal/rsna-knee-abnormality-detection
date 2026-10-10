from __future__ import annotations

GIB = 1024 ** 3


def detect_image_layout(shape: tuple[int, ...]) -> str:
    if len(shape) != 4:
        raise ValueError("expected a 4D image batch")
    if shape[1] == 3 and shape[-1] != 3:
        return "NCHW"
    if shape[-1] == 3 and shape[1] != 3:
        return "NHWC"
    raise ValueError("ambiguous or unsupported channel layout")

def canonical_nhwc_shape(shape: tuple[int, ...]) -> tuple[int, ...]:
    layout = detect_image_layout(shape)
    if layout == "NHWC":
        return shape
    n, c, h, w = shape
    return (n, h, w, c)

def uint8_payload_gib(total_windows: int, height: int, width: int, channels: int = 3) -> float:
    if min(total_windows, height, width, channels) <= 0:
        raise ValueError("dimensions must be positive")
    return total_windows * height * width * channels / GIB

def confirmation_gate(
    *,
    candidate_mean: float,
    mean_blend_delta: float,
    fold_deltas: dict[int, float] | dict[str, float],
    worst_target_delta: float,
    bootstrap_positive_fraction: float,
    median_spearman: float,
    candidate_min: float = 0.740,
    blend_delta_min: float = 0.00075,
    worst_target_min: float = -0.005,
    bootstrap_min: float = 0.80,
    spearman_max: float = 0.985,
) -> dict[str, object]:
    """Evaluate the public aggregate confirmation contract.

    The function intentionally accepts aggregate fold/target summaries only.
    It does not expose predictions, study identifiers, sampling schedules,
    model weights, or competition-specific inference logic.
    """
    values = tuple(float(v) for v in fold_deltas.values())
    if not values:
        raise ValueError("at least one fold delta is required")
    gates = {
        "candidate_mean_fold_macro": float(candidate_mean) >= candidate_min,
        "fixed_blend_delta": float(mean_blend_delta) >= blend_delta_min,
        "all_confirmation_folds_nonnegative": all(v >= 0.0 for v in values),
        "worst_target_regression": float(worst_target_delta) >= worst_target_min,
        "bootstrap_positive_fraction": float(bootstrap_positive_fraction) >= bootstrap_min,
        "diversity": float(median_spearman) <= spearman_max,
    }
    return {
        "gates": gates,
        "promoted": all(gates.values()),
    }
