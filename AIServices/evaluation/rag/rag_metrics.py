"""Rank-aware retrieval metrics over chunking-invariant gold spans.

Gold spans are (docId, page, charStart, charEnd, grade) offsets into the extracted
page text. A retrieved chunk inherits the grade of the gold span it covers, so the
labels do not move when chunk size changes.

Coverage rule: a chunk is credited with a gold span when the chunk covers at least
COVERAGE_THRESHOLD of that span. Each gold span can be credited at most once per
query, which prevents a single relevant passage from inflating recall or nDCG when
several overlapping chunks retrieve it.
"""

from __future__ import annotations

import math

COVERAGE_THRESHOLD = 0.5


def goldOverlap(chunk: dict, span: dict) -> float:
    """Fraction of the gold span covered by the chunk."""
    if chunk["docId"] != span["d"] or int(chunk["page"]) != int(span["p"]):
        return 0.0

    start = max(int(chunk["charStart"]), int(span["s"]))
    end = min(int(chunk["charEnd"]), int(span["e"]))
    length = int(span["e"]) - int(span["s"])

    if length <= 0 or end <= start:
        return 0.0

    return (end - start) / length


def chunkGrade(chunk: dict, goldSpans: list[dict]) -> tuple[int, int]:
    """Best grade credited to a chunk, plus the index of the credited span."""
    best_grade = 0
    best_index = -1

    for index, span in enumerate(goldSpans):
        if goldOverlap(chunk, span) >= COVERAGE_THRESHOLD:
            if int(span["g"]) > best_grade:
                best_grade = int(span["g"])
                best_index = index

    return best_grade, best_index


def precisionAtK(grades: list[int], k: int) -> float:
    if k <= 0:
        return 0.0
    return sum(1 for g in grades[:k] if g >= 1) / k


def recallAtK(credited: set[int], totalGold: int) -> float:
    if totalGold == 0:
        return 0.0
    return len(credited) / totalGold


def f1(precision: float, recall: float) -> float:
    if precision + recall == 0:
        return 0.0
    return 2 * precision * recall / (precision + recall)


def dcg(gains: list[int]) -> float:
    total = 0.0
    for position, gain in enumerate(gains, start=1):
        total += (2**gain - 1) / math.log2(position + 1)
    return total


def ndcgAtK(chunkGradesInOrder: list[int], goldSpans: list[dict], k: int) -> float:
    """nDCG@k with distinct gold spans counted once, at their first retrieval."""
    # Gains arrive already deduplicated: a gold span is credited at most once.
    gains = [int(g) for g in chunkGradesInOrder[:k]]

    ideal = sorted((int(s["g"]) for s in goldSpans), reverse=True)[:k]
    ideal_dcg = dcg(ideal)

    if ideal_dcg == 0:
        return 0.0

    return dcg(gains) / ideal_dcg


def reciprocalRank(chunkGradesInOrder: list[int]) -> float:
    for position, grade in enumerate(chunkGradesInOrder, start=1):
        if grade >= 1:
            return 1.0 / position
    return 0.0


def evaluateQuery(
    chunks: list[dict],
    ranked_indices: list[int],
    goldSpans: list[dict],
    kValues: tuple[int, ...] = (3, 5, 10),
) -> dict:
    """Metrics for one query at each k, with duplicate credit suppressed."""
    ordered_chunks = [chunks[i] for i in ranked_indices]
    total_gold = sum(1 for s in goldSpans if int(s["g"]) >= 1)

    raw_grades: list[int] = []
    credited_by_rank: list[set[int]] = []

    for chunk in ordered_chunks:
        grade, index = chunkGrade(chunk, goldSpans)
        raw_grades.append(grade)
        credited_by_rank.append({index} if index >= 0 else set())

    result = {
        "goldCount": total_gold,
        "mrr": round(reciprocalRank(raw_grades), 4),
        "rankedGrades": raw_grades,
    }

    for k in kValues:
        window = raw_grades[:k]
        credited: set[int] = set()
        deduped_grades: list[int] = []

        for rank in range(min(k, len(ordered_chunks))):
            spans = credited_by_rank[rank]
            newly = spans - credited
            credited |= spans
            deduped_grades.append(raw_grades[rank] if newly else 0)

        precision = precisionAtK(window, k)
        recall = recallAtK(credited, total_gold)
        result[f"p@{k}"] = round(precision, 4)
        result[f"r@{k}"] = round(recall, 4)
        result[f"f1@{k}"] = round(f1(precision, recall), 4)
        result[f"ndcg@{k}"] = round(ndcgAtK(deduped_grades, goldSpans, k), 4)

    return result


def aggregate(perQuery: list[dict], kValues: tuple[int, ...] = (3, 5, 10)) -> dict:
    if not perQuery:
        return {"n": 0}

    out: dict = {"n": len(perQuery), "mrr": round(
        sum(q["mrr"] for q in perQuery) / len(perQuery), 4
    )}

    for k in kValues:
        for metric in ("p", "r", "f1", "ndcg"):
            key = f"{metric}@{k}"
            out[key] = round(sum(q[key] for q in perQuery) / len(perQuery), 4)

    out["hitRate@5"] = round(
        sum(1 for q in perQuery if q.get("r@5", 0) > 0) / len(perQuery), 4
    )
    return out


def percentiles(values: list[float]) -> dict:
    if not values:
        return {}
    import numpy as np

    array = np.asarray(values, dtype=float)
    return {
        "n": int(array.size),
        "p50Ms": round(float(np.percentile(array, 50)), 3),
        "p95Ms": round(float(np.percentile(array, 95)), 3),
        "maxMs": round(float(array.max()), 3),
        "meanMs": round(float(array.mean()), 3),
    }
