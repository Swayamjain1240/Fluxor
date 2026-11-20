"""L5 intra-rater stability check for the RAG relevance judgments.

The corpus judgments were made by a single annotator (AUDIT.md L5), so no
inter-annotator agreement can be reported. Instead, 20% of the usable queries
are re-judged blind -- original grades stripped, candidate order shuffled -- and
the second pass is compared with the first.

This measures *stability of the judging policy*, not correctness: the same
system judges twice, so high agreement is evidence that the rubric can be
re-applied consistently, not that the grades are right.

Workflow:
    python evaluation/rag/intra_rater.py sheet     # blind sheet + empty templates
    # fill evaluation/data/intra_rater/grades.json by hand
    python evaluation/rag/intra_rater.py score     # writes the agreement report

Grades use the frozen schema: 2 = directly answers the query, 1 = supporting
information, 0 = judged irrelevant.
"""

from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

DATA_DIR = AI_ROOT / "evaluation" / "data"
OUT_DIR = DATA_DIR / "intra_rater"
QUERIES = DATA_DIR / "rag_queries.jsonl"
CANDIDATES = DATA_DIR / "rag_candidates.jsonl"
REPORT = AI_ROOT / "evaluation" / "reports" / "rag_intra_rater.md"

SAMPLE_SEED = 20261120
FRACTION = 0.20
GRADES = (0, 1, 2)


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------

def loadQueries() -> list[dict]:
    records = []
    for line in QUERIES.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if "qid" in record:
            records.append(record)
    return records


def loadCandidates() -> dict[str, list[dict]]:
    pooled: dict[str, list[dict]] = {}
    for line in CANDIDATES.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        pooled.setdefault(record["queryId"], []).append(record)
    return pooled


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def allocate(splitSizes: dict[str, int], fraction: float) -> dict[str, int]:
    """Largest-remainder allocation of the sample across splits."""

    total = round(fraction * sum(splitSizes.values()))
    ideal = {split: fraction * size for split, size in splitSizes.items()}
    counts = {split: int(value) for split, value in ideal.items()}

    remainder = total - sum(counts.values())
    order = sorted(
        splitSizes,
        key=lambda split: (ideal[split] - counts[split], split),
        reverse=True,
    )

    for split in order[:remainder]:
        counts[split] += 1

    return counts


def sampleQueries(queries: list[dict], seed: int, fraction: float) -> list[dict]:
    splitSizes = Counter(record["split"] for record in queries)
    counts = allocate(dict(splitSizes), fraction)

    rng = random.Random(seed)
    chosen: list[dict] = []

    for split in sorted(counts):
        pool = sorted(
            (record for record in queries if record["split"] == split),
            key=lambda record: record["qid"],
        )
        chosen.extend(rng.sample(pool, counts[split]))

    return sorted(chosen, key=lambda record: record["qid"])


# ---------------------------------------------------------------------------
# Blind sheet
# ---------------------------------------------------------------------------

def originalGrade(candidate: dict, gold: list[dict]) -> int:
    """The grade recorded in the first pass, 0 if the passage was judged irrelevant."""

    for span in gold:
        if (
            span["d"] == candidate["docId"]
            and span["p"] == candidate["page"]
            and span["s"] == candidate["charStart"]
            and span["e"] == candidate["charEnd"]
        ):
            return int(span["g"])
    return 0


def buildSheet(seed: int = SAMPLE_SEED, fraction: float = FRACTION) -> dict:
    queries = loadQueries()
    pooled = loadCandidates()
    sampled = sampleQueries(queries, seed, fraction)

    rng = random.Random(seed + 1)

    sheetLines: list[str] = []
    template: dict[str, dict] = {}

    for record in sampled:
        candidates = list(pooled.get(record["qid"], []))
        rng.shuffle(candidates)

        sheetLines.append(f"\n## {record['qid']}  query: {record['query']}\n")
        template[record["qid"]] = {
            "query": record["query"],
            "split": record["split"],
            "topic": record["topic"],
            "passages": {},
        }

        for index, candidate in enumerate(candidates, start=1):
            passageId = f"{record['qid']}-{index:02d}"
            text = " ".join(candidate["text"].split())

            sheetLines.append(
                f"\n### {passageId}  [{candidate['docId']} p{candidate['page']} "
                f"{candidate['charStart']}-{candidate['charEnd']}]\n{text}\n"
            )

            template[record["qid"]]["passages"][passageId] = {
                "docId": candidate["docId"],
                "page": candidate["page"],
                "charStart": candidate["charStart"],
                "charEnd": candidate["charEnd"],
                "firstPassGrade": originalGrade(candidate, record["gold"]),
                "secondPassGrade": None,
            }

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    (OUT_DIR / "sheet.md").write_text(
        "# Blind re-judgment sheet (L5)\n\n"
        "Grade every passage: 2 = directly answers the query, 1 = supporting "
        "information, 0 = irrelevant to the query.\n" + "".join(sheetLines),
        encoding="utf-8",
    )

    (OUT_DIR / "grades.json").write_text(
        json.dumps(template, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    (OUT_DIR / "sample.json").write_text(
        json.dumps(
            {
                "seed": seed,
                "fraction": fraction,
                "sampledQids": [record["qid"] for record in sampled],
                "population": dict(Counter(r["split"] for r in queries)),
                "sampled": dict(Counter(r["split"] for r in sampled)),
                "passages": {
                    qid: len(entry["passages"]) for qid, entry in template.items()
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return {
        "queries": len(sampled),
        "passages": sum(len(v["passages"]) for v in template.values()),
        "path": str(OUT_DIR),
    }


# ---------------------------------------------------------------------------
# Agreement
# ---------------------------------------------------------------------------

def cohenKappa(first: list[int], second: list[int], labels: tuple[int, ...]) -> float:

    total = len(first)
    if total == 0:
        return 0.0

    observed = sum(1 for a, b in zip(first, second) if a == b) / total
    histFirst = Counter(first)
    histSecond = Counter(second)
    expected = sum(
        histFirst[label] * histSecond[label] for label in labels
    ) / (total * total)

    if expected >= 1.0:
        return 1.0

    return (observed - expected) / (1.0 - expected)


def quadraticWeightedKappa(
    first: list[int], second: list[int], labels: tuple[int, ...]
) -> float:

    index = {label: i for i, label in enumerate(labels)}
    k = len(labels)
    total = len(first)

    if total == 0:
        return 0.0

    observed = [[0] * k for _ in range(k)]
    for a, b in zip(first, second):
        observed[index[a]][index[b]] += 1

    histFirst = [0] * k
    histSecond = [0] * k
    for a in first:
        histFirst[index[a]] += 1
    for b in second:
        histSecond[index[b]] += 1

    numerator = 0.0
    denominator = 0.0

    for i in range(k):
        for j in range(k):
            weight = ((i - j) ** 2) / ((k - 1) ** 2)
            numerator += weight * observed[i][j]
            denominator += weight * histFirst[i] * histSecond[j] / total

    if denominator == 0:
        return 1.0

    return 1.0 - numerator / denominator


def score(gradesPath: Path = OUT_DIR / "grades.json") -> dict:

    payload = json.loads(gradesPath.read_text(encoding="utf-8"))

    first: list[int] = []
    second: list[int] = []
    missing: list[str] = []
    rows: list[dict] = []

    for qid, entry in payload.items():
        for passageId, passage in entry["passages"].items():
            graded = passage.get("secondPassGrade")
            if graded is None:
                missing.append(passageId)
                continue
            if int(graded) not in GRADES:
                raise ValueError(f"{passageId}: grade {graded} is not in {GRADES}")
            first.append(int(passage["firstPassGrade"]))
            second.append(int(graded))
            rows.append(
                {
                    "passageId": passageId,
                    "qid": qid,
                    "split": entry["split"],
                    "firstPass": int(passage["firstPassGrade"]),
                    "secondPass": int(graded),
                }
            )

    if not rows:
        raise SystemExit("no second-pass grades found; fill grades.json first")

    total = len(rows)
    exact = sum(1 for row in rows if row["firstPass"] == row["secondPass"]) / total
    withinOne = sum(
        1 for row in rows if abs(row["firstPass"] - row["secondPass"]) <= 1
    ) / total

    confusion = Counter((row["firstPass"], row["secondPass"]) for row in rows)

    binaryFirst = [1 if row["firstPass"] >= 1 else 0 for row in rows]
    binarySecond = [1 if row["secondPass"] >= 1 else 0 for row in rows]

    result = {
        "passages": total,
        "queries": len({row["qid"] for row in rows}),
        "unjudgedPassages": missing,
        "exactAgreement": round(exact, 4),
        "agreementWithinOneGrade": round(withinOne, 4),
        "cohenKappaBinaryRelevant": round(
            cohenKappa(binaryFirst, binarySecond, (0, 1)), 4
        ),
        "quadraticWeightedKappa": round(
            quadraticWeightedKappa(first, second, GRADES), 4
        ),
        "confusionFirstVsSecond": {
            f"{a}->{b}": count for (a, b), count in sorted(confusion.items())
        },
        "gradeDistributionFirst": dict(sorted(Counter(first).items())),
        "gradeDistributionSecond": dict(sorted(Counter(second).items())),
        "changes": [row for row in rows if row["firstPass"] != row["secondPass"]],
    }

    bySplit: dict[str, dict] = {}
    for split in sorted({row["split"] for row in rows}):
        subset = [row for row in rows if row["split"] == split]
        bySplit[split] = {
            "passages": len(subset),
            "exactAgreement": round(
                sum(1 for r in subset if r["firstPass"] == r["secondPass"])
                / len(subset),
                4,
            ),
        }
    result["bySplit"] = bySplit

    OUT_DIR.joinpath("agreement.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )

    return result


def main() -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["sheet", "score"])
    parser.add_argument("--grades", default=str(OUT_DIR / "grades.json"))
    args = parser.parse_args()

    if args.command == "sheet":
        print(buildSheet())
        return

    result = score(Path(args.grades))
    print(json.dumps({k: v for k, v in result.items() if k != "changes"}, indent=2))


if __name__ == "__main__":
    main()
