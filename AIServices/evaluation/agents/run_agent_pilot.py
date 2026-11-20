"""Measure real token usage of the Fluxor multi-agent workflow.

This is a cost-measurement harness, not a quality evaluation. It runs the
production LangGraph workflow (`graph.workflow.fluxorWorkflow`) on a small,
fixed target list and records the provider-reported token usage of every LLM
call: input tokens, output tokens and the reasoning-token subset of the output.

Why the instrumentation lives here and not in the agents:

  `agents/*.py` call `model.with_structured_output(schema)` and discard the raw
  message, so the usage metadata is lost. The harness re-declares only the
  model-construction step (`getModel`) and asks for `include_raw=True`, which
  sends the same request and returns the same parsed object while keeping the
  raw `AIMessage`. Prompts, routing, node logic and the confidence loop are the
  unmodified production code.

Deliberate deviations from a production request, both recorded in the output:

  * Historical light curves are served from the frozen Track 1 cache
    (`evaluation/data/cache/*.npz`) instead of re-downloading every TESS sector
    through `download_all()`. The `historicalAgent` summary code is unchanged.
  * The candidate state carries `mission`/`sector` metadata but no `ra`/`dec`,
    because the frozen benchmark manifest does not store coordinates. SIMBAD is
    queried by object name and VizieR is skipped.

Reasoning tokens are billed as output tokens, so `outputTokens` already includes
them; `reasoningTokens` is reported as a subset for diagnosis, never added again.

Run (real, billed):
    python evaluation/agents/run_agent_pilot.py --limit 3

Run (plumbing check, no API calls, results marked dry-run):
    python evaluation/agents/run_agent_pilot.py --limit 3 --dry-run
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import types
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

PINNED_MODEL = "openai:gpt-5.4-mini-2026-03-17"

# List prices for gpt-5.4-mini, USD per 1M tokens.
INPUT_USD_PER_MTOK = 0.75
OUTPUT_USD_PER_MTOK = 4.50

DATA_DIR = AI_ROOT / "evaluation" / "data"
CACHE_DIR = DATA_DIR / "cache"
RESULTS_DIR = AI_ROOT / "evaluation" / "results"
PILOT_CHROMA = CACHE_DIR / "pilot_chroma"

WINDOW_SIZE = 200
STEP_SIZE = 100
MIN_POINTS = 80


# ---------------------------------------------------------------------------
# Token accounting
# ---------------------------------------------------------------------------

class TokenCounter:

    def __init__(self):

        self.calls: list[dict] = []
        self.usageMissing = 0

    def record(
        self,
        agent: str,
        raw,
        latencyMs: float,
        parsingError=None,
        stub: bool = False,
    ) -> None:

        usage = {}

        if raw is not None:

            usage = getattr(raw, "usage_metadata", None) or {}

            if not usage:

                usage = (
                    getattr(raw, "response_metadata", {}) or {}
                ).get("token_usage", {}) or {}

        inputTokens = int(
            usage.get("input_tokens")
            or usage.get("prompt_tokens")
            or 0
        )

        outputTokens = int(
            usage.get("output_tokens")
            or usage.get("completion_tokens")
            or 0
        )

        details = (
            usage.get("output_token_details")
            or usage.get("completion_tokens_details")
            or {}
        ) or {}

        reasoningTokens = int(
            details.get("reasoning")
            or details.get("reasoning_tokens")
            or 0
        )

        inputDetails = usage.get("input_token_details") or {}

        responseMetadata = getattr(raw, "response_metadata", {}) or {}

        if not stub and raw is not None and inputTokens == 0 and outputTokens == 0:

            self.usageMissing += 1

        self.calls.append(
            {
                "agent": agent,
                "inputTokens": inputTokens,
                "outputTokens": outputTokens,
                "reasoningTokens": reasoningTokens,
                "cachedInputTokens": int(
                    inputDetails.get("cache_read") or 0
                ),
                "latencyMs": round(latencyMs, 1),
                "modelRequested": PINNED_MODEL,
                "modelReported": responseMetadata.get("model_name"),
                "finishReason": (
                    (getattr(raw, "response_metadata", {}) or {}).get(
                        "finish_reason"
                    )
                    if raw is not None
                    else None
                ),
                "parsingError": str(parsingError) if parsingError else None,
                "stub": stub,
            }
        )

    def totals(self) -> dict:

        return {
            "calls": len(self.calls),
            "inputTokens": sum(c["inputTokens"] for c in self.calls),
            "outputTokens": sum(c["outputTokens"] for c in self.calls),
            "reasoningTokens": sum(c["reasoningTokens"] for c in self.calls),
        }


def costUsd(inputTokens: int, outputTokens: int) -> float:

    return round(
        inputTokens / 1_000_000 * INPUT_USD_PER_MTOK
        + outputTokens / 1_000_000 * OUTPUT_USD_PER_MTOK,
        6,
    )


# ---------------------------------------------------------------------------
# Model instrumentation
# ---------------------------------------------------------------------------

class InstrumentedModel:

    def __init__(self, model, counter: TokenCounter, agent: str):

        self.model = model
        self.counter = counter
        self.agent = agent

    def with_structured_output(self, schema, **kwargs):

        kwargs.pop("include_raw", None)

        chain = self.model.with_structured_output(
            schema,
            include_raw=True,
            **kwargs,
        )

        counter = self.counter
        agent = self.agent

        def invoke(prompt, *args, **callKwargs):

            started = time.perf_counter()

            output = chain.invoke(prompt, *args, **callKwargs)

            elapsedMs = (time.perf_counter() - started) * 1000.0

            counter.record(
                agent,
                output.get("raw"),
                elapsedMs,
                output.get("parsing_error"),
            )

            parsed = output.get("parsed")

            if parsed is None:

                raise ValueError(
                    f"{agent} structured output failed: "
                    f"{output.get('parsing_error')}"
                )

            return parsed

        return types.SimpleNamespace(invoke=invoke)


class StubModel:
    """Dry-run model: canned structured outputs, zero token usage."""

    def __init__(self, counter: TokenCounter, agent: str):

        self.counter = counter
        self.agent = agent

    def with_structured_output(self, schema, **kwargs):

        counter = self.counter
        agent = self.agent

        def invoke(prompt, *args, **callKwargs):

            started = time.perf_counter()
            time.sleep(0.01)

            if schema.__name__ == "TriageOutput":

                parsed = schema(
                    scientificallyInteresting=True,
                    priority="MEDIUM",
                    reason="Stub triage for plumbing check.",
                    artifactRisk=0.3,
                )

            else:

                hypothesis = schema.model_fields["hypotheses"].annotation.__args__[0]

                parsed = schema(
                    hypotheses=[
                        hypothesis(
                            name="Stellar flare",
                            explanation="Stub explanation.",
                            supportingEvidence=["stub"],
                            contradictingEvidence=["stub"],
                            confidence=0.4,
                        )
                    ],
                    confidence=0.5,
                    followupPlan=["Stub follow-up."],
                    reportMarkdown="# Stub report",
                )

            counter.record(
                agent,
                None,
                (time.perf_counter() - started) * 1000.0,
                stub=True,
            )

            return parsed

        return types.SimpleNamespace(invoke=invoke)


# ---------------------------------------------------------------------------
# Retrieval index
# ---------------------------------------------------------------------------

def ensureIndex(force: bool = False) -> dict:
    """Build the pilot Chroma index, verifying it is complete.

    `rag/documents/` is empty in the repository, so the frozen evaluation
    corpus is the document source. Chunk text comes from the Part 3 cache
    (`rag_1000_200_chunks.jsonl`, produced by the production splitter with
    `add_start_index=True` over the same PDFs); loading it instead of re-parsing
    500 PDF pages makes the build reproducible and a few seconds long. The
    embedding model, collection name and Chroma defaults come from
    `rag/vectorStore.py` unchanged, and retrieval still goes through
    `rag/retriever.py`.
    """

    import shutil

    import rag.vectorStore as vectorStore

    from langchain_chroma import Chroma
    from langchain_core.documents import Document

    vectorStore.CHROMA_DIR = PILOT_CHROMA

    # The production loader yields 1,874 chunks for this corpus and the frozen
    # Part 3 configuration yields 1,389; anything below this floor means a
    # partial build (an interrupted embedding pass leaves a valid-looking
    # sqlite file with no rows).
    expected = 1000

    if force and PILOT_CHROMA.exists():

        shutil.rmtree(PILOT_CHROMA)

    if (PILOT_CHROMA / "chroma.sqlite3").exists():

        try:

            existing = Chroma(
                collection_name=vectorStore.COLLECTION_NAME,
                embedding_function=vectorStore.get_embedding_model(),
                persist_directory=str(PILOT_CHROMA),
            )

            count = existing._collection.count()

            if count >= expected:

                return {"built": False, "path": str(PILOT_CHROMA), "chunks": count}

            print(f"index incomplete ({count} chunks); rebuilding")

            shutil.rmtree(PILOT_CHROMA)

        except Exception as error:

            print(f"index unreadable ({error}); rebuilding")

            if PILOT_CHROMA.exists():

                shutil.rmtree(PILOT_CHROMA)

    chunkPath = CACHE_DIR / "rag_1000_200_chunks.jsonl"

    if not chunkPath.exists():

        raise SystemExit(
            f"missing {chunkPath}; run the Part 3 RAG baseline once to build it"
        )

    chunks = [
        json.loads(line)
        for line in chunkPath.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]

    documents = [
        Document(
            page_content=chunk["text"],
            metadata={
                "source": chunk["docId"] + ".pdf",
                "page": chunk["page"],
                "start_index": chunk["charStart"],
            },
        )
        for chunk in chunks
    ]

    started = time.perf_counter()

    Chroma.from_documents(
        documents=documents,
        embedding=vectorStore.get_embedding_model(),
        collection_name=vectorStore.COLLECTION_NAME,
        persist_directory=str(PILOT_CHROMA),
    )

    return {
        "built": True,
        "path": str(PILOT_CHROMA),
        "chunks": len(documents),
        "seconds": round(time.perf_counter() - started, 1),
    }


# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

def loadManifest() -> dict:

    return json.loads(
        (DATA_DIR / "benchmark_manifest.json").read_text(encoding="utf-8")
    )


def selectTargets(split: str, limit: int) -> list[str]:

    manifest = loadManifest()

    return sorted(manifest["splits"][split])[:limit]


def scoreTarget(objectId: str, sector: int) -> dict:
    """Run the production detector on the frozen light curve."""

    import numpy as np

    from ml.anomalyDetector import AnomalyDetector
    from ml.features import extract_window_features
    from ml.preprocessing import preprocess_light_curve

    path = CACHE_DIR / (objectId.replace(" ", "_") + ".npz")

    with np.load(path) as data:

        timeArr = np.asarray(data["time"], dtype=float)
        fluxArr = np.asarray(data["flux"], dtype=float)

    timeClean, fluxClean = preprocess_light_curve(timeArr, fluxArr)

    features, windows = extract_window_features(
        timeClean, fluxClean, WINDOW_SIZE, STEP_SIZE, MIN_POINTS
    )

    result = AnomalyDetector().detect(features, windows)

    return {
        "anomalyScore": result["anomalyScore"],
        "priority": result["priority"],
        "windows": result["totalWindows"],
        "metadata": {
            "mission": "TESS",
            "sector": sector,
            "points": int(len(fluxClean)),
            "source": "TESS 2-minute photometry (frozen Track 1 cache)",
        },
    }


def patchHistoricalTool() -> None:
    """Serve historicalAgent from the frozen cache instead of re-downloading."""

    import numpy as np

    import agents.historicalAgent as historicalModule

    def fetchCached(object_id: str, source: str = "TESS"):

        path = CACHE_DIR / (object_id.replace(" ", "_") + ".npz")

        if not path.exists():

            raise FileNotFoundError(f"no cached light curve for {object_id}")

        with np.load(path) as data:

            return {
                "objectId": object_id,
                "mission": source,
                "time": np.asarray(data["time"], dtype=float),
                "flux": np.asarray(data["flux"], dtype=float),
            }

    historicalModule.fetch_light_curve = fetchCached


def patchOfflineCatalog() -> None:
    """Dry-run only: deterministic catalog answers, no network."""

    import agents.catalogAgent as catalogModule

    catalogModule.get_simbad_object = lambda objectId: {
        "found": False,
        "objectId": objectId,
        "source": "SIMBAD",
        "error": "offline stub",
    }

    catalogModule.get_simbad_by_coordinates = lambda ra, dec: {
        "found": False,
        "source": "SIMBAD",
        "data": [],
    }

    catalogModule.query_vizier = lambda ra, dec: {
        "found": False,
        "source": "VizieR",
        "catalogs": [],
    }


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

def runTarget(
    initialState: dict,
    counter: TokenCounter,
) -> dict:

    from graph.workflow import fluxorWorkflow

    path: list[str] = []
    nodeMs: dict[str, float] = {}

    started = time.perf_counter()
    previous = started

    for update in fluxorWorkflow.stream(initialState, stream_mode="updates"):

        now = time.perf_counter()

        for node in update:

            path.append(node)
            nodeMs[node] = round((now - previous) * 1000.0, 1)

        previous = now

    wallMs = round((time.perf_counter() - started) * 1000.0, 1)

    return {
        "nodePath": path,
        "nodeLatencyMs": nodeMs,
        "wallMs": wallMs,
    }


def main() -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=3)
    parser.add_argument("--split", default="test")
    parser.add_argument(
        "--model",
        default=PINNED_MODEL,
        help="LLM_MODEL value; defaults to the pinned gpt-5.4-mini snapshot",
    )
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--rebuild-index", action="store_true")
    args = parser.parse_args()

    from dotenv import load_dotenv

    load_dotenv(dotenv_path=AI_ROOT / ".env")

    if not args.dry_run and not os.environ.get("OPENAI_API_KEY"):

        raise SystemExit("OPENAI_API_KEY is not set; cannot run a billed pilot")

    # Must precede the agent imports: they read LLM_MODEL at first call.
    os.environ["LLM_MODEL"] = args.model

    index = ensureIndex(force=args.rebuild_index)
    print(f"index: {index}")

    patchHistoricalTool()

    if args.dry_run:

        patchOfflineCatalog()

    import agents.reasoningAgent as reasoningModule
    import agents.triageAgent as triageModule

    counter = TokenCounter()

    if args.dry_run:

        triageModule.getModel = lambda: StubModel(counter, "triage")
        reasoningModule.getModel = lambda: StubModel(counter, "reasoning")

    else:

        from langchain.chat_models import init_chat_model

        sharedModel = init_chat_model(args.model, temperature=0)

        triageModule.getModel = lambda: InstrumentedModel(
            sharedModel, counter, "triage"
        )
        reasoningModule.getModel = lambda: InstrumentedModel(
            sharedModel, counter, "reasoning"
        )

    targets = selectTargets(args.split, args.limit)
    manifest = loadManifest()

    runs: list[dict] = []

    for objectId in targets:

        sector = int(manifest["objects"][objectId]["sector"])
        scored = scoreTarget(objectId, sector)

        initialState = {
            "candidateId": f"pilot:{objectId}",
            "objectId": objectId,
            "anomalyScore": scored["anomalyScore"],
            "priority": scored["priority"],
            "metadata": scored["metadata"],
            "iterationCount": 0,
            "hypotheses": [],
            "ragEvidence": [],
            "confidence": 0,
            "status": "started",
        }

        before = len(counter.calls)

        trace = runTarget(initialState, counter)

        calls = counter.calls[before:]

        inputTokens = sum(c["inputTokens"] for c in calls)
        outputTokens = sum(c["outputTokens"] for c in calls)

        runs.append(
            {
                "objectId": objectId,
                "split": args.split,
                "sector": sector,
                "anomalyScore": scored["anomalyScore"],
                "priority": scored["priority"],
                "nodePath": trace["nodePath"],
                "nodeLatencyMs": trace["nodeLatencyMs"],
                "wallMs": trace["wallMs"],
                "llmCalls": calls,
                "inputTokens": inputTokens,
                "outputTokens": outputTokens,
                "reasoningTokens": sum(
                    c["reasoningTokens"] for c in calls
                ),
                "costUsd": costUsd(inputTokens, outputTokens),
            }
        )

        print(
            f"{objectId}: nodes={len(trace['nodePath'])} "
            f"calls={len(calls)} in={inputTokens} out={outputTokens} "
            f"reasoning={runs[-1]['reasoningTokens']} "
            f"${runs[-1]['costUsd']:.4f}"
        )

    totalIn = sum(r["inputTokens"] for r in runs)
    totalOut = sum(r["outputTokens"] for r in runs)

    payload = {
        "mode": "dry-run" if args.dry_run else "measured",
        "modelRequested": args.model,
        "priceUsdPerMillionTokens": {
            "input": INPUT_USD_PER_MTOK,
            "output": OUTPUT_USD_PER_MTOK,
        },
        "reasoningTokensBilledAsOutput": True,
        "index": index,
        "targets": targets,
        "deviationFromProduction": [
            "historical light curves served from the frozen Track 1 cache "
            "instead of download_all()",
            "no ra/dec in candidate metadata, so VizieR is skipped and SIMBAD "
            "is queried by object name only",
        ],
        "usageMissingResponses": counter.usageMissing,
        "runs": runs,
        "totals": {
            "runs": len(runs),
            "llmCalls": sum(len(r["llmCalls"]) for r in runs),
            "inputTokens": totalIn,
            "outputTokens": totalOut,
            "reasoningTokens": sum(r["reasoningTokens"] for r in runs),
            "costUsd": costUsd(totalIn, totalOut),
        },
        "capturedAtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    outPath = RESULTS_DIR / f"agent_pilot_{stamp}.json"
    outPath.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    print(f"\nwrote {outPath}")
    print(
        f"totals: runs={len(runs)} calls={payload['totals']['llmCalls']} "
        f"in={totalIn} out={totalOut} "
        f"reasoning={payload['totals']['reasoningTokens']} "
        f"cost=${payload['totals']['costUsd']:.4f} "
        f"({payload['mode']})"
    )


if __name__ == "__main__":
    main()
