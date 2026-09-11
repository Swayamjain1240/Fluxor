from typing import Any
from typing_extensions import TypedDict


class FluxorState(TypedDict, total=False):

    # Candidate
    candidateId: str
    objectId: str

    anomalyScore: float
    priority: str

    metadata: dict[str, Any]
    lightCurve: list[dict[str, float]]


    # Triage
    triageResult: dict[str, Any]


    # Scientific context
    catalogData: dict[str, Any]

    historicalData: dict[str, Any]

    ragEvidence: list[dict[str, Any]]

    ragQuery: str


    # Scientific reasoning
    hypotheses: list[dict[str, Any]]

    evidence: dict[str, Any]

    confidence: float


    # Confidence loop
    iterationCount: int


    # Final output
    followupPlan: list[str]

    reportMarkdown: str

    status: str