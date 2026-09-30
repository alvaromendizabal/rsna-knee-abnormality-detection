from __future__ import annotations

GIB = 1024 ** 3

def public_gap(reference: float, leader: float) -> float:
    return round(float(leader) - float(reference), 12)

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
