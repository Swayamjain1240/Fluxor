"""Known-value regression tests for the ML evaluation metrics and injection logic.

Values are hand-computed. If an assertion here fails, a reported metric is wrong.
Run: python -m pytest evaluation/tests -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pytest

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

from evaluation.mlEvaluation import evaluateMl  # noqa: E402
from evaluation.data.build_ml_benchmark import (  # noqa: E402
    INJECTION_WIDTH,
    WINDOW_SIZE,
    inject,
    make_dip,
    make_flare,
    make_offset,
    make_sinusoid,
    robust_sigma,
)


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------


def test_confusion_counts_and_rates():
    # tp=2, fp=1, fn=0, tn=1
    result = evaluateMl([0, 0, 1, 1], [0, 1, 1, 1])

    assert result["truePositive"] == 2
    assert result["falsePositive"] == 1
    assert result["falseNegative"] == 0
    assert result["trueNegative"] == 1
    assert result["confusionMatrix"] == {"tn": 1, "fp": 1, "fn": 0, "tp": 2}

    assert result["precision"] == pytest.approx(2 / 3, abs=1e-4)
    assert result["recall"] == pytest.approx(1.0)
    assert result["f1Score"] == pytest.approx(0.8, abs=1e-4)
    assert result["falsePositiveRate"] == pytest.approx(0.5)
    assert result["falseNegativeRate"] == pytest.approx(0.0)


def test_false_negative_rate():
    # tp=1, fn=2 -> FNR = 2/3, recall = 1/3
    result = evaluateMl([0, 1, 1, 1], [0, 0, 0, 1])

    assert result["falseNegativeRate"] == pytest.approx(2 / 3, abs=1e-4)
    assert result["recall"] == pytest.approx(1 / 3, abs=1e-4)
    assert result["falsePositiveRate"] == pytest.approx(0.0)


def test_roc_auc_perfect_and_reversed():
    perfect = evaluateMl([0, 0, 1, 1], [0, 0, 1, 1], scores=[0.1, 0.2, 0.3, 0.4])
    assert perfect["rocAuc"] == pytest.approx(1.0)
    assert perfect["prAuc"] == pytest.approx(1.0)

    reversed_ = evaluateMl([0, 0, 1, 1], [0, 0, 1, 1], scores=[0.4, 0.3, 0.2, 0.1])
    assert reversed_["rocAuc"] == pytest.approx(0.0)


def test_roc_auc_with_identical_scores_is_chance():
    result = evaluateMl([0, 0, 1, 1], [0, 0, 1, 1], scores=[0.5, 0.5, 0.5, 0.5])
    assert result["rocAuc"] == pytest.approx(0.5)


def test_pr_auc_of_perfect_ranking_is_one():
    result = evaluateMl([0, 1, 0, 1], [0, 1, 0, 1], scores=[0.1, 0.9, 0.2, 0.8])
    assert result["prAuc"] == pytest.approx(1.0)


def test_single_class_is_rejected():
    with pytest.raises(ValueError):
        evaluateMl([1, 1, 1], [1, 1, 0])


def test_empty_is_rejected():
    with pytest.raises(ValueError):
        evaluateMl([], [])


def test_length_mismatch_is_rejected():
    with pytest.raises(ValueError):
        evaluateMl([0, 1], [0])


def test_score_length_mismatch_is_rejected():
    with pytest.raises(ValueError):
        evaluateMl([0, 1], [0, 1], scores=[0.1])


def test_auc_absent_when_scores_not_supplied():
    result = evaluateMl([0, 1], [0, 1])
    assert "rocAuc" not in result


# ---------------------------------------------------------------------------
# Injection shapes
# ---------------------------------------------------------------------------


def test_robust_sigma_of_constant_series_is_zero():
    assert robust_sigma(np.ones(50)) == pytest.approx(0.0)


def test_robust_sigma_scales_with_noise():
    rng = np.random.default_rng(0)
    clean = 1.0 + rng.normal(0, 0.01, 20000)
    assert 0.009 < robust_sigma(clean) < 0.011


def test_flare_peaks_at_amplitude_and_decays():
    signal = make_flare(INJECTION_WIDTH, 0.05, np.random.default_rng(1))
    assert len(signal) == INJECTION_WIDTH
    assert signal[0] == pytest.approx(0.0)
    # The recorded amplitude must be the true injected peak.
    assert signal[1] == pytest.approx(0.05, abs=1e-9)
    assert signal.max() == pytest.approx(0.05, abs=1e-9)
    assert signal[-1] < signal[1]
    assert np.all(np.diff(signal[1:]) <= 1e-15)
    assert np.all(signal >= 0)


def test_dip_is_negative_and_bounded():
    signal = make_dip(INJECTION_WIDTH, 0.03, np.random.default_rng(2))
    assert signal.min() < 0
    assert signal.min() >= -0.03 - 1e-12
    assert np.all(signal <= 0)


def test_sinusoid_is_tapered_to_zero_at_edges():
    signal = make_sinusoid(INJECTION_WIDTH, 0.02, np.random.default_rng(3))
    assert abs(signal[0]) < 1e-12
    assert abs(signal[-1]) < 1e-12
    assert np.abs(signal).max() <= 0.02 + 1e-12


def test_offset_is_rectangular():
    signal = make_offset(INJECTION_WIDTH, 0.04, np.random.default_rng(4))
    nonzero = np.abs(signal) > 0
    assert nonzero.any()
    assert np.allclose(signal[nonzero], signal[nonzero][0])


# ---------------------------------------------------------------------------
# Injection determinism and labelling geometry
# ---------------------------------------------------------------------------


def test_injection_is_deterministic_for_a_fixed_seed():
    flux = 1.0 + np.random.default_rng(9).normal(0, 0.002, WINDOW_SIZE * 3)

    a_flux, a_params = inject(flux, 100, "T1_flare", np.random.default_rng(123))
    b_flux, b_params = inject(flux, 100, "T1_flare", np.random.default_rng(123))

    assert np.array_equal(a_flux, b_flux)
    assert a_params == b_params


def test_injection_changes_only_the_centre_span():
    flux = 1.0 + np.random.default_rng(10).normal(0, 0.002, WINDOW_SIZE * 3)
    injected, params = inject(flux, 100, "T2_dip", np.random.default_rng(7))

    start, end = params["spanStartIndex"], params["spanEndIndex"]
    assert end - start == INJECTION_WIDTH
    # Span is centred in the window starting at 100.
    assert start == 100 + (WINDOW_SIZE - INJECTION_WIDTH) // 2

    assert np.array_equal(injected[:start], flux[:start])
    assert np.array_equal(injected[end:], flux[end:])
    assert not np.array_equal(injected[start:end], flux[start:end])


def test_amplitude_stays_within_documented_clip():
    flux = 1.0 + np.random.default_rng(11).normal(0, 0.002, WINDOW_SIZE * 3)
    for seed in range(25):
        _, params = inject(flux, 100, "T1_flare", np.random.default_rng(seed))
        assert 0.001 - 1e-12 <= params["amplitudeRel"] <= 0.10 + 1e-12


def test_injected_span_is_fully_covered_by_exactly_one_window():
    """The labelling rule relies on this: one window has full coverage, no more."""
    flux = 1.0 + np.random.default_rng(12).normal(0, 0.002, 1000)
    _, params = inject(flux, 200, "T1_flare", np.random.default_rng(5))
    span = set(range(params["spanStartIndex"], params["spanEndIndex"]))

    full = []
    partial = []
    for start in range(0, 1000 - WINDOW_SIZE + 1, 100):
        window = set(range(start, start + WINDOW_SIZE))
        overlap = len(span & window)
        if overlap == INJECTION_WIDTH:
            full.append(start)
        elif overlap > 0:
            partial.append((start, overlap))

    assert full == [200]
    assert all(overlap < INJECTION_WIDTH for _start, overlap in partial)


# ---------------------------------------------------------------------------
# Threshold calibration rules
# ---------------------------------------------------------------------------


def test_global_threshold_flags_only_scores_below_cut():
    from evaluation.ml.tune_iforest import apply_global_threshold

    decision = np.array([-0.4, -0.1, 0.0, 0.1, 0.4])
    assert apply_global_threshold(decision, 0.0).tolist() == [1, 1, 0, 0, 0]
    assert apply_global_threshold(decision, -0.2).tolist() == [1, 0, 0, 0, 0]


def test_per_curve_quantile_flags_exactly_ceil_qn_lowest_scores():
    from evaluation.ml.tune_iforest import apply_per_curve_quantile

    decision = np.array([0.3, -0.5, 0.1, -0.2, 0.0])
    flags = apply_per_curve_quantile(decision, 0.2)  # ceil(0.2*5) = 1
    assert flags.sum() == 1
    assert flags[1] == 1  # lowest decision score = most anomalous

    flags_two = apply_per_curve_quantile(decision, 0.4)  # ceil(0.4*5) = 2
    assert flags_two.sum() == 2
    assert set(np.flatnonzero(flags_two)) == {1, 3}


def test_per_curve_quantile_flag_count_is_monotone_in_q():
    from evaluation.ml.tune_iforest import apply_per_curve_quantile

    decision = np.linspace(-1.0, 1.0, 50)
    counts = [apply_per_curve_quantile(decision, q).sum() for q in (0.02, 0.1, 0.2, 0.3)]
    assert counts == sorted(counts)
    assert all(c >= 1 for c in counts)


def _fake_grouped():
    """Two train, two validation and two test objects with deterministic scores."""
    grouped = {}
    predictions = {}
    rng = np.random.default_rng(0)

    for i in range(6):
        obj = f"obj{i}"
        n = 20
        labels = [1 if j % 5 == 0 else 0 for j in range(n)]
        grouped[obj] = {
            "split": "train" if i < 2 else ("val" if i < 4 else "test"),
            "X": rng.normal(size=(n, 3)),
            "labels": labels,
            "evaluable": np.ones(n, dtype=bool),
            "injectionClass": ["T1_flare" if lab == 1 else None for lab in labels],
            "windows": [],
        }
        predictions[obj] = (np.zeros(n, dtype=int), np.linspace(-0.2, 0.2, n))

    return grouped, predictions


def test_calibrated_bootstrap_reports_the_calibrated_rule():
    """Regression: the bootstrap must apply the calibrated rule, not the fixed offset."""
    from evaluation.ml.tune_iforest import calibrated_bootstrap, metrics_for

    grouped, predictions = _fake_grouped()
    result = calibrated_bootstrap(
        grouped, predictions, "test", "quantile", 0.2, seed=0, iterations=50
    )
    expected = metrics_for(grouped, predictions, "quantile", 0.2)["test"]

    assert result["rule"] == "quantile"
    assert result["param"] == 0.2
    assert result["point"]["f1Score"] == expected["f1Score"]
    assert result["point"]["recall"] == expected["recall"]
    assert result["point"]["precision"] == expected["precision"]


def test_calibrated_rule_changes_predictions_versus_fixed_offset():
    """The calibrated rule must not reproduce the uncalibrated one."""
    from evaluation.ml.tune_iforest import collect_for

    grouped, predictions = _fake_grouped()
    objects = [o for o in sorted(grouped) if grouped[o]["split"] == "test"]

    fixed = collect_for(objects, grouped, predictions, "fixed_offset", 0.0)
    calibrated = collect_for(objects, grouped, predictions, "quantile", 0.2)

    assert fixed["yPred"] != calibrated["yPred"]
    # Fixed offset flags every negative decision score: 10 of 20 per object.
    assert sum(fixed["yPred"]) == 20
    # Quantile flags ceil(0.2 * 20) = 4 per object.
    assert sum(calibrated["yPred"]) == 8
