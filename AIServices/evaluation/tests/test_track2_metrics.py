"""Known-value tests for the Track 2 weak-label machinery.

If `rocAuc` is wrong, the reported track-2 AUC is wrong. If `labelFromGaia` is
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
from evaluation.track2.run_eval import rocAuc  # noqa: E402


# ---------------------------------------------------------------------------
# AUC
# ---------------------------------------------------------------------------

def test_auc_perfect_ranking_is_one():
    assert rocAuc([0, 0, 1, 1], [0.1, 0.2, 0.8, 0.9]) == pytest.approx(1.0)


def test_auc_reversed_ranking_is_zero():
    assert rocAuc([0, 0, 1, 1], [0.9, 0.8, 0.2, 0.1]) == pytest.approx(0.0)


def test_auc_single_positive_matches_rank_position():
    # Positive scored between the two negatives: one of two pairs is ordered.
    assert rocAuc([0, 0, 1], [0.1, 0.9, 0.5]) == pytest.approx(0.5)


def test_auc_ties_are_half_credit():
    assert rocAuc([0, 1], [0.5, 0.5]) == pytest.approx(0.5)


def test_auc_matches_sklearn():
    sklearn = pytest.importorskip("sklearn.metrics")
    import random

    rng = random.Random(7)
    for _ in range(20):
        labels = [rng.randint(0, 1) for _ in range(12)]
        scores = [round(rng.random(), 2) for _ in range(12)]
        if sum(labels) in (0, 12):
            continue
        assert rocAuc(labels, scores) == pytest.approx(
            sklearn.roc_auc_score(labels, scores), abs=1e-12
        )


def test_auc_undefined_with_one_class():
    assert rocAuc([1, 1, 1], [0.1, 0.2, 0.3]) is None
    assert rocAuc([0, 0], [0.1, 0.2]) is None


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
