"""Baseline RAG retrieval evaluation on the frozen corpus.

Baseline configuration is the production default: chunk_size=1000, chunk_overlap=200,
top_k=5. It is chosen a priori, not tuned, so scoring the test split here is a single
untuned pass.

Run:
    python evaluation/rag/run_rag_eval.py
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

BASELINE = {"chunkSize": 1000, "chunkOverlap": 200, "topK": 5}
K_VALUES = (3, 5, 10)


def run(out_dir: Path, report_path: Path) -> dict:
    started = time.time()

    manifest = load_corpus_manifest()
    pages = load_pages()
    queries = load_queries()

    index = build_index(BASELINE["chunkSize"], BASELINE["chunkOverlap"], pages)
    chunks, matrix = index["chunks"], index["vectors"]

    query_vectors = embed_queries([q["query"] for q in queries])

    per_query: list[dict] = []
    latencies: list[float] = []

    for position, query in enumerate(queries):
        t0 = time.perf_counter()
        ranked = search(query_vectors[position], matrix, max(BASELINE["topK"], max(K_VALUES)))
        latencies.append((time.perf_counter() - t0) * 1000.0)

        metrics = evaluateQuery(chunks, ranked, query["gold"], K_VALUES)
        per_query.append(
            {
                "qid": query["qid"],
                "split": query["split"],
                "topic": query["topic"],
                "query": query["query"],
                "goldCount": metrics["goldCount"],
                "mrr": metrics["mrr"],
                **{k: v for k, v in metrics.items() if k not in ("goldCount", "mrr", "rankedGrades")},
                "top5": [
                    {
                        "docId": chunks[i]["docId"],
                        "page": chunks[i]["page"],
                        "charStart": chunks[i]["charStart"],
                        "grade": metrics["rankedGrades"][rank]
                        if rank < len(metrics["rankedGrades"])
                        else 0,
                    }
                    for rank, i in enumerate(ranked[:5])
                ],
            }
        )

    by_split = {
        split: aggregate([q for q in per_query if q["split"] == split], K_VALUES)
        for split in ("val", "test")
    }

    topics = sorted({q["topic"] for q in per_query})
    by_topic = {
        topic: aggregate([q for q in per_query if q["topic"] == topic and q["split"] == "test"], K_VALUES)
        for topic in topics
    }

    results = {
        "corpus": {
            "corpusId": manifest["corpusId"],
            "documents": manifest["totals"]["documents"],
            "pages": manifest["totals"]["pages"],
            "chars": manifest["totals"]["chars"],
        },
        "config": {**BASELINE, "metricK": list(K_VALUES)},
        "index": {
            "chunks": len(chunks),
            "chunkIndexDigest": index_digest(chunks),
            "cached": index["cached"],
            "buildSeconds": index["buildSeconds"],
            "embeddingModel": "sentence-transformers/all-MiniLM-L6-v2 (384-d, normalised)",
            "ranking": "exact cosine over unit vectors (identical ordering to Chroma L2)",
        },
        "annotation": {
            "queries": len(queries),
            "val": sum(1 for q in queries if q["split"] == "val"),
            "test": sum(1 for q in queries if q["split"] == "test"),
            "annotator": "single annotator",
            "coverageRule": "chunk credited when it covers >= 50% of a gold span",
            "unjudgedPolicy": "passages outside the candidate pool treated as irrelevant",
        },
        "results": {"bySplit": by_split, "byTopicTest": by_topic, "perQuery": per_query},
        "latency": {"retrievalPerQuery": percentiles(latencies)},
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
        },
        "runtimeSeconds": round(time.time() - started, 2),
        "limitations": [
            "Ground truth is a single-annotator judgment set located with anchor-assisted search, "
            "so no inter-annotator agreement can be reported.",
            "Passages outside the judged candidate pool are treated as irrelevant; a retriever that "
            "surfaces a genuinely relevant unjudged passage is penalised.",
            "Ranking is exact cosine over production embeddings; Chroma's ANN index and persistence "
            "are not exercised, so this measures retrieval quality rather than index latency.",
            "The corpus is 12 documents; recall is bounded by a small gold set of at most five spans "
            "per query, so small metric differences are within annotation noise.",
            "Only retrieval quality is measured. No LLM answer quality, faithfulness or citation "
            "correctness is claimed.",
        ],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    result_path = out_dir / f"rag_baseline_{stamp}.json"
    result_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    write_markdown(report_path, results)

    print(json.dumps({
        "result": str(result_path),
        "report": str(report_path),
        "chunks": len(chunks),
        "val": by_split["val"],
        "test": by_split["test"],
        "latency": results["latency"]["retrievalPerQuery"],
    }, indent=2))

    return results


def write_markdown(path: Path, results: dict) -> None:
    config = results["config"]
    lines: list[str] = []

    lines.append("# Fluxor — RAG Retrieval Baseline\n")
    lines.append("Generated by `evaluation/rag/run_rag_eval.py`; every number is read from the "
                 "machine-readable result file.\n")
    lines.append("## Corpus and configuration\n")
    lines.append("| Item | Value |")
    lines.append("|---|---|")
    lines.append(f"| Corpus | `{results['corpus']['corpusId']}` |")
    lines.append(f"| Documents / pages / chars | {results['corpus']['documents']} / "
                 f"{results['corpus']['pages']} / {results['corpus']['chars']} |")
    lines.append(f"| Chunk size / overlap / top_k | {config['chunkSize']} / "
                 f"{config['chunkOverlap']} / {config['topK']} |")
    lines.append(f"| Chunks indexed | {results['index']['chunks']} |")
    lines.append(f"| Index digest | `{results['index']['chunkIndexDigest'][:16]}...` |")
    lines.append(f"| Embeddings | {results['index']['embeddingModel']} |")
    lines.append(f"| Queries (val / test) | {results['annotation']['val']} / "
                 f"{results['annotation']['test']} |")
    lines.append("")

    lines.append("## Retrieval metrics\n")
    lines.append("| Split | n | P@5 | R@5 | F1@5 | nDCG@5 | nDCG@10 | MRR | hit rate@5 |")
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for split in ("val", "test"):
        row = results["results"]["bySplit"][split]
        lines.append(
            f"| {split} | {row['n']} | {row['p@5']} | {row['r@5']} | {row['f1@5']} | "
            f"{row['ndcg@5']} | {row['ndcg@10']} | {row['mrr']} | {row['hitRate@5']} |"
        )
    lines.append("")
    lines.append("Per-topic breakdown on the test split:\n")
    lines.append("| Topic | n | P@5 | R@5 | nDCG@5 | MRR |")
    lines.append("|---|---|---|---|---|---|")
    for topic, row in results["results"]["byTopicTest"].items():
        lines.append(
            f"| {topic} | {row['n']} | {row['p@5']} | {row['r@5']} | {row['ndcg@5']} | {row['mrr']} |"
        )
    lines.append("")

    lines.append("## Latency\n")
    lat = results["latency"]["retrievalPerQuery"]
    lines.append(f"Retrieval per query: p50 {lat['p50Ms']} ms, p95 {lat['p95Ms']} ms, "
                 f"max {lat['maxMs']} ms over {lat['n']} queries.\n")
    lines.append("Index build: "
                 f"{results['index']['buildSeconds']} s (cached: {results['index']['cached']}).\n")

    lines.append("## Worst test queries\n")
    worst = sorted(
        [q for q in results["results"]["perQuery"] if q["split"] == "test"],
        key=lambda q: (q["ndcg@5"], q["mrr"]),
    )[:5]
    lines.append("| Query | nDCG@5 | R@5 | gold spans |")
    lines.append("|---|---|---|---|")
    for q in worst:
        lines.append(f"| {q['qid']}: {q['query']} | {q['ndcg@5']} | {q['r@5']} | {q['goldCount']} |")
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
        "--report", default=str(AI_ROOT / "evaluation" / "reports" / "rag_baseline.md")
    )
    args = parser.parse_args()

    run(out_dir=Path(args.out_dir), report_path=Path(args.report))


if __name__ == "__main__":
    main()
