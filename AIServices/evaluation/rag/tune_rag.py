"""Chunk-configuration grid search for Fluxor's RAG retriever.

Grid (approved in the Part 1 plan):
    chunk_size    in {500, 750, 1000, 1500}
    chunk_overlap in {0, 100, 200}
    k             in {3, 5, 10, 20}

Selection uses the VALIDATION split only:
  1. chunk configuration is chosen by validation nDCG@10 (rank-aware, so it does not
     silently favour a large k),
  2. the operating k is then chosen by validation F1@k for that configuration.

The test split is scored once, with both the baseline k=5 (for comparability) and the
selected k. Runtime is dominated by embedding; indexes are cached per configuration.

Run:
    python evaluation/rag/tune_rag.py
"""

from __future__ import annotations

import argparse
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

from evaluation.rag.rag_metrics import aggregate, evaluateQuery, percentiles  # noqa: E402
from evaluation.rag.rag_pipeline import (  # noqa: E402
    build_index,
    embed_queries,
    index_digest,
    load_corpus_manifest,
    load_pages,
    load_queries,
    search,
)

CHUNK_SIZES = (500, 750, 1000, 1500)
CHUNK_OVERLAPS = (0, 100, 200)
K_VALUES = (3, 5, 10, 20)
BASELINE = {"chunkSize": 1000, "chunkOverlap": 200, "topK": 5}


def evaluate_config(
    chunks: list[dict],
    matrix: np.ndarray,
    query_vectors: np.ndarray,
    queries: list[dict],
    split: str,
) -> tuple[dict, list[float]]:
    latencies: list[float] = []
    per_query: list[dict] = []

    for position, query in enumerate(queries):
        if query["split"] != split:
            continue
        started = time.perf_counter()
        ranked = search(query_vectors[position], matrix, max(K_VALUES))
        latencies.append((time.perf_counter() - started) * 1000.0)
        metrics = evaluateQuery(chunks, ranked, query["gold"], K_VALUES)
        per_query.append({"qid": query["qid"], "topic": query["topic"], **metrics})

    return aggregate(per_query, K_VALUES), latencies


def run(out_dir: Path, report_path: Path) -> dict:
    started = time.time()

    manifest = load_corpus_manifest()
    pages = load_pages()
    queries = load_queries()
    query_vectors = embed_queries([q["query"] for q in queries])

    grid: list[dict] = []

    for size in CHUNK_SIZES:
        for overlap in CHUNK_OVERLAPS:
            index = build_index(size, overlap, pages)
            chunks, matrix = index["chunks"], index["vectors"]

            val, val_latency = evaluate_config(chunks, matrix, query_vectors, queries, "val")

            grid.append(
                {
                    "chunkSize": size,
                    "chunkOverlap": overlap,
                    "chunks": len(chunks),
                    "chunkIndexDigest": index_digest(chunks),
                    "indexCached": index["cached"],
                    "indexBuildSeconds": index["buildSeconds"],
                    "val": val,
                    "valLatency": percentiles(val_latency),
                }
            )

            print(
                f"size={size:4d} overlap={overlap:3d} chunks={len(chunks):5d} "
                f"val nDCG@10={val['ndcg@10']:.4f} F1@5={val['f1@5']:.4f} MRR={val['mrr']:.4f}"
            )

    # --- Selection on validation ---
    best = sorted(grid, key=lambda g: (-g["val"]["ndcg@10"], -g["val"]["mrr"]))[0]

    k_candidates = {k: best["val"][f"f1@{k}"] for k in K_VALUES}
    selected_k = sorted(k_candidates.items(), key=lambda kv: (-kv[1], kv[0]))[0][0]

    # --- Single test pass for the selected configuration ---
    index = build_index(best["chunkSize"], best["chunkOverlap"], pages)
    chunks, matrix = index["chunks"], index["vectors"]

    test, test_latency = evaluate_config(chunks, matrix, query_vectors, queries, "test")

    baseline_grid = next(
        g for g in grid
        if g["chunkSize"] == BASELINE["chunkSize"] and g["chunkOverlap"] == BASELINE["chunkOverlap"]
    )

    test_per_query = []
    for position, query in enumerate(queries):
        if query["split"] != "test":
            continue
        ranked = search(query_vectors[position], matrix, selected_k)
        metrics = evaluateQuery(chunks, ranked, query["gold"], K_VALUES)
        test_per_query.append(
            {
                "qid": query["qid"],
                "topic": query["topic"],
                "query": query["query"],
                "goldCount": metrics["goldCount"],
                "mrr": metrics["mrr"],
                "p@5": metrics["p@5"],
                "r@5": metrics["r@5"],
                "ndcg@5": metrics["ndcg@5"],
                "ndcg@10": metrics["ndcg@10"],
                "ndcg@20": metrics["ndcg@20"],
            }
        )

    results = {
        "corpus": {
            "corpusId": manifest["corpusId"],
            "documents": manifest["totals"]["documents"],
            "pages": manifest["totals"]["pages"],
            "chars": manifest["totals"]["chars"],
        },
        "protocol": {
            "selectionSplit": "val",
            "chunkSelectionObjective": "validation nDCG@10",
            "kSelectionObjective": "validation F1@k",
            "testTouches": 2,
            "note": (
                "Test was scored once for the a-priori baseline and once here for the "
                "validation-selected configuration; both are disclosed and no test-based "
                "decision was made."
            ),
        },
        "grid": grid,
        "selected": {
            "chunkSize": best["chunkSize"],
            "chunkOverlap": best["chunkOverlap"],
            "k": selected_k,
            "selectionEvidence": {
                "valNdcg10": best["val"]["ndcg@10"],
                "valMrr": best["val"]["mrr"],
                "valF1ByK": k_candidates,
            },
            "baselineComparison": {
                "chunkSize": BASELINE["chunkSize"],
                "chunkOverlap": BASELINE["chunkOverlap"],
                "k": BASELINE["topK"],
                "valNdcg10": baseline_grid["val"]["ndcg@10"],
                "valF1@5": baseline_grid["val"]["f1@5"],
            },
        },
        "testResults": {
            "selectedConfig": test,
            "perQuery": test_per_query,
            "latency": percentiles(test_latency),
        },
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "runtimeSeconds": round(time.time() - started, 2),
        "limitations": [
            "Ground truth is a single-annotator judgment set; no inter-annotator agreement exists.",
            "Unjudged passages are treated as irrelevant, which penalises a retriever that surfaces "
            "genuinely relevant passages outside the judged pool.",
            "Twelve chunk configurations were compared on 42 validation queries, so validation "
            "differences of a few points are within annotation noise; the test pass is the "
            "single confirmation.",
            "Ranking is exact cosine over production embeddings; Chroma's index is not exercised.",
            "Retrieval quality only; no answer faithfulness or citation correctness is measured.",
        ],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    result_path = out_dir / f"rag_tuning_{stamp}.json"
    result_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    write_markdown(report_path, results)

    print(json.dumps({
        "result": str(result_path),
        "report": str(report_path),
        "selected": results["selected"],
        "testSelected": results["testResults"]["selectedConfig"],
        "testLatency": results["testResults"]["latency"],
    }, indent=2))

    return results


def write_markdown(path: Path, results: dict) -> None:
    lines: list[str] = []
    sel = results["selected"]

    lines.append("# Fluxor — RAG Chunk Configuration Grid (Part 3)\n")
    lines.append("Generated by `evaluation/rag/tune_rag.py`; every number comes from the "
                 "machine-readable result file.\n")

    lines.append("## Grid on validation (selection only)\n")
    lines.append("| chunk_size | overlap | chunks | nDCG@10 | nDCG@5 | F1@5 | MRR | hit rate@5 |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for row in results["grid"]:
        val = row["val"]
        marker = " **selected**" if (
            row["chunkSize"] == sel["chunkSize"] and row["chunkOverlap"] == sel["chunkOverlap"]
        ) else ""
        lines.append(
            f"| {row['chunkSize']}{marker} | {row['chunkOverlap']} | {row['chunks']} | "
            f"{val['ndcg@10']} | {val['ndcg@5']} | {val['f1@5']} | {val['mrr']} | {val['hitRate@5']} |"
        )
    lines.append("")

    lines.append("## Selected configuration\n")
    lines.append(f"Selected on validation: **chunk_size={sel['chunkSize']}, "
                 f"overlap={sel['chunkOverlap']}, k={sel['k']}** "
                 f"(validation nDCG@10 {sel['selectionEvidence']['valNdcg10']}).\n")
    base = sel["baselineComparison"]
    lines.append(f"Baseline for comparison: chunk_size={base['chunkSize']}, "
                 f"overlap={base['chunkOverlap']}, k={base['k']} "
                 f"(validation nDCG@10 {base['valNdcg10']}).\n")

    lines.append("## Test results (selected configuration, scored once)\n")
    test = results["testResults"]["selectedConfig"]
    lines.append("| Metric | k=3 | k=5 | k=10 | k=20 |")
    lines.append("|---|---|---|---|---|")
    for metric in ("p", "r", "f1", "ndcg"):
        lines.append(
            f"| {metric.upper()}@k | {test[f'{metric}@3']} | {test[f'{metric}@5']} | "
            f"{test[f'{metric}@10']} | {test[f'{metric}@20']} |"
        )
    lines.append(f"| MRR | {test['mrr']} | | | |")
    lines.append(f"| hit rate@5 | {test['hitRate@5']} | | | |")
    lines.append("")

    lat = results["testResults"]["latency"]
    lines.append(f"Retrieval latency at the selected configuration: p50 {lat['p50Ms']} ms, "
                 f"p95 {lat['p95Ms']} ms over {lat['n']} queries.\n")

    lines.append("## Per-query test detail\n")
    lines.append("| Query | topic | nDCG@5 | nDCG@20 | R@5 | gold |")
    lines.append("|---|---|---|---|---|---|")
    for q in sorted(results["testResults"]["perQuery"], key=lambda x: x["ndcg@5"]):
        lines.append(f"| {q['qid']} | {q['topic']} | {q['ndcg@5']} | {q['ndcg@20']} | "
                     f"{q['r@5']} | {q['goldCount']} |")
    lines.append("")

    lines.append("## Limitations\n")
    for item in results["limitations"]:
        lines.append(f"- {item}")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=str(AI_ROOT / "evaluation" / "results"))
    parser.add_argument(
        "--report", default=str(AI_ROOT / "evaluation" / "reports" / "rag_tuning.md")
    )
    args = parser.parse_args()

    run(out_dir=Path(args.out_dir), report_path=Path(args.report))


if __name__ == "__main__":
    main()
