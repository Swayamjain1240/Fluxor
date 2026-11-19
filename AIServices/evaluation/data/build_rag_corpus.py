"""Fetch and freeze the approved RAG corpus for Fluxor evaluation.

The 12 documents below were approved by the project owner. This script:
  1. downloads each document exactly once (cached afterwards),
  2. captures the licence displayed by the source at fetch time,
  3. records SHA-256, size, page and character counts,
  4. extracts per-page text with pypdf into a JSONL file,
  5. writes corpus_manifest.json, which is the frozen record of the corpus.

LICENSING: PDFs and extracted text stay local. They are never committed
(evaluation/.gitignore covers the corpus directory), so nothing is redistributed.
arXiv's default "perpetual non-exclusive license" and CC BY-NC-ND both restrict
redistribution, which is why only metadata, hashes and URL are recorded in the
tracked manifest.

Annotation helper:
    python evaluation/data/build_rag_corpus.py --search "scattered light"

Run:
    python evaluation/data/build_rag_corpus.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

DATA_DIR = AI_ROOT / "evaluation" / "data"
CORPUS_DIR = DATA_DIR / "corpus"

USER_AGENT = "FluxorRAGBenchmark/1.0 (research evaluation; contact: project owner)"

# Approved corpus. `arxiv` ids are used for both licence lookup and PDF fetch.
DOCUMENTS = [
    {
        "docId": "D01",
        "kind": "nasa",
        "title": "TESS Instrument Handbook v0.1",
        "authors": "Vanderspek et al.",
        "year": 2018,
        "identifier": "TESS Instrument Handbook v0.1",
        "url": "https://archive.stsci.edu/missions/tess/doc/TESS_Instrument_Handbook_v0.1.pdf",
    },
    {
        "docId": "D02",
        "kind": "nasa",
        "title": "Kepler Instrument Handbook",
        "authors": "Caldwell & Van Cleve",
        "year": 2016,
        "identifier": "KSCI-19033-002",
        "url": "https://archive.stsci.edu/kepler/manuals/KSCI-19033-002.pdf",
    },
    {
        "docId": "D03",
        "kind": "arxiv",
        "arxiv": "2110.13155",
        "title": "No Such Thing as a Simple Flare: Substructure and QPPs Observed in a "
        "Statistical Sample of 20 Second Cadence TESS Flares",
        "authors": "Howard & MacGregor",
        "year": 2022,
    },
    {
        "docId": "D04",
        "kind": "arxiv",
        "arxiv": "2409.02540",
        "title": "Scalable, Advanced Machine Learning-based Approaches for Stellar Flare "
        "Identification: Application to TESS short-cadence Data",
        "authors": "Lin et al.",
        "year": 2024,
    },
    {
        "docId": "D05",
        "kind": "arxiv",
        "arxiv": "2511.13716",
        "title": "Stellar Flares in the TESS Light Curves of Planet-hosting M dwarfs",
        "authors": "(as published)",
        "year": 2025,
    },
    {
        "docId": "D06",
        "kind": "arxiv",
        "arxiv": "2110.13382",
        "title": "TESS Eclipsing Binary Stars. I. Short cadence observations of 4584 "
        "eclipsing binaries in Sectors 1-26",
        "authors": "Prsa et al.",
        "year": 2022,
    },
    {
        "docId": "D07",
        "kind": "arxiv",
        "arxiv": "2506.05631",
        "title": "The TESS Ten Thousand Catalog: 10,001 uniformly-vetted and -validated "
        "Eclipsing Binary Stars",
        "authors": "(as published)",
        "year": 2025,
    },
    {
        "docId": "D08",
        "kind": "arxiv",
        "arxiv": "2106.15063",
        "title": "The unpopular Package: a Data-driven Approach to De-trend TESS Full Frame "
        "Image Light Curves",
        "authors": "Hattori et al.",
        "year": 2021,
    },
    {
        "docId": "D09",
        "kind": "arxiv",
        "arxiv": "1203.1383",
        "title": "Kepler Presearch Data Conditioning II - A Bayesian Approach to Systematic "
        "Error Correction",
        "authors": "Twicken et al.",
        "year": 2012,
    },
    {
        "docId": "D10",
        "kind": "arxiv",
        "arxiv": "2204.06020",
        "title": "Localizing Sources of Variability in Crowded TESS Photometry",
        "authors": "Higgins & Bell",
        "year": 2022,
    },
    {
        "docId": "D11",
        "kind": "arxiv",
        "arxiv": "2008.03311",
        "title": "Alert Classification for the ALeRCE Broker System: The Light Curve "
        "Classifier",
        "authors": "Sanchez-Saez et al.",
        "year": 2021,
    },
    {
        "docId": "D12",
        "kind": "arxiv",
        "arxiv": "2008.03303",
        "title": "The Automatic Learning for the Rapid Classification of Events (ALeRCE) "
        "Alert Broker",
        "authors": "Forster et al.",
        "year": 2021,
    },
]


# ---------------------------------------------------------------------------
# Fetching
# ---------------------------------------------------------------------------


def _ssl_context():
    """CA bundle for TLS verification.

    Verifies against certifi's roots when available. Verification is never
    disabled; if no bundle can be found the call is left to fail loudly.
    """
    try:
        import ssl

        import certifi

        return ssl.create_default_context(cafile=certifi.where())
    except Exception:
        return None


def http_get(url: str, timeout: int = 120) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    context = _ssl_context()
    kwargs = {"timeout": timeout}
    if context is not None:
        kwargs["context"] = context
    with urllib.request.urlopen(request, **kwargs) as response:
        return response.read()


def pdf_url(document: dict) -> str:
    if document["kind"] == "arxiv":
        return f"https://arxiv.org/pdf/{document['arxiv']}"
    return document["url"]


def licence_for(document: dict) -> dict:
    """Read the licence the source displays at fetch time.

    arXiv abstract pages name the licence beneath the download options. NASA
    technical reports are US Government works; that is recorded explicitly rather
    than inferred silently.
    """
    if document["kind"] == "nasa":
        return {
            "licence": "US Government work (NASA technical report)",
            "redistributable": False,
            "note": "Treated as public domain in the US; still kept local-only here.",
            "source": "mission documentation page",
        }

    arxiv_id = document["arxiv"]
    try:
        html = http_get(f"https://arxiv.org/abs/{arxiv_id}").decode("utf-8", "replace")
    except Exception as error:
        return {"licence": "unknown", "error": f"{type(error).__name__}: {error}"}

    match = re.search(r"creativecommons\.org/licenses/([a-z\-]+)/(\d\.\d)", html)
    if match:
        return {
            "licence": f"CC {match.group(1).upper()} {match.group(2)}",
            "redistributable": match.group(1) == "by",
            "source": f"arxiv.org/abs/{arxiv_id}",
        }

    if "nonexclusive-distrib" in html or "perpetual non-exclusive" in html:
        return {
            "licence": "arXiv.org perpetual non-exclusive license 1.0",
            "redistributable": False,
            "note": "Does not grant redistribution; local use only.",
            "source": f"arxiv.org/abs/{arxiv_id}",
        }

    return {
        "licence": "not detected",
        "redistributable": False,
        "source": f"arxiv.org/abs/{arxiv_id}",
    }


def extract_pages(pdf_path: Path) -> list[dict]:
    from pypdf import PdfReader

    reader = PdfReader(str(pdf_path))
    pages = []
    for index, page in enumerate(reader.pages):
        try:
            text = page.extract_text() or ""
        except Exception as error:
            text = ""
            pages.append(
                {"page": index + 1, "text": text, "error": f"{type(error).__name__}"}
            )
            continue
        pages.append({"page": index + 1, "text": text})
    return pages


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------


def build(force: bool = False) -> dict:
    pdf_dir = CORPUS_DIR / "pdf"
    text_dir = CORPUS_DIR / "text"
    pdf_dir.mkdir(parents=True, exist_ok=True)
    text_dir.mkdir(parents=True, exist_ok=True)

    entries = []
    failures = []

    for document in DOCUMENTS:
        doc_id = document["docId"]
        target = pdf_dir / f"{doc_id}.pdf"

        if not target.exists() or force:
            url = pdf_url(document)
            print(f"[{doc_id}] fetching {url}")
            try:
                payload = http_get(url)
            except Exception as error:
                failures.append({"docId": doc_id, "error": f"{type(error).__name__}: {error}"})
                print(f"  FAILED: {error}")
                continue
            target.write_bytes(payload)
            time.sleep(1.0)  # be polite to the source
        else:
            print(f"[{doc_id}] cached {target.stat().st_size} bytes")

        payload = target.read_bytes()
        digest = hashlib.sha256(payload).hexdigest()

        pages = extract_pages(target)
        total_chars = sum(len(p.get("text", "")) for p in pages)

        if total_chars == 0:
            failures.append({"docId": doc_id, "error": "no extractable text"})
            print("  FAILED: no extractable text")
            continue

        with (text_dir / f"{doc_id}.jsonl").open("w", encoding="utf-8", newline="\n") as handle:
            for page in pages:
                handle.write(
                    json.dumps(
                        {"docId": doc_id, "page": page["page"], "text": page["text"]},
                        ensure_ascii=False,
                    )
                    + "\n"
                )

        licence = licence_for(document)
        entry = {
            "docId": doc_id,
            "title": document["title"],
            "authors": document["authors"],
            "year": document["year"],
            "kind": document["kind"],
            "identifier": document.get("arxiv") or document.get("identifier"),
            "url": pdf_url(document),
            "sha256": digest,
            "bytes": len(payload),
            "pages": len(pages),
            "chars": total_chars,
            "charsPerPage": round(total_chars / max(1, len(pages)), 1),
            **licence,
        }
        entries.append(entry)
        print(
            f"  pages={len(pages)} chars={total_chars} licence={licence.get('licence')}"
        )

    if failures:
        raise SystemExit(
            f"{len(failures)} document(s) failed; corpus incomplete, refusing to freeze.\n"
            + json.dumps(failures, indent=2)
        )

    manifest = {
        "corpusId": "fluxor-astronomy-v1",
        "approvedBy": "project owner (12-document list)",
        "frozen": True,
        "redistributionPolicy": (
            "PDFs and extracted text are local-only and never committed. Only metadata, "
            "URLs, licences and hashes are tracked."
        ),
        "documents": entries,
        "totals": {
            "documents": len(entries),
            "pages": sum(e["pages"] for e in entries),
            "chars": sum(e["chars"] for e in entries),
        },
        "builtAtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    (DATA_DIR / "corpus_manifest.json").write_text(
        json.dumps(manifest, indent=2), encoding="utf-8"
    )

    print(
        f"\ncorpus frozen: {manifest['totals']['documents']} documents, "
        f"{manifest['totals']['pages']} pages, {manifest['totals']['chars']} chars"
    )
    return manifest


# ---------------------------------------------------------------------------
# Annotation helper
# ---------------------------------------------------------------------------


def iter_pages(text_dir: Path):
    for path in sorted(text_dir.glob("*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                yield json.loads(line)


def search(terms: str, window: int = 420, limit: int = 6) -> None:
    """Print up to `limit` passages per document containing all `terms`."""
    text_dir = CORPUS_DIR / "text"
    needles = [t.strip().lower() for t in terms.split("|") if t.strip()]

    per_doc: dict[str, int] = {}

    for record in iter_pages(text_dir):
        text = record["text"]
        lowered = text.lower()
        for needle in needles:
            start = 0
            while True:
                index = lowered.find(needle, start)
                if index < 0:
                    break
                start = index + 1
                if per_doc.get(record["docId"], 0) >= limit:
                    break

                lo = max(0, index - window // 4)
                hi = min(len(text), index + window)
                snippet = " ".join(text[lo:hi].split())

                print(
                    f"\n--- {record['docId']} p{record['page']} @{index} "
                    f"[{needle}] ---\n{snippet}"
                )
                per_doc[record["docId"]] = per_doc.get(record["docId"], 0) + 1


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--force", action="store_true", help="re-download everything")
    parser.add_argument("--search", help="pipe-separated terms; prints matching passages")
    parser.add_argument("--limit", type=int, default=6)
    parser.add_argument("--window", type=int, default=420)
    args = parser.parse_args()

    if args.search:
        search(args.search, window=args.window, limit=args.limit)
        return

    build(force=args.force)


if __name__ == "__main__":
    main()
