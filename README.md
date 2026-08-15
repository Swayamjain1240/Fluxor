# 🌌 Fluxor

### Autonomous Agentic AI Platform for Real-Time Astronomical Event Discovery & Investigation

Fluxor is an **Agentic AI-powered astronomical research platform** designed to help scientists detect, investigate, and prioritize unusual astronomical events from **real-time and near-real-time telescope alerts**.

The system combines **Machine Learning, Deep Learning, LLMs, RAG, LangChain, LangGraph, astronomical data analysis, and scientific reasoning agents** to transform raw astronomical alerts into evidence-based scientific insights and follow-up observation recommendations.

---

## 🚀 Problem

Modern astronomical observatories generate a massive number of observations and transient alerts. Scientists cannot manually investigate every event in real time.

A conventional system may detect:

> "An unusual brightness change has occurred."

But a scientist needs much more:

* Is the event actually unusual?
* Has this object been observed before?
* What could have caused the event?
* Are there similar historical events?
* What does scientific literature say?
* How confident is the classification?
* Should another observation be performed?

**Fluxor automates this initial investigation process while keeping the scientist in the loop.**

---

## 💡 Solution

Fluxor creates an intelligent pipeline:

```text
Real-Time Astronomical Alerts
            ↓
      Alert Ingestion
            ↓
     Data Normalization
            ↓
      ML/DL Screening
            ↓
     Anomaly Detection
            ↓
    Candidate Prioritization
            ↓
      LangGraph Agents
            ↓
 ┌──────────┼───────────┐
 ↓          ↓           ↓
Catalog    RAG      Historical
Agent      Agent     Agent
 └──────────┼───────────┘
            ↓
     Hypothesis Agent
            ↓
      Evidence Agent
            ↓
    Scientific Reasoning
            ↓
   Follow-up Planning Agent
            ↓
    Scientific Research Report
            ↓
       👨‍🔬 Scientist
```

---

# 🔭 Key Features

### 1. Real-Time Astronomical Alerts

Fluxor is designed to consume astronomical transient alerts from sources such as:

* Zwicky Transient Facility (ZTF)
* NASA General Coordinates Network (GCN)
* Other compatible astronomical alert streams

These alerts can contain information such as:

* Object coordinates
* Brightness
* Observation time
* Filters
* Object identifiers
* Event metadata

---

### 2. ML/DL Anomaly Detection

Fluxor analyzes incoming observations and identifies unusual patterns.

Possible techniques include:

* Isolation Forest
* Autoencoders
* Statistical anomaly detection
* Time-series analysis
* 1D CNN-based classification

Example:

```text
Normal brightness:
15.2 → 15.1 → 15.2 → 15.2

Detected:
15.2 → 15.1 → 12.4 → 15.2

Anomaly Score:
96%
```

Only potentially interesting events are passed to the expensive Agentic AI pipeline.

---

### 3. Agentic Investigation

Fluxor uses **LangGraph** to orchestrate specialized AI agents.

The system can dynamically decide what information is required for an investigation instead of following a fixed sequence.

```text
Event
 ↓
Triage
 ↓
Catalog Search
 ↓
Historical Analysis
 ↓
Scientific Literature
 ↓
Hypothesis Generation
 ↓
Evidence Evaluation
 ↓
Follow-up Planning
```

---

### 4. Scientific RAG

Fluxor uses Retrieval-Augmented Generation to ground its reasoning in scientific information.

The knowledge base can contain:

* Astronomy research papers
* NASA documentation
* Scientific reports
* Historical observations
* Astronomical terminology
* Object classifications

The system retrieves relevant information before generating scientific explanations.

---

### 5. Hypothesis Generation

Fluxor does not immediately assume a single explanation.

For example:

```text
Candidate Event

Stellar Flare       → 46%
Variable Star       → 29%
Instrument Artifact → 15%
Other Transient     → 10%
```

Each hypothesis is evaluated using supporting and contradicting evidence.

---

### 6. Evidence-Based Scientific Reasoning

For every conclusion, Fluxor attempts to provide:

* Supporting evidence
* Contradicting evidence
* Relevant observations
* Scientific literature
* Confidence score
* Recommended next investigation

Example:

```text
Hypothesis:
Stellar Flare

Confidence:
78%

Supporting Evidence:
✓ Rapid brightness increase
✓ Short event duration
✓ Historical similarity

Missing Evidence:
⚠ Spectroscopic confirmation
```

---

### 7. Follow-Up Observation Planning

If an event appears scientifically significant, Fluxor generates a follow-up recommendation.

Example:

```text
Priority: HIGH

Recommended observation:
Within 3 hours

Filter:
r-band

Exposure:
120 seconds

Reason:
Rapid brightness evolution requires
additional observations.
```

The system is designed with a **Human-in-the-Loop** approach. Scientists review and approve recommendations before any real-world action.

---

### 8. Scientist Dashboard

The React dashboard provides:

* Live astronomical events
* Candidate priority
* Anomaly scores
* Object information
* Light curves
* AI investigation progress
* Scientific evidence
* Research-paper references
* Hypotheses
* Confidence scores
* Follow-up recommendations

---

# 🧠 Technology Stack

## Artificial Intelligence

* Python
* Machine Learning
* Deep Learning
* LLMs
* LangChain
* LangGraph
* Agentic AI
* Function Calling
* Structured Outputs

## ML/DL

* PyTorch
* Scikit-learn
* NumPy
* Pandas
* SciPy
* Isolation Forest
* Autoencoder
* Time-Series Analysis

## Astronomy

* Astropy
* FITS
* Astronomical coordinates
* Photometry
* Light-curve analysis
* ZTF alerts
* NASA GCN
* TESS / Gaia archival data

## RAG

* Qdrant / Chroma
* Embedding Models
* Semantic Search
* Scientific Literature Retrieval
* Reranking

## Backend

* FastAPI
* PostgreSQL
* Redis
* Apache Kafka

## Frontend

* React
* Vite
* Tailwind CSS
* Recharts / Plotly
* React Flow

## AI Observability

* LangSmith
* Agent tracing
* Evaluation
* LLM monitoring

---

# 🏗️ System Architecture

```text
                         🌌 ASTRONOMICAL OBSERVATORIES
                                      │
                    ┌─────────────────┼─────────────────┐
                    ↓                 ↓                 ↓
                  ZTF                GCN          Other Sources
                    │                 │                 │
                    └─────────────────┼─────────────────┘
                                      ↓
                              ┌──────────────┐
                              │    Kafka     │
                              └──────┬───────┘
                                     ↓
                           ┌──────────────────┐
                           │ Alert Ingestion  │
                           └────────┬─────────┘
                                    ↓
                           ┌──────────────────┐
                           │ Data Normalizer  │
                           └────────┬─────────┘
                                    ↓
                           ┌──────────────────┐
                           │    ML / DL       │
                           │ Anomaly Detector │
                           └────────┬─────────┘
                                    ↓
                              Candidate Event
                                    │
                                    ↓
                         ╔════════════════════╗
                         ║    LANGGRAPH       ║
                         ║ AGENT ORCHESTRATOR  ║
                         ╚══════════╤═════════╝
                                    │
              ┌─────────────────────┼─────────────────────┐
              ↓                     ↓                     ↓
        Catalog Agent          RAG Agent          History Agent
              │                     │                     │
              └─────────────────────┼─────────────────────┘
                                    ↓
                           Hypothesis Agent
                                    ↓
                             Evidence Agent
                                    ↓
                       Scientific Reasoning Agent
                                    ↓
                         Follow-Up Planner
                                    ↓
                         Scientific Report
                                    ↓
                              👨‍🔬 Scientist
```

---

# 📊 Example Workflow

Suppose a telescope alert reports:

```text
Object: ZTF26XXXX
Brightness: 18.9 → 16.1
Change: +2.8 magnitude
```

Fluxor receives the alert and performs:

```text
1. Receive alert
2. Validate data
3. Calculate anomaly score
4. Check historical observations
5. Cross-match astronomical catalogs
6. Search scientific literature
7. Generate possible hypotheses
8. Collect supporting evidence
9. Evaluate confidence
10. Recommend follow-up observation
```

Example result:

```text
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
       FLUXOR INVESTIGATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Object:
ZTF26XXXX

Anomaly Score:
94%

Most Likely:
Stellar Flare

Confidence:
78%

Alternative:
Variable Star — 14%

Evidence:
✓ Rapid brightness increase
✓ Short duration
✓ Similar historical events
✓ Catalog match

Recommendation:
HIGH PRIORITY FOLLOW-UP

Reason:
Additional observation is required
for confirmation.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

# 🔐 Human-in-the-Loop

Fluxor is designed as a **scientist-assistance system**, not a replacement for astronomers.

The AI provides:

```text
Detection
   ↓
Investigation
   ↓
Evidence
   ↓
Hypothesis
   ↓
Recommendation
```

The scientist provides:

```text
Validation
   ↓
Approval / Rejection
   ↓
Scientific Decision
```

This reduces the risk of an LLM making an unsupported scientific claim or automatically taking an irreversible action.

---

# 📁 Proposed Project Structure

```text
fluxor/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── agents/
│   │   ├── astronomy/
│   │   ├── ml/
│   │   ├── rag/
│   │   ├── services/
│   │   ├── models/
│   │   └── core/
│   │
│   ├── tests/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── stores/
│   └── package.json
│
├── data/
│   ├── samples/
│   └── knowledge_base/
│
├── models/
│
├── notebooks/
│
├── docs/
│
├── docker-compose.yml
│
└── README.md
```

---

# 🎯 Project Goals

Fluxor aims to:

1. Detect potentially interesting astronomical events.
2. Reduce the number of events requiring manual inspection.
3. Automatically investigate high-priority candidates.
4. Combine ML with LLM-based scientific reasoning.
5. Ground AI responses using scientific literature.
6. Provide evidence and confidence rather than unsupported predictions.
7. Help scientists prioritize follow-up observations.
8. Keep humans involved in final scientific decisions.

---

# 🛣️ Development Roadmap

### Phase 1 — Data Pipeline

* [ ] Astronomical alert ingestion
* [ ] Alert parser
* [ ] Data normalization
* [ ] PostgreSQL schema
* [ ] Kafka integration

### Phase 2 — ML

* [ ] Feature extraction
* [ ] Anomaly detection
* [ ] Candidate scoring
* [ ] Light-curve analysis

### Phase 3 — RAG

* [ ] Scientific document collection
* [ ] Embedding pipeline
* [ ] Qdrant setup
* [ ] Retrieval
* [ ] Reranking

### Phase 4 — Agentic AI

* [ ] LangGraph state
* [ ] Triage Agent
* [ ] Catalog Agent
* [ ] Historical Analysis Agent
* [ ] RAG Agent
* [ ] Hypothesis Agent
* [ ] Evidence Agent
* [ ] Follow-up Agent

### Phase 5 — Frontend

* [ ] Live event dashboard
* [ ] Candidate explorer
* [ ] Light-curve visualization
* [ ] AI investigation interface
* [ ] Evidence panel
* [ ] Follow-up recommendation UI

### Phase 6 — Evaluation

* [ ] ML evaluation
* [ ] RAG evaluation
* [ ] Agent evaluation
* [ ] Hallucination checks
* [ ] Scientific accuracy analysis
* [ ] LangSmith tracing

---

# ⏱️ Target Timeline

**MVP:** 15–20 days

Approximately:

```text
4–5 hours/day
×
15–20 days
=
60–100 hours
```

The first version should focus on:

```text
ZTF/GCN
   ↓
Alert Processing
   ↓
ML Anomaly Detection
   ↓
LangGraph
   ↓
Scientific RAG
   ↓
Hypothesis + Evidence
   ↓
Follow-up Recommendation
   ↓
Scientist Dashboard
```

Advanced telescope control and complex deep-learning models can be added later.

---

# 🌟 Future Scope

Potential future extensions include:

* Multi-observatory event correlation
* Gravitational-wave event analysis
* Automated telescope scheduling
* Reinforcement-learning observation planning
* Real telescope API integration
* Multi-modal astronomical image analysis
* CNN/ViT-based image classification
* Spectral analysis
* Autonomous scientific experiment planning
* Scientist collaboration
* Event notification system
* Public discovery database

---

# 📚 Scientific Data Sources

Potential data sources include:

* NASA General Coordinates Network (GCN)
* Zwicky Transient Facility (ZTF)
* NASA MAST
* TESS
* Gaia
* Hubble Space Telescope archives
* Public astronomical transient catalogs
* Scientific literature / arXiv

---

# ⚠️ Important Scope Note

Fluxor is a **research prototype and scientific decision-support system**.

AI-generated classifications and recommendations should be treated as **candidate hypotheses**, not confirmed astronomical discoveries.

Final scientific interpretation and observation decisions remain with qualified researchers.

---

# 👨‍💻 Project

**Project Name:** Fluxor
**Category:** Space Science / Astronomy / Agentic AI
**Focus:** Real-Time Astronomical Event Intelligence
**Architecture:** ML + LLM + RAG + Multi-Agent + LangGraph
**Frontend:** React
**Backend:** FastAPI
**Status:** Final-Year Major Project

---

## ⭐ Core Idea

> **Fluxor turns real-time astronomical alerts into actionable scientific intelligence by combining ML-based anomaly detection with Agentic AI, scientific RAG, astronomical data analysis, and human-in-the-loop research workflows.**

**Detect → Investigate → Reason → Validate → Recommend**
