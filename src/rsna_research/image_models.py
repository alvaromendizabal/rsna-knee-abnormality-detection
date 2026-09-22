"""Small, dependency-free audit primitives for the image-model research notebooks.

The private training and MRI-inference pipeline is not distributed here. These
functions expose the frozen pooling mechanism, exact AUC convention, fixed blend,
and promotion decision so that the analytical contract can be tested publicly.
"""
from __future__ import annotations
import math
from typing import Sequence


def probabilities(values: Sequence[float]) -> list[float]:
    result = [float(v) for v in values]
    if not result or any(not math.isfinite(v) or not 0 <= v <= 1 for v in result):
        raise ValueError('Expected nonempty, finite probabilities in [0, 1].')
    return result


def binary_auc(labels: Sequence[int], scores: Sequence[float]) -> float | None:
    """Pairwise ROC AUC; ties receive one half. One-class AUC is undefined."""
    p = probabilities(scores)
    if len(labels) != len(p) or any(v not in (0, 1) for v in labels):
        raise ValueError('Labels must be binary and aligned with predictions.')
    positives = [v for y, v in zip(labels, p) if y == 1]
    negatives = [v for y, v in zip(labels, p) if y == 0]
    if not positives or not negatives:
        return None
    return math.fsum((a > b) + 0.5 * (a == b) for a in positives for b in negatives) / (len(positives) * len(negatives))


def brier(labels: Sequence[int], scores: Sequence[float]) -> float:
    p = probabilities(scores)
    if len(labels) != len(p) or any(v not in (0, 1) for v in labels):
        raise ValueError('Labels must be binary and aligned with predictions.')
    return math.fsum((float(y) - v) ** 2 for y, v in zip(labels, p)) / len(p)


def fixed_blend(primary: Sequence[float], secondary: Sequence[float], weight: float = 0.1) -> list[float]:
    """A fixed secondary-model weight, never a weight learned on evaluation rows."""
    a, b = probabilities(primary), probabilities(secondary)
    if len(a) != len(b) or not math.isfinite(weight) or not 0 <= weight <= 1:
        raise ValueError('Aligned vectors and a finite weight in [0, 1] are required.')
    return [(1 - weight) * x + weight * y for x, y in zip(a, b)]


def attention_pool(features: Sequence[Sequence[float]], logits: Sequence[float]) -> list[float]:
    """Stable global pooling for one target after frozen feature normalization.

    Features from all encoding microbatches must be concatenated before this
    operation. Applying softmax independently to microbatches is not equivalent.
    """
    if not features or len(features) != len(logits) or not features[0]:
        raise ValueError('Expected aligned, nonempty windows and attention logits.')
    width = len(features[0])
    if any(len(row) != width for row in features):
        raise ValueError('Ragged feature matrix.')
    if any(not math.isfinite(float(x)) for row in features for x in row) or any(not math.isfinite(float(v)) for v in logits):
        raise ValueError('Nonfinite features or attention logits.')
    m = max(logits)
    weights = [math.exp(v - m) for v in logits]
    denominator = math.fsum(weights)
    return [math.fsum(w * row[j] for w, row in zip(weights, features)) / denominator for j in range(width)]


def promotion(auc_delta: float, brier_delta: float, targets: int, studies: int) -> str:
    """Frozen Stage-27 thresholds. A passed gate is not submission authorization."""
    if targets != 12 or studies < 6:
        return 'INCONCLUSIVE_SUPPORT'
    if not all(math.isfinite(v) for v in (auc_delta, brier_delta)):
        raise ValueError('Metric differences must be finite.')
    if auc_delta <= -0.002 or brier_delta > 0.01:
        return 'STOP_FIXED_BLEND_DIRECTION'
    if auc_delta >= 0.002:
        return 'CANDIDATE_FOR_BROADER_VALIDATION'
    return 'INCONCLUSIVE_EFFECT'
