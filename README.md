<div align="center">

# 🌌 Fluxor

### Agentic AI for Astronomical Transient Discovery & Scientific Investigation

*An AI research assistant that detects anomalies in astronomical data, runs a multi-agent scientific investigation, and generates evidence-based reports — with a human scientist always in the loop.*

[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Node.js](https://img.shields.io/badge/Node.js-Express-339933?logo=node.js&logoColor=white)](https://nodejs.org/)
[![React](https://img.shields.io/badge/React-Vite-61DAFB?logo=react&logoColor=black)](https://react.dev/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-47A248?logo=mongodb&logoColor=white)](https://www.mongodb.com/atlas)
[![LangGraph](https://img.shields.io/badge/LangGraph-Agent%20Orchestration-1C3C3C)](https://langchain-ai.github.io/langgraph/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

[Overview](#-overview) • [Architecture](#-architecture) • [Tech Stack](#-tech-stack) • [Getting Started](#-getting-started) • [API Reference](#-api-reference) • [Roadmap](#-production-roadmap)

</div>

---

## 📖 Overview

Astronomers deal with an overwhelming volume of telescope data — most of it uninteresting, some of it scientifically valuable. **Fluxor** automates the first pass of that triage: it watches for statistical anomalies in astronomical data, and when it finds one worth a closer look, it kicks off a structured, multi-agent scientific investigation — the same way a research team would, just faster.

```
Telescope data  →  ML anomaly detection  →  Multi-agent AI investigation  →  Scientific report  →  Human review
```

This is **not** a chatbot wrapped around space data. It's a workflow automation system built on genuine ML (anomaly detection), genuine information retrieval (RAG over real astronomy literature), and genuine agentic reasoning (a stateful LangGraph pipeline with conditional re-investigation) — with a human scientist making every final call.

> **Terminology note:** Fluxor is designed for **near-real-time astronomical alert intelligence**. The current build processes real astronomical data through **live or replayed alert streams** — see [Current Scope vs. Production](#-production-roadmap) for exactly what's real vs. simulated in this build.

### Why this project exists

- Real observatories (ZTF, TESS, GCN) generate volumes of data no human team can manually review end-to-end.
- Most "AI + astronomy" demos are either pure ML with no reasoning, or a chatbot with no real pipeline behind it.
- Fluxor tries to be neither — it's a small, honest, end-to-end version of how an autonomous discovery pipeline would actually be structured.

---

## ✨ Key Features

- 🔭 **Dual data ingestion paths** — photometric light curves (TESS/Kepler) and real-time-style alerts (ZTF/GCN), each normalized through its own pipeline before merging into a common investigation flow
- 🧠 **ML-based anomaly screening** — Isolation Forest flags statistically unusual light curves before anything expensive (LLM calls) gets triggered
- 🎯 **Triage Agent** — separates "statistically anomalous" from "scientifically interesting," filtering out known artifacts before deeper investigation
- 🕸️ **5-agent LangGraph pipeline** — Triage → Catalog & Historical → Scientific RAG → Hypothesis & Evidence → Follow-up & Report, with **shared state** and a **bounded confidence loop** (re-investigates on low confidence, capped to avoid infinite loops)
- 📚 **Real RAG pipeline** — retrieves evidence from a curated corpus of astronomy papers and NASA documentation via vector search
- 🔬 **Multi-hypothesis reasoning** — generates competing explanations (stellar flare, variable star, transient, instrumental artifact) and weighs supporting/contradicting evidence for each
- 📡 **Follow-up recommendations** — proposes what additional observations would help confirm or refute the leading hypothesis
- 📊 **Built-in evaluation** — ML metrics (precision/recall/F1), RAG retrieval relevance, and agent task-completion tracking, not just a working demo
- ✅ **Human-in-the-loop by design** — every AI conclusion is a recommendation; a scientist approves or rejects before anything is treated as a finding

---

## 🏗 Architecture

```
   TESS / Kepler                          ZTF / GCN
        │                                      │
   Light Curves                       Astronomical Alerts
        │                                      │
  Feature Extraction                  Event Normalization
        │                                      │
  ML Anomaly Detection                 ML / Triage Screening
   (Isolation Forest)                          │
        └──────────────────┬───────────────────┘
                            │
                       Interesting?
                       ╱          ╲
                     No            Yes
                      │              │
                  Archive     LangGraph Orchestrator
                                     │
                              Triage Agent
                       (scientific priority check)
                                     │
                     ┌───────────────┼───────────────┐
                     │                               │
            Catalog & Historical Agent      Scientific RAG Agent
               (SIMBAD / VizieR)              (Chroma + papers)
                     └───────────────┬───────────────┘
                                     │
                     Hypothesis & Evidence Agent
                  (competing hypotheses + evidence weighing)
                                     │
                              Confidence Check
                               ╱            ╲
                             Low            High
                       (max 3 retries)        │
                              │          Follow-up Agent
                       Re-investigate          │
                                        Scientific Report
                                    (structured JSON + Markdown)
                                              │
                                       Scientist Dashboard
                                              │
                                       Approve / Reject
```

### Service architecture

Fluxor is split into three services that communicate over a fixed JSON contract:

```
        React (Vite)
              │
        Express API  ──────►  MongoDB Atlas
              │                (events, anomalies,
       AI_SERVICE_URL           investigations, reports)
              │
     FastAPI + LangGraph
              │
    ┌─────────┼─────────┐
    │         │         │
 Isolation  Chroma   Astroquery
  Forest   (RAG)    (SIMBAD/VizieR)
```

| Service | Responsibility |
|---|---|
| **Client** (React) | Scientist-facing dashboard — candidate list, investigation trace, report review, approve/reject |
| **Server** (Node/Express) | Application layer — datasets, anomalies, reports, validations; calls the AI service and persists results |
| **AI Service** (Python/FastAPI) | The actual science engine — anomaly detection, RAG, and the LangGraph multi-agent pipeline |

---

## 🧰 Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React (Vite), React Router, Axios, Recharts/Plotly.js |
| Backend API | Node.js, Express, Mongoose |
| Application DB | MongoDB Atlas |
| AI Service | Python, FastAPI, Uvicorn |
| Agent Orchestration | LangGraph, LangChain |
| LLM | Claude / GPT-4-class model |
| ML (Anomaly Detection) | scikit-learn (Isolation Forest) |
| Vector Store (RAG) | Chroma |
| Astronomy Data Access | astroquery, lightkurve, astropy |
| Data Sources | NASA MAST (TESS/Kepler), SIMBAD, VizieR, NASA ADS/arXiv, ALeRCE, GCN |

---

## 📁 Project Structure

```
fluxor/
├── client/                  # React frontend
│   ├── src/
│   │   ├── pages/            # Dashboard, Anomaly List, Object Detail
│   │   └── components/
│   └── package.json
│
├── server/                  # Node.js/Express backend
│   ├── models/                # Dataset, Anomaly, Report, Validation
│   ├── routes/                 # /api/datasets, /api/anomalies
│   ├── services/                # aiService.js — calls the AI microservice
│   └── package.json
│
├── ai-service/               # Python FastAPI + LangGraph
│   ├── agents/                  # triage, catalog, rag, hypothesis, followup + graph.py
│   ├── data/                     # loader, normalizer, feature extraction
│   ├── models/                    # anomaly.py (Isolation Forest)
│   ├── rag/                        # corpus, indexer, retriever
│   ├── evaluation/                  # ML / RAG / agent evaluation scripts
│   └── main.py
│
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Node.js 18+
- Python 3.10+
- A MongoDB Atlas connection string (free tier is enough)
- An LLM API key (Claude or OpenAI)

### 1. Clone the repo

```bash
git clone https://github.com/<your-username>/fluxor.git
cd fluxor
```

### 2. AI Service (Python)

```bash
cd ai-service
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env            # add LLM_API_KEY, VECTOR_STORE_PATH
uvicorn main:app --reload --port 8000
```

### 3. Backend (Node.js)

```bash
cd server
npm install

cp .env.example .env            # add MONGODB_URI, AI_SERVICE_URL=http://localhost:8000
npm run dev
```

### 4. Frontend (React)

```bash
cd client
npm install
npm run dev
```

Visit `http://localhost:5173` — you should see the candidate dashboard.

---

## 🔌 API Reference

### Backend (Node/Express)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `POST` | `/api/datasets` | Register a new dataset |
| `GET` | `/api/datasets` | List datasets |
| `POST` | `/api/datasets/:id/detect` | Trigger anomaly detection on a dataset |
| `GET` | `/api/anomalies?datasetId=...` | List anomalies for a dataset |
| `GET` | `/api/anomalies/:objectId` | Get anomaly details + report |
| `GET` | `/api/anomalies/:objectId/lightcurve` | Raw time/flux data for plotting |
| `POST` | `/api/anomalies/:objectId/analyze` | Trigger the AI investigation |
| `POST` | `/api/anomalies/:objectId/validate` | Submit scientist approve/reject decision |

### AI Service (FastAPI)

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Service health check |
| `POST` | `/detect_anomalies` | Run ML screening on a dataset, return ranked anomalies |
| `POST` | `/analyze_object` | Trigger the full LangGraph investigation for one object |

<details>
<summary><strong>Response shape — <code>POST /analyze_object</code></strong></summary>

```json
{
  "catalog_summary": {},
  "hypotheses": [
    {
      "name": "Stellar Flare",
      "confidence": 0.78,
      "supporting_evidence": ["..."],
      "contradicting_evidence": ["..."]
    }
  ],
  "followup_plan": ["..."],
  "report_markdown": "...",
  "status": "completed"
}
```

`status` transitions through `queued → running → completed | failed | needs_review` — investigations aren't instantaneous, so the dashboard polls this to show progress.

</details>

---

## 📊 Evaluation

Fluxor includes a dedicated evaluation layer rather than relying on demo-only validation:

| Layer | Metrics |
|---|---|
| **ML** | Precision, Recall, F1, False Positive Rate (against a labeled subset of known objects) |
| **RAG** | Retrieval relevance and citation correctness against a manual test-query set |
| **Agents** | Investigation completion rate, evidence coverage per hypothesis, invalid-hypothesis rate |

Results are documented in [`ai-service/evaluation/`](ai-service/evaluation/).

---

## 🎯 Current Scope vs. Production Roadmap

Built solo in ~17 days as a portfolio project — scope was intentionally curated for depth over breadth. Here's exactly what's real in this build vs. what a production version would add:

| Component | This build (MVP) | Production version |
|---|---|---|
| Alert ingestion | Replayed archived alerts, async | Live ZTF/GCN via Kafka |
| Anomaly detection | Isolation Forest | + Autoencoder/1D-CNN comparison |
| Vector store | Chroma (local) | Qdrant (clustered) |
| RAG corpus | ~80-120 curated papers | Continuously updated corpus |
| Retrieval | Plain top-k vector search | Cross-encoder reranking |
| Reprocessing | Bounded confidence loop (max 3 retries) | Same, with richer escalation paths |
| Historical analysis | Merged into Catalog Agent | Dedicated agent |

This distinction is intentional — the goal was to build a genuinely working, honestly-scoped system rather than an impressive-sounding one that doesn't run end-to-end.

---

## 🖼 Demo

*(Add screenshots/GIFs of the dashboard, investigation trace, and a sample report here once available)*

*(Add a link to the demo video here)*

---

## 🤝 Contributing

This started as a solo portfolio project, but issues and PRs are welcome — especially around evaluation methodology, additional data source integrations, or agent prompt improvements.

1. Fork the repo
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Open a PR

---

## 📄 License

Distributed under the MIT License. See [`LICENSE`](LICENSE) for details.

---

## 🙏 Acknowledgements

- [NASA MAST](https://mast.stsci.edu/) for TESS/Kepler light curve access
- [SIMBAD](http://simbad.u-strasbg.fr/simbad/) & [VizieR](https://vizier.u-strasbg.fr/) for astronomical catalog data
- [ALeRCE](https://alerce.online/) for historical ZTF alert access
- [GCN](https://gcn.nasa.gov/) for real-time astronomical alert infrastructure
- [LangGraph](https://langchain-ai.github.io/langgraph/) for stateful agent orchestration

---

<div align="center">

*Built to help astronomers spend less time triaging noise and more time on discoveries that matter.*

</div>
