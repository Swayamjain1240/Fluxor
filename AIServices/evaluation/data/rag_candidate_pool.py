"""Generate candidate passages for RAG relevance annotation.

For each authored query, locate passages that mention its anchor terms and emit
them with exact character offsets into the extracted page text. Those offsets are
the unit of relevance judgement, so judgements survive any chunk-size change.

This tool only *locates* candidates. Whether a candidate is relevant, and how
relevant, is a separate judging decision recorded in rag_queries.jsonl.

Ranking policy (to avoid a gold set built from table-of-contents fragments):
  - table-of-contents pages are dropped (they contain many dot-leader runs),
  - spans that are mostly dot leaders are dropped,
  - candidates are diversified: at most one per page and two per document,
  - figure/table captions are kept but ranked below body text.

Run:
    python evaluation/data/rag_candidate_pool.py
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

DATA_DIR = AI_ROOT / "evaluation" / "data"
CORPUS_TEXT = DATA_DIR / "corpus" / "text"

SPAN_BEFORE = 60
SPAN_AFTER = 380
MAX_PER_QUERY = 5
MAX_PER_DOC = 2

DOT_LEADER = re.compile(r"(?:\.\s*){4,}")
CAPTION_START = re.compile(r"^\s*(?:Figure|Fig\.|Table)\s", re.IGNORECASE)


def is_toc_page(text: str) -> bool:
    return len(DOT_LEADER.findall(text)) >= 5


def is_dot_leader_span(text: str) -> bool:
    if not text:
        return True
    return text.count(".") / len(text) > 0.08


def spans_for_page(text: str, anchors: list[str]) -> list[dict]:
    """Merge anchor hits on one page into non-overlapping spans."""
    hits: list[tuple[int, str]] = []
    lowered = text.lower()

    for anchor in anchors:
        start = 0
        while True:
            index = lowered.find(anchor.lower(), start)
            if index < 0:
                break
            hits.append((index, anchor))
            start = index + len(anchor)

    if not hits:
        return []

    hits.sort()
    merged: list[dict] = []

    for index, anchor in hits:
        lo = max(0, index - SPAN_BEFORE)
        hi = min(len(text), index + SPAN_AFTER)
        if merged and lo <= merged[-1]["charEnd"]:
            span = merged[-1]
            span["charEnd"] = max(span["charEnd"], hi)
            span["anchors"].append(anchor)
        else:
            merged.append({"charStart": lo, "charEnd": hi, "anchors": [anchor]})

    out = []
    for span in merged:
        lo, hi = span["charStart"], span["charEnd"]
        raw = text[lo:hi]
        if is_dot_leader_span(raw):
            continue
        out.append(
            {
                "charStart": lo,
                "charEnd": hi,
                "anchors": span["anchors"],
                "text": " ".join(raw.split()),
            }
        )
    return out


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seeds", default=str(DATA_DIR / "rag_query_seeds.json"))
    parser.add_argument("--out", default=str(DATA_DIR / "rag_candidates.jsonl"))
    parser.add_argument("--max-per-query", type=int, default=MAX_PER_QUERY)
    args = parser.parse_args()

    seeds = json.loads(Path(args.seeds).read_text(encoding="utf-8"))["queries"]
    pages = load_pages()
    print(f"loaded {sum(len(v) for v in pages.values())} pages from {len(pages)} documents")

    out_path = Path(args.out)
    counts: dict[str, int] = {}
    toc_pages_skipped = 0

    with out_path.open("w", encoding="utf-8", newline="\n") as handle:
        for query in seeds:
            raw_candidates = []

            for doc_id in sorted(pages):
                for record in pages[doc_id]:
                    text = record["text"]
                    if is_toc_page(text):
                        toc_pages_skipped += 1
                        continue
                    for span in spans_for_page(text, query["anchors"]):
                        distinct = sorted(set(span["anchors"]))
                        raw_candidates.append(
                            {
                                "docId": doc_id,
                                "page": record["page"],
                                "charStart": span["charStart"],
                                "charEnd": span["charEnd"],
                                "anchorsHit": distinct,
                                "anchorCount": len(distinct),
                                "isCaption": bool(CAPTION_START.match(span["text"])),
                                "text": span["text"],
                            }
                        )

            raw_candidates.sort(
                key=lambda c: (
                    -c["anchorCount"],
                    c["isCaption"],
                    c["docId"],
                    c["page"],
                    c["charStart"],
                )
            )

            kept: list[dict] = []
            per_doc: dict[str, int] = {}
            seen_pages: set[tuple[str, int]] = set()

            for candidate in raw_candidates:
                if len(kept) >= args.max_per_query:
                    break
                page_key = (candidate["docId"], candidate["page"])
                if page_key in seen_pages:
                    continue
                if per_doc.get(candidate["docId"], 0) >= MAX_PER_DOC:
                    continue
                seen_pages.add(page_key)
                per_doc[candidate["docId"]] = per_doc.get(candidate["docId"], 0) + 1
                kept.append(candidate)

            counts[query["queryId"]] = len(kept)

            for rank, candidate in enumerate(kept, start=1):
                handle.write(
                    json.dumps(
                        {
                            "queryId": query["queryId"],
                            "rank": rank,
                            "query": query["query"],
                            "topic": query["topic"],
                            **candidate,
                        },
                        ensure_ascii=False,
                    )
                    + "\n"
                )

            print(
                f"{query['queryId']}: {len(raw_candidates)} candidates after filtering, "
                f"kept {len(kept)}"
            )

    missing = [q for q, n in counts.items() if n == 0]
    print(f"\ntoc pages skipped per query pass: {toc_pages_skipped}")
    print(f"wrote {out_path}")
    print(f"queries with no candidates: {missing if missing else 'none'}")


def load_pages() -> dict[str, list[dict]]:
    pages: dict[str, list[dict]] = {}
    for path in sorted(CORPUS_TEXT.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            pages.setdefault(record["docId"], []).append(record)
    for doc_pages in pages.values():
        doc_pages.sort(key=lambda r: r["page"])
    return pages


if __name__ == "__main__":
    main()
