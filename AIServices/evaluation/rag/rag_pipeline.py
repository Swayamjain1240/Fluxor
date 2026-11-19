"""Retrieval harness for the frozen Fluxor RAG corpus.

Uses the production splitter configuration (`RecursiveCharacterTextSplitter` with
`add_start_index=True`, applied per PDF page, exactly as `rag/vectorStore.py`
does) and the production embedding model (`rag/embeddings.get_embedding_model`).

Ranking is exact cosine similarity over the same normalised vectors. Chroma's
default space is L2, and for unit vectors ||a-b||^2 = 2 - 2(a.b), so the induced
ordering is identical; only ANN/index overhead is absent. This is disclosed in the
report rather than presented as a measurement of Chroma itself.
"""

from __future__ import annotations

import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

DATA_DIR = AI_ROOT / "evaluation" / "data"
CORPUS_TEXT = DATA_DIR / "corpus" / "text"
CACHE_DIR = DATA_DIR / "cache"
MANIFEST = DATA_DIR / "corpus_manifest.json"
QUERIES = DATA_DIR / "rag_queries.jsonl"


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


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


def load_corpus_manifest() -> dict:
    if not MANIFEST.exists():
        raise FileNotFoundError(
            "corpus_manifest.json missing; run evaluation/data/build_rag_corpus.py first"
        )
    return json.loads(MANIFEST.read_text(encoding="utf-8"))


def load_queries() -> list[dict]:
    records = []
    for line in QUERIES.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        if "qid" in record:
            records.append(record)
    return records


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------


def build_chunks(
    pages: dict[str, list[dict]], chunk_size: int, chunk_overlap: int
) -> list[dict]:
    """Split each page with the production splitter, keeping exact offsets."""
    from langchain_core.documents import Document
    from langchain_text_splitters import RecursiveCharacterTextSplitter

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        add_start_index=True,
    )

    chunks: list[dict] = []

    for doc_id in sorted(pages):
        for record in pages[doc_id]:
            text = record["text"]
            if not text.strip():
                continue

            pieces = splitter.split_documents(
                [
                    Document(
                        page_content=text,
                        metadata={"source": doc_id, "page": record["page"]},
                    )
                ]
            )

            for piece in pieces:
                start = int(piece.metadata.get("start_index", 0))
                body = piece.page_content
                chunks.append(
                    {
                        "docId": doc_id,
                        "page": record["page"],
                        "charStart": start,
                        "charEnd": start + len(body),
                        "text": body,
                    }
                )

    return chunks


def embed_documents(texts: list[str]) -> np.ndarray:
    from rag.embeddings import get_embedding_model

    model = get_embedding_model()
    vectors = model.embed_documents(texts)
    matrix = np.asarray(vectors, dtype=np.float32)
    # Normalise defensively; the production model already does this.
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


def embed_queries(texts: list[str]) -> np.ndarray:
    from rag.embeddings import get_embedding_model

    model = get_embedding_model()
    vectors = model.embed_query(texts[0]) if len(texts) == 1 else None

    if len(texts) == 1:
        matrix = np.asarray([vectors], dtype=np.float32)
    else:
        matrix = np.asarray(model.embed_documents(texts), dtype=np.float32)

    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    return matrix / norms


# ---------------------------------------------------------------------------
# Index (cached per chunk configuration)
# ---------------------------------------------------------------------------


def build_index(
    chunk_size: int, chunk_overlap: int, pages: dict[str, list[dict]] | None = None
) -> dict:
    """Chunks + embeddings for one configuration, cached on disk."""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    key = f"rag_{chunk_size}_{chunk_overlap}"
    chunk_path = CACHE_DIR / f"{key}_chunks.jsonl"
    vector_path = CACHE_DIR / f"{key}_vectors.npy"

    started = time.time()

    if chunk_path.exists() and vector_path.exists():
        chunks = [
            json.loads(line)
            for line in chunk_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        matrix = np.load(vector_path)
        return {
            "config": {"chunkSize": chunk_size, "chunkOverlap": chunk_overlap},
            "chunks": chunks,
            "vectors": matrix,
            "cached": True,
            "buildSeconds": round(time.time() - started, 2),
        }

    pages = pages if pages is not None else load_pages()
    chunks = build_chunks(pages, chunk_size, chunk_overlap)

    embed_started = time.time()
    matrix = embed_documents([c["text"] for c in chunks])
    embed_seconds = time.time() - embed_started

    with chunk_path.open("w", encoding="utf-8", newline="\n") as handle:
        for chunk in chunks:
            handle.write(json.dumps(chunk, ensure_ascii=False) + "\n")
    np.save(vector_path, matrix)

    return {
        "config": {"chunkSize": chunk_size, "chunkOverlap": chunk_overlap},
        "chunks": chunks,
        "vectors": matrix,
        "cached": False,
        "embedSeconds": round(embed_seconds, 2),
        "buildSeconds": round(time.time() - started, 2),
    }


def index_digest(chunks: list[dict]) -> str:
    payload = json.dumps(
        [[c["docId"], c["page"], c["charStart"], c["charEnd"]] for c in chunks],
        sort_keys=True,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# Search
# ---------------------------------------------------------------------------


def search(query_vector: np.ndarray, matrix: np.ndarray, top_k: int) -> list[int]:
    """Indices of the top_k highest cosine similarities, best first."""
    scores = matrix @ query_vector
    k = min(top_k, len(scores))
    order = np.argsort(-scores, kind="stable")[:k]
    return [int(i) for i in order]


def search_with_scores(
    query_vector: np.ndarray, matrix: np.ndarray, top_k: int
) -> list[dict]:
    scores = matrix @ query_vector
    k = min(top_k, len(scores))
    order = np.argsort(-scores, kind="stable")[:k]
    return [{"index": int(i), "score": float(scores[i])} for i in order]
