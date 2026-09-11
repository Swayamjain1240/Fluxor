import os

from dotenv import load_dotenv

from pydantic import (
    BaseModel,
    Field
)

from typing import Literal

from langchain.chat_models import (
    init_chat_model
)

from graph.state import FluxorState


load_dotenv()


class TriageOutput(BaseModel):

    scientificallyInteresting: bool

    priority: Literal[
        "LOW",
        "MEDIUM",
        "HIGH"
    ]

    reason: str

    artifactRisk: float = Field(
        ge=0,
        le=1
    )


_model = None


def getModel():

    global _model

    if _model is None:

        _model = init_chat_model(
            os.getenv(
                "LLM_MODEL",
                "openai:gpt-5.4-mini"
            ),
            temperature=0
        )

    return _model


def triageAgent(
    state: FluxorState
):

    model = getModel()

    structuredModel = (
        model.with_structured_output(
            TriageOutput
        )
    )


    prompt = f"""
You are the Triage Agent inside Fluxor,
an astronomical research-assistance system.

Your job is NOT to claim a discovery.

Decide whether this ML-detected anomaly deserves
deeper scientific investigation.

Candidate:

Object ID:
{state.get("objectId")}

ML anomaly score:
{state.get("anomalyScore")}

Initial ML priority:
{state.get("priority")}

Metadata:
{state.get("metadata", {})}

Consider:

1. How statistically unusual the candidate appears.
2. Whether the signal could plausibly be instrumental noise.
3. Whether deeper catalog/literature investigation is justified.
4. Do not treat anomaly score as scientific confidence.

Return a conservative scientific triage decision.
"""


    result = structuredModel.invoke(
        prompt
    )


    return {

        "triageResult": {
            "scientificallyInteresting":
                result.scientificallyInteresting,

            "priority":
                result.priority,

            "reason":
                result.reason,

            "artifactRisk":
                result.artifactRisk
        },

        "status":
            "triaged"
    }