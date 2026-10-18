import math

import numpy as np
import pytest

from rsna_review.diagnostics import probability_diagnostics, training_prevalence


def test_prevalence_excludes_heldout_labels():
    labels = np.array([[0], [0], [1], [1]])
    folds = np.array([0, 0, 1, 1])
    baseline = training_prevalence(labels, folds)
    np.testing.assert_array_equal(baseline, [[1], [1], [0], [0]])
    changed = labels.copy()
    changed[:2] = 1
    np.testing.assert_array_equal(training_prevalence(changed, folds)[:2], baseline[:2])
    with pytest.raises(ValueError, match="at least two folds"):
        training_prevalence(labels, np.zeros(4, dtype=int))


def test_hand_computed_losses_reliability_endpoints_and_scanner_weighting():
    y = np.array([[0], [1], [1], [0]])
    p = np.array([[0.], [1.], [.5], [.5]])
    result = probability_diagnostics(y, p, np.full_like(p, .5), ["a", "a", "a", "b"], ["target"], bins=2)
    assert result["macro"]["brier"] == .125
    assert result["macro"]["baseline_brier"] == .25
    assert result["macro"]["brier_skill"] == .5
    assert result["macro"]["log_loss"] == pytest.approx(math.log(2) / 2, abs=1e-14)
    assert result["per_target"]["target"]["reliability"] == [
        {"lower": 0., "upper": .5, "count": 1, "mean_probability": 0., "observed_fraction": 0.},
        {"lower": .5, "upper": 1., "count": 3, "mean_probability": 2 / 3, "observed_fraction": 2 / 3}]
    assert sum(row["brier"] * row["rows"] for row in result["by_scanner"]) / 4 == .125


def test_zero_reference_and_empty_bins_are_explicit_not_nan():
    y = np.zeros((2, 1))
    result = probability_diagnostics(y, y, y, ["scanner", "scanner"], ["target"])
    assert result["macro"]["brier_skill"] is None
    empty = result["per_target"]["target"]["reliability"][1]
    assert empty["count"] == 0 and empty["mean_probability"] is None and empty["observed_fraction"] is None


@pytest.mark.parametrize("dtype", [np.uint8, np.uint64, np.int8, np.int64])
def test_integer_probability_losses_match_float_arithmetic(dtype):
    labels = np.array([[1], [0]], dtype=dtype)
    probabilities = np.array([[0], [1]], dtype=dtype)
    baseline = np.zeros((2, 1), dtype=dtype)
    result = probability_diagnostics(labels, probabilities, baseline, ["a", "b"], ["target"])
    reference = probability_diagnostics(labels.astype(float), probabilities.astype(float),
                                        baseline.astype(float), ["a", "b"], ["target"])
    assert result == reference
    assert result["macro"]["brier"] == 1.0
    assert result["by_scanner"][0]["brier"] == 1.0  # unsigned p=0, y=1
    assert result["macro"]["baseline_brier"] == .5
    assert result["macro"]["brier_skill"] == -1.0


@pytest.mark.parametrize("bad", [np.nan, np.inf, -.1, 1.1])
def test_invalid_probabilities_are_rejected(bad):
    with pytest.raises(ValueError, match="probabilities"):
        probability_diagnostics([[0]], [[bad]], [[.5]], ["scanner"], ["target"])
