import os
from typing import Any
from dotenv import load_dotenv
from fastapi import FastAPI
from pydantic import BaseModel, Field
from graph.workflow import (
    fluxorWorkflow
)

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
def analyze_object(
    request: AnalyzeObjectRequest
):

    try:

        initialState = {

            "candidateId":
                request.candidateId,

            "objectId":
                request.objectId,

            "anomalyScore":
                request.anomalyScore,

            "priority":
                request.priority,

            "metadata":
                request.metadata,

            "lightCurve": [

                point.model_dump()

                for point
                in request.lightCurve
            ],

            "iterationCount": 0,

            "hypotheses": [],

            "ragEvidence": [],

            "confidence": 0,

            "status":
                "started"
        }


        result = (
            fluxorWorkflow.invoke(
                initialState
            )
        )


        return {

            "success":
                True,

            "candidateId":
                request.candidateId,

            "objectId":
                request.objectId,

            "status":
                result.get(
                    "status"
                ),

            "triageResult":
                result.get(
                    "triageResult",
                    {}
                ),

            "iterationCount":
                result.get(
                    "iterationCount",
                    0
                ),

            "confidence":
                result.get(
                    "confidence",
                    0
                ),

            "catalogSummary":
                result.get(
                    "catalogData",
                    {}
                ),

            "hypotheses":
                result.get(
                    "hypotheses",
                    []
                ),

            "evidence":
                result.get(
                    "evidence",
                    {}
                ),

            "followupPlan":
                result.get(
                    "followupPlan",
                    []
                ),

            "reportMarkdown":
                result.get(
                    "reportMarkdown",
                    ""
                )
        }


    except Exception as error:

        raise HTTPException(
            status_code=500,
            detail=(
                "Agent investigation failed: "
                + str(error)
            )
        )