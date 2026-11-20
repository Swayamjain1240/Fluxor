"""Known-value tests for the Track 2 weak-label machinery.

If `auc` is wrong, the reported track-2 AUC is wrong. If `labelFromGaia` is
wrong, the labels themselves are wrong.
Run: python -m pytest evaluation/tests -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

from evaluation.track2.build_labels import labelFromGaia  # noqa: E402
from evaluation.track2.run_eval import (  # noqa: E402
    auc,
    permutationPValue,
    stratifiedBootstrapAuc,
)


# ---------------------------------------------------------------------------
# AUC wrapper
# ---------------------------------------------------------------------------

def test_auc_perfect_ranking_is_one():
    assert auc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == pytest.approx(1.0)


def test_auc_reversed_ranking_is_zero():
    assert auc([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1]) == pytest.approx(0.0)


def test_auc_ties_are_half_credit():
    assert auc([0, 1], [0.5, 0.5]) == pytest.approx(0.5)


def test_auc_is_undefined_with_one_class():
    """Object-level labels can be degenerate; callers must get None, not a crash."""

    assert auc([1, 1, 1], [0.1, 0.2, 0.3]) is None
    assert auc([0, 0], [0.1, 0.2]) is None


# ---------------------------------------------------------------------------
# Bootstrap
# ---------------------------------------------------------------------------

def test_stratified_bootstrap_keeps_every_class_in_every_replicate():
    """The point of stratifying: no replicate can lose the positive class."""

    labels = [1] * 5 + [0] * 35
    scores = [0.9, 0.8, 0.7, 0.6, 0.5] + [0.8 - 0.02 * i for i in range(35)]

    result = stratifiedBootstrapAuc(labels, scores, seed=0, iterations=200)

    assert result["iterations"] == 200
    assert result["skipped"] == 0
    assert result["stratified"] is True
    assert result["ci95"][0] <= result["median"] <= result["ci95"][1]


def test_stratified_bootstrap_is_deterministic_for_a_fixed_seed():
    labels = [0, 0, 1, 1, 0, 1, 0, 1]
    scores = [0.2, 0.7, 0.5, 0.9, 0.1, 0.4, 0.3, 0.8]

    first = stratifiedBootstrapAuc(labels, scores, seed=5, iterations=100)
    second = stratifiedBootstrapAuc(labels, scores, seed=5, iterations=100)

    assert first == second


def test_stratified_bootstrap_returns_nothing_without_both_classes():
    result = stratifiedBootstrapAuc([1, 1, 1, 1], [0.1, 0.2, 0.3, 0.4], 0, 50)

    assert result["iterations"] == 0
    assert result["skipped"] == 50


# ---------------------------------------------------------------------------
# Permutation test
# ---------------------------------------------------------------------------

def test_permutation_p_reflects_how_often_chance_separates_the_classes():
    """With 3 positives and 3 negatives, 1 label arrangement in 20 separates them.

    So a perfect ranking on six objects can only reach p ~ 0.05: the test is
    bounded by the number of distinct label arrangements, not by the AUC.
    """

    result = permutationPValue([0, 0, 0, 1, 1, 1], [0.1, 0.2, 0.3, 0.7, 0.8, 0.9], 0, 999)

    assert result["observed"] == pytest.approx(1.0)
    assert 0.03 <= result["pValue"] <= 0.07


def test_permutation_p_is_one_when_the_ranking_is_chance():
    """All scores tied: every shuffling of labels produces the same AUC."""

    result = permutationPValue([0, 1, 0, 1], [0.5, 0.5, 0.5, 0.5], 0, 200)

    assert result["observed"] == pytest.approx(0.5)
    assert result["pValue"] == pytest.approx(1.0)


def test_permutation_is_deterministic_and_handles_one_class():
    labels = [0, 0, 1, 1, 0, 1, 0, 1]
    scores = [0.2, 0.7, 0.5, 0.9, 0.1, 0.4, 0.3, 0.8]

    assert permutationPValue(labels, scores, 3, 200) == permutationPValue(
        labels, scores, 3, 200
    )

    degenerate = permutationPValue([1, 1, 1], [0.1, 0.2, 0.3], 0, 50)
    assert degenerate["pValue"] is None


# ---------------------------------------------------------------------------
# Label mapping
# ---------------------------------------------------------------------------

def test_missing_source_is_negative():
    assert labelFromGaia(None) == 0


def test_unclassified_source_is_negative():
    assert labelFromGaia({"inVariClassificationResult": 0, "gaiaClasses": []}) == 0


def test_classified_without_a_specific_class_is_positive():
    """Most classified Gaia sources carry no specific class; they still count."""

    assert labelFromGaia({"inVariClassificationResult": 1, "gaiaClasses": []}) == 1


def test_specific_class_is_positive():
    assert (
        labelFromGaia(
            {"inVariClassificationResult": 1, "gaiaClasses": ["eclipsing_binary"]}
        )
        == 1
    )
