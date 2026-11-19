"""Known-value tests for the RAG retrieval metrics.

If an assertion fails, a reported retrieval metric is wrong.
Run: python -m pytest evaluation/tests -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

from evaluation.rag.rag_metrics import (  # noqa: E402
    aggregate,
    chunkGrade,
    evaluateQuery,
    f1,
    goldOverlap,
    ndcgAtK,
    precisionAtK,
    recallAtK,
    reciprocalRank,
)


# ---------------------------------------------------------------------------
# Chunking-invariant mapping
# ---------------------------------------------------------------------------


def test_full_coverage_is_one():
    chunk = {"docId": "D01", "page": 3, "charStart": 100, "charEnd": 600}
    span = {"d": "D01", "p": 3, "s": 200, "e": 500, "g": 2}
    assert goldOverlap(chunk, span) == pytest.approx(1.0)


def test_partial_coverage_is_fraction_of_span():
    chunk = {"docId": "D01", "page": 3, "charStart": 100, "charEnd": 300}
    span = {"d": "D01", "p": 3, "s": 200, "e": 600, "g": 2}  # length 400
    assert goldOverlap(chunk, span) == pytest.approx(100 / 400)


def test_different_page_or_document_never_matches():
    span = {"d": "D01", "p": 3, "s": 200, "e": 600, "g": 2}
    assert goldOverlap({"docId": "D01", "page": 4, "charStart": 200, "charEnd": 600}, span) == 0.0
    assert goldOverlap({"docId": "D02", "page": 3, "charStart": 200, "charEnd": 600}, span) == 0.0


def test_coverage_threshold_boundary():
    span = {"d": "D01", "p": 1, "s": 0, "e": 100, "g": 2}
    # 50% coverage is credited (>= threshold), 49% is not.
    half = {"docId": "D01", "page": 1, "charStart": 0, "charEnd": 50}
    below = {"docId": "D01", "page": 1, "charStart": 0, "charEnd": 49}
    assert chunkGrade(half, [span])[0] == 2
    assert chunkGrade(below, [span])[0] == 0


def test_chunk_grade_takes_the_maximum():
    chunk = {"docId": "D01", "page": 1, "charStart": 0, "charEnd": 500}
    gold = [
        {"d": "D01", "p": 1, "s": 0, "e": 100, "g": 1},
        {"d": "D01", "p": 1, "s": 100, "e": 200, "g": 2},
    ]
    grade, index = chunkGrade(chunk, gold)
    assert grade == 2
    assert index == 1


# ---------------------------------------------------------------------------
# Rank metrics
# ---------------------------------------------------------------------------


def test_precision_at_k():
    assert precisionAtK([2, 0, 1, 0, 0], 5) == pytest.approx(2 / 5)
    assert precisionAtK([1, 1], 2) == pytest.approx(1.0)
    assert precisionAtK([], 3) == pytest.approx(0.0)


def test_recall_at_k_with_deduplicated_credit():
    assert recallAtK({0, 1}, 4) == pytest.approx(0.5)
    assert recallAtK(set(), 4) == pytest.approx(0.0)
    assert recallAtK(set(), 0) == pytest.approx(0.0)


def test_f1():
    assert f1(1.0, 1.0) == pytest.approx(1.0)
    assert f1(0.5, 0.5) == pytest.approx(0.5)
    assert f1(0.0, 0.0) == pytest.approx(0.0)


def test_reciprocal_rank():
    assert reciprocalRank([2, 0, 1]) == pytest.approx(1.0)
    assert reciprocalRank([0, 1, 0]) == pytest.approx(0.5)
    assert reciprocalRank([0, 0, 0]) == pytest.approx(0.0)


def test_ndcg_hand_computed():
    gold = [{"d": "D01", "p": 1, "s": 0, "e": 10, "g": 2}]

    # Perfect single-document retrieval.
    assert ndcgAtK([2], gold, 1) == pytest.approx(1.0)

    # Relevant but grade 1 instead of 2: DCG = 1, IDCG = 3.
    assert ndcgAtK([1], gold, 1) == pytest.approx(1 / 3, abs=1e-4)

    # Correct document at rank 2: DCG = 3 / log2(3), IDCG = 3.
    assert ndcgAtK([0, 2], gold, 2) == pytest.approx((3 / 1.5849625) / 3, abs=1e-4)


def test_ndcg_two_spans_in_ideal_order_is_one():
    gold = [
        {"d": "D01", "p": 1, "s": 0, "e": 10, "g": 2},
        {"d": "D01", "p": 2, "s": 0, "e": 10, "g": 1},
    ]
    assert ndcgAtK([2, 1], gold, 2) == pytest.approx(1.0, abs=1e-6)


def test_ndcg_zero_when_nothing_relevant():
    gold = [{"d": "D01", "p": 1, "s": 0, "e": 10, "g": 2}]
    assert ndcgAtK([0, 0], gold, 2) == pytest.approx(0.0)


# ---------------------------------------------------------------------------
# Per-query evaluation and duplicate suppression
# ---------------------------------------------------------------------------


def _chunk(doc, page, start, end):
    return {"docId": doc, "page": page, "charStart": start, "charEnd": end, "text": ""}


def test_duplicate_chunks_credit_a_span_once():
    gold = [{"d": "D01", "p": 1, "s": 0, "e": 100, "g": 2}]
    chunks = [
        _chunk("D01", 1, 0, 500),      # covers the span
        _chunk("D01", 1, 50, 550),     # covers the same span again
        _chunk("D02", 9, 0, 500),      # irrelevant
    ]

    result = evaluateQuery(chunks, [0, 1, 2], gold, (1, 2, 3))

    # Precision counts both retrieved relevant chunks...
    assert result["p@2"] == pytest.approx(1.0)
    # ...but recall cannot exceed one credited span out of one.
    assert result["r@1"] == pytest.approx(1.0)
    assert result["r@2"] == pytest.approx(1.0)
    # Duplicate at rank 2 contributes no extra gain.
    assert result["ndcg@2"] == pytest.approx(1.0)


def test_evaluate_query_reports_gold_count_and_mrr():
    gold = [
        {"d": "D01", "p": 1, "s": 0, "e": 100, "g": 2},
        {"d": "D02", "p": 2, "s": 0, "e": 100, "g": 1},
    ]
    chunks = [_chunk("D09", 5, 0, 400), _chunk("D02", 2, 0, 400)]

    result = evaluateQuery(chunks, [0, 1], gold, (1, 2))

    assert result["goldCount"] == 2
    assert result["mrr"] == pytest.approx(0.5)
    assert result["p@1"] == pytest.approx(0.0)
    assert result["r@2"] == pytest.approx(0.5)


def test_aggregate_averages_across_queries():
    per_query = [
        {"mrr": 1.0, "p@5": 0.2, "r@5": 1.0, "f1@5": 0.3333, "ndcg@5": 1.0},
        {"mrr": 0.0, "p@5": 0.0, "r@5": 0.0, "f1@5": 0.0, "ndcg@5": 0.0},
    ]
    result = aggregate(per_query, (5,))

    assert result["n"] == 2
    assert result["mrr"] == pytest.approx(0.5)
    assert result["p@5"] == pytest.approx(0.1)
    assert result["hitRate@5"] == pytest.approx(0.5)
