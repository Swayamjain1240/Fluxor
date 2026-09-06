import os
from typing import Any
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field

load_dotenv()

app=FastAPI(
    title=os.getenv(
        "APP_NAME",
        "Fluxor AI Service"
    ),
    description=(
        "ML, RAG and Agentic AI service "
        "for astronomical investigation."
    ),
    version="1.0.0"
)

class DetectAnomalyRequest(BaseModel):
    datasetId: str
    source: str
    objectId: str


class LightCurvePoint(BaseModel):
    time: float
    flux: float


class AnalyzeObjectRequest(BaseModel):
    candidateId: str
    objectId: str

    anomalyScore: float = Field(
        ge=0,
        le=1
    )

    priority: str

    metadata: dict[str, Any] = Field(
        default_factory=dict
    )

    lightCurve: list[LightCurvePoint] = Field(
        default_factory=list
    )

@app.get("/health")
async def health():

    return {
        "success": True,
        "service": "Fluxor AI Service",
        "status": "running"
    }


@app.post("/detect_anomalies")
async def detect_anomalies(
    request: DetectAnomalyRequest
):

    # Placeholder
    # Real ML pipeline comes in Part 2

    return {
        "success": True,
        "message": (
            "Anomaly detection endpoint working"
        ),
        "datasetId": request.datasetId,
        "source": request.source,
        "objectId": request.objectId,
        "candidates": []
    }

@app.post("/analyze_object")
async def analyze_object(
    request: AnalyzeObjectRequest
):

    # Placeholder
    # Real LangGraph workflow comes in Part 4

    return {
        "success": True,

        "candidateId":
            request.candidateId,

        "objectId":
            request.objectId,

        "iterationCount": 0,

        "confidence": 0,

        "catalogSummary": {},

        "hypotheses": [],

        "evidence": {},

        "followupPlan": [],

        "reportMarkdown":
            "Agentic investigation is not implemented yet."
    }