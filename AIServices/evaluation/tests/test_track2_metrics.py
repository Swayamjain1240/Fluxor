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

from evaluation.track2.build_enriched_targets import (  # noqa: E402
    magnitudeBands,
    matchNegatives,
)
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


# ---------------------------------------------------------------------------
# Enriched sampling: band pagination and magnitude matching
# ---------------------------------------------------------------------------

def test_magnitude_bands_are_contiguous_and_cover_the_range():
    """Bands replace cursor paging, so they must tile the range exactly."""

    bands = magnitudeBands(4)

    assert len(bands) == 4
    assert bands[0][0] == 8.0
    assert bands[-1][1] == 13.0
    for (_, high), (nextLow, _) in zip(bands, bands[1:]):
        assert high == pytest.approx(nextLow)
    assert sum(high - low for low, high in bands) == pytest.approx(5.0)


def test_matching_gives_each_positive_one_control_within_tolerance():
    positives = [
        {"sourceId": "p1", "gMag": 9.0, "classes": ["eclipsing_binary"], "label": 1},
        {"sourceId": "p2", "gMag": 10.0, "classes": ["rrlyrae"], "label": 1},
    ]
    controls = [
        {"sourceId": "c1", "gMag": 9.1, "classes": [], "label": 0},
        {"sourceId": "c2", "gMag": 10.05, "classes": [], "label": 0},
    ]

    matched = matchNegatives(positives, controls)

    assert len(matched) == 2
    assert [row["sourceId"] for row in matched] == ["c1", "c2"]
    assert all(row["label"] == 0 for row in matched)
    # A control is used once, so positives and controls stay disjoint.
    assert not {row["sourceId"] for row in matched} & {p["sourceId"] for p in positives}


def test_matching_skips_controls_outside_the_magnitude_tolerance():
    positives = [{"sourceId": "p1", "gMag": 9.0, "classes": ["x"], "label": 1}]
    controls = [{"sourceId": "c1", "gMag": 11.0, "classes": [], "label": 0}]

    assert matchNegatives(positives, controls) == []
