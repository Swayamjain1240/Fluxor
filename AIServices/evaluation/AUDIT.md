# Fluxor — Part 1 Audit and Evaluation Methodology Register

Status: **Part 1 conditionally approved by the project owner (2026-11-18).**
Scope of this document: verified repository/dataset audit, approved evaluation design,
methodology controls, limitation register, and file plan.
It contains **no experimental results**. No model has been fitted, no retrieval has been run,
and no metric has been computed. Any number not traceable to a result artifact must be treated
as fabricated.

---

## 1. Environment snapshot (measured)

| Item | Value |
|---|---|
| Interpreter | Python 3.13.9 (`AIServices/venv`) |
| Git | 12 commits, 114 tracked files, clean working tree at audit time |
| Syntax check | `python -m compileall` passes on all AI modules |
| numpy | 2.5.3 |
| scikit-learn | 1.9.0 |
| scipy | 1.18.1 |
| pandas | 2.3.3 |
| chromadb | 1.5.9 |
| langchain | 1.4.0 |
| langchain-chroma | 1.1.0 |
| langchain-huggingface | 1.2.2 |
| langgraph | 1.2.11 |
| sentence-transformers | 6.0.1 |
| torch | 2.14.0+cpu |
| tiktoken | 0.14.0 |
| fastapi | 0.141.1 |
| pypdf | 6.18.1 |
| astroquery | 0.4.11 |
| lightkurve | 2.6.0 |

Config keys present in `AIServices/.env` (names inspected, values never read):
`APP_NAME, ENVIRONMENT, HOST, PORT, OPENAI_API_KEY, LLM_MODEL, CONFIDENCE_THRESHOLD, MAX_ITERATIONS`.

**Reproducibility defect:** `AIServices/requirements.txt` (177 pins) and `AIServices/requirement.txt`
(44 pins) are **UTF-16LE** encoded. `pip install -r` decodes as UTF-8 and fails. This is a
reproducibility blocker and is scheduled as an encoding-only fix (no version edits).

---

## 2. Verified pipeline status

### 2.1 ML anomaly detection — modules exist, pipeline unreachable

| Component | Path | Verified state |
|---|---|---|
| Preprocessing | `ml/preprocessing.py` | Enforces >=100 points, drops non-finite, sorts by time, normalizes flux by median. **Imported by nothing.** |
| Feature extraction | `ml/features.py` | 8 features per window: `mean_flux, std_flux, median_flux, amplitude, iqr, mad, slope, outlier_ratio`. `window_size=200, step_size=100, min_points=80`. **Imported by nothing.** |
| Detector | `ml/anomalyDetector.py` | `IsolationForest(n_estimators=200, contamination="auto", random_state=42, n_jobs=-1)`; `fit_predict` + `decision_function`; `anomalyScore = 1/(1+exp(8*decision))`. **Imported by nothing.** |
| API entry | `main.py:/detect_anomalies` | Explicit placeholder returning `candidates: []`. |

Consequence: `Backend/services/anomalyServices.js` creates zero candidates and still persists
`dataset.status = "completed"` — a silent no-op that looks like a successful run.

Additional verified defects in that path:
1. `Backend/models/datasetModel.js` requires `dataPath`; `datasetService.createDatasetService` never
   sets it, so dataset creation fails Mongoose validation. The ML entry path is unreachable via the API.
2. `main.py` raises `HTTPException` but imports only `FastAPI, BaseModel, Field` → `NameError` instead
   of an HTTP 500 on any agent failure.

### 2.2 RAG — code complete, corpus and index absent

| Component | Verified value |
|---|---|
| Ingestion | `rag/vectorStore.py`: PDFs (per page via `pypdf`) and `.txt/.md` from `rag/documents/` |
| Splitter | `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)` |
| Collection | `fluxor_astronomy` |
| Persist dir | `rag/chroma_db/` — **does not exist** |
| Embeddings | `sentence-transformers/all-MiniLM-L6-v2`, 384-d, `normalize_embeddings=True` |
| Retrieval | `similarity_search_with_score(query, k=5)`; returns `content, source, page, startIndex, distance` |
| Corpus size | **0 chunks** — `rag/documents/` contains only `README.md` |
| Index build | `build_vectorstore()` **never called anywhere** |

### 2.3 Multi-agent workflow — real, and the strongest implemented subsystem

`graph/workflow.py` compiles a 5-node `StateGraph`:

```
START -> triageAgent -(conditional)-+-> catalogAgent -> historicalAgent -> ragAgent -> reasoningAgent
                                    |                                                        |
                                    +-> archive -> END                    (confidence) <------+
                                                                                              |
                                        finalize -> END  <=  confidence >= 0.72  OR  iterations >= 3
                                        ragAgent         <=  otherwise (targeted re-retrieval)
```

- LLM nodes: `triageAgent`, `reasoningAgent` (`init_chat_model`, `temperature=0`, `with_structured_output`).
- Deterministic tool nodes: `catalogAgent` (SIMBAD, VizieR), `historicalAgent` (MAST via lightkurve), `ragAgent`.
- Bound: `CONFIDENCE_THRESHOLD=0.72`, `MAX_ITERATIONS=3` (env-overridable). Max 3 reasoning calls, 3 retrievals.
- Follow-up plan and Markdown report are produced **by `reasoningAgent`**; there is no `followupAgent.py`.
- `triageAgent`/`reasoningAgent` default to `"openai:gpt-5.4-mini"`, which **is** a valid OpenAI model
  (default snapshot `gpt-5.4-mini-2026-03-17`, $0.75 / $4.50 per 1M input / output tokens). An earlier version
  of this audit wrongly called it an unknown model ID; corrected 2026-11-19. The model and snapshot still
  must be pinned explicitly in the `LLM_MODEL` value for the Part 4 runs, and any reasoning-token usage
  reported by the provider must be recorded, because it is billed as output.

### 2.4 Existing evaluation utilities — present, never executed, partly incorrect

| Module | Verified capability | Defect |
|---|---|---|
| `evaluation/mlEvaluation.py` | precision, recall, F1, FPR, confusion matrix | No FNR, no ROC-AUC/PR-AUC, no latency, no labels source. No caller. |
| `evaluation/ragEvaluation.py` | source-level hit/precision/recall/citation coverage | Precision denominator is `|unique retrieved source names|`, collapsing 5 chunk results into a filename set; no per-rank P@K, no nDCG, no MRR, no latency. Its `__main__` block references `stellarFlares.pdf` / `tessArtifacts.pdf`, which do not exist. |
| `evaluation/agentEvaluation.py` | structural completeness, evidence coverage, iteration-bound compliance | `archived` used to be counted as completed, inflating `completionRate`; **fixed 2026-11-20** and covered by `evaluation/tests/test_agent_evaluation.py`. `needs_review` still counts, because that run reached `finalize` and did investigate. No timing, no token usage, no tool-call success, no retry accounting. |

---

## 3. Dataset and label audit

| Question | Verified answer |
|---|---|
| Dataset file in version control? | **None.** Zero `.csv/.parquet/.jsonl/.fits/.npz`; only `package(-lock).json`. |
| Anomaly ground-truth labels? | **None anywhere.** |
| RAG query->relevance judgments? | **None.** Two hardcoded queries pointing at nonexistent PDFs. |
| Train/val/test splits? | **None.** |
| Tests? | **None.** No `test`/`spec`/`conftest` files; pytest not installed. |
| Vector index? | **None.** 0 chunks. |
| Data acquisition capability? | `tools/mastTool.py` can fetch real TESS/Kepler light curves; `simbadTool`/`vizierTool` reach real catalogues. Nothing is cached or persisted. |

**Therefore no metric in the project brief can be reported today.** None is reported here.

---

## 4. Validity hazards and required controls

| # | Hazard | Control |
|---|---|---|
| H1 | `window_size=200, step=100` → adjacent windows share 50% of samples; a random row split leaks | Split by **object**, never by window; evaluate contiguously within a curve |
| H2 | Deployed semantics fit `IsolationForest` on the same windows it scores, per light curve | Evaluate both semantics (per-curve transductive vs pooled-train/held-out); designate one primary and report both |
| H3 | `contamination="auto"` sets a **fixed** score threshold (`offset_ = -0.5`), not a target quantile, so the flagged fraction is data-dependent. Confirmed empirically in the Part 2 baseline: 11.6% of pooled-train windows were flagged but only 0.8% of held-out test windows | Report ranking quality (ROC-AUC / PR-AUC, computable from the monotone `decisionScore`) alongside threshold-conditional P/R/F1; never present flag rate as detection skill |
| H4 | `anomalyScore` is `sigmoid(8*decision)`, saturated (`|decision| > 0.6` → 0.008 / 0.992) | Never report as calibrated probability; use only for ranking and priority bands |
| H5 | Chroma chunk IDs change with chunk size, so relevance labels could silently change meaning | Judge relevance on **chunking-invariant gold spans** `(doc_id, page, char_start, char_end)`; map to chunks per configuration |
| H6 | Generating eval queries from chunk text makes retrieval trivially easy | Author queries independently of the chunking under test |
| H7 | SIMBAD / VizieR / MAST latency and availability vary | Record/replay tool cache for agent benchmarks so latency isolates agent cost |
| H8 | Corpus drift between baseline and optimized RAG experiments | Freeze corpus, hash each file (SHA-256), record manifest hash in every result |

---

## 5. Approved evaluation decisions (owner, 2026-11-18)

### 5.1 ML labels — APPROVED with conditions

- Run **Track 1 (controlled anomaly injection)** and **Track 2 (catalogue-derived proxy labels)**.
- The two tracks are kept separate in datasets, scripts, metrics, and reports. They are never merged
  and never averaged.
- Track 1 uses synthetic ground truth that is known by construction.
- Track 2 must be labelled **weak-label / proxy evaluation** everywhere it appears, never
  "confirmed anomaly ground truth".
- Injection methodology, anomaly types, assumptions and limitations must be documented (Section 6).
- No leakage between train / validation / test (Section 6.4).

### 5.2 RAG corpus — APPROVED WITH A PRIOR GATE

- A small, frozen, hash-versioned NASA/arXiv astronomy corpus.
- **The document list must be approved by the owner before any download or ingestion.**
  The proposed list, with URLs, selection criteria, size estimate, annotation methodology and
  licensing analysis, is presented for approval alongside this document.
- On approval, the approved list is frozen into `AIServices/evaluation/data/corpus_manifest.json`
  (doc_id, title, authors, year, identifier, URL, license, SHA-256, page count).

### 5.3 Production fixes — SEPARATE FROM EVALUATION

- Production fixes are not part of evaluation work. No broad refactoring, no architecture changes.
- Evaluation is performed against the ML/RAG modules as pure functions, which requires **no**
  production change.
- Any production fix that becomes necessary must be documented, proposed with exact
  CREATE/UPDATE paths, and implemented only after separate approval.

### 5.4 Reporting discipline

- Measured, estimated, and unverified results are labelled distinctly.
- Failed experiments are reported, not hidden.
- One experimental variable changes at a time; every run records seed, configuration, and data hash.

---

## 6. Track 1 injection methodology (specification, not yet executed)

### 6.1 Base data
Real public light curves from MAST via the existing `lightkurve` dependency, downloaded **once**,
cached to `AIServices/evaluation/data/cache/*.npz`, each with SHA-256 and `object_id` recorded.
Provenance: mission, target ID, sector/quarter, cadence, flux column (PDC-SAP).

### 6.2 Injected anomaly classes

| ID | Class | Morphology | Amplitude | Duration |
|---|---|---|---|---|
| T1 | Flare | fast exponential rise, slower decay | 1–10% of median flux | 0.1–1 d, 1–3 events |
| T2 | Eclipsing/transit dip | trapezoid | 0.1–5% depth | 1–6 h |
| T3 | Periodic variability | sinusoid | 0.5–3% | period 0.5–10 d |
| T4 | Instrumental step | abrupt level offset | 0.2–2% | persists to window end |

### 6.3 Labelling rule
A window is positive iff an injected signal overlaps **>=50%** of the window time span **and** the
injected signal's in-window SNR exceeds a fixed threshold. Injection parameters are written per
window into `ml_benchmark.jsonl`, enabling per-class recall to be reported separately.

### 6.4 Leakage controls
1. Split is **grouped by object** (60/20/20), never by window (H1).
2. An object appears in exactly one split; injected windows cannot cross a split boundary.
3. Positive rate is a controlled parameter (~10% of windows), with sensitivity runs at 5% and 20%.
4. Independent RNG streams derived from a master seed (42) per split, so test injection parameters
   are never visible to tuning.
5. Clean base curves used to generate test negatives are excluded from training.
6. Hyperparameters are selected on validation only; the test split is scored **once**.

### 6.5 Known limitations (to be restated in every Track 1 result)
Injected morphologies are simple and parametric. They do not represent blended eclipsing binaries,
detector glitches, granulation, or other real anomaly classes. Track 1 therefore measures
sensitivity to **these injected classes**, not general "scientifically interesting anomaly" detection.
Because `contamination` fixes an approximate flag rate, precision at the default threshold largely
reflects that setting rather than detection skill (H3).

---

## 7. Track 2 weak-label methodology (specification, not yet executed)

- Positive proxy labels: objects present in published variability catalogues
  (TESS eclipsing-binary catalogue, MAST HLSP `tess-ebs`, DOI `10.17909/t9-9gm4-fx30`;
  Kepler EB catalogue, `keplerEBs.villanova.edu`; published flare catalogues).
- Negative proxy labels: targets with no catalogue match in the queried catalogues.
- **Weak-label caveat, stated everywhere:** catalogue absence is not evidence of normality.
  Coverage is incomplete, cross-match radius introduces error, and class definitions are
  catalogue-specific.
- Evaluation unit is the **object** (was any window flagged?), not the window, because proxy labels
  exist per object. Track 2 metrics are reported in their own section with catalogue version and N.
- Track 2 results are never averaged with Track 1 results.

---

## 8. Limitation register

| ID | Limitation |
|---|---|
| L1 | ML pipeline is orphaned; evaluation calls the modules directly rather than through the API |
| L2 | No real anomaly ground truth exists in the project; Track 1 positives are synthetic |
| L3 | Track 2 labels are weak/proxy, not confirmed |
| L4 | RAG corpus is proposed, not yet approved or ingested; all RAG numbers depend on it |
| L5 | RAG relevance is judged by a single annotator (the agent), so no inter-annotator agreement can be reported; intra-rater re-judgment on a 20% sample will be reported instead |
| L6 | Retrieval quality is measured separately from LLM answer quality; no end-to-end answer-faithfulness metric is claimed |
| L7 | Agent benchmarks require live LLM calls; token accounting depends on provider usage metadata |
| L8 | README currently overstates implemented capability ("labelled subset of known objects", `followupAgent`, 80–120 papers). To be corrected to measured reality, not updated speculatively |

---

## 9. File plan (Part 1 approved item only)

| Action | Path | Purpose |
|---|---|---|
| CREATE | `AIServices/evaluation/AUDIT.md` | This document: audit, decisions, methodology register, limitations |

All Part 2/3/4 files remain proposals pending approval and are listed in the implementation plan.

---

## 10. Gates

| Gate | State |
|---|---|
| Part 1 audit | Conditionally approved |
| Part 1 decisions (ML labels, production-fix separation, reporting) | Approved |
| RAG corpus document list | **AWAITING OWNER APPROVAL — ingestion blocked** |
| Part 2 implementation | **NOT STARTED — awaiting approval** |
