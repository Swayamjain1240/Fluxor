import os
import json

from dotenv import load_dotenv

from pydantic import (
    BaseModel,
    Field
)

from langchain.chat_models import (
    init_chat_model
)

from graph.state import FluxorState


load_dotenv()


class Hypothesis(BaseModel):

    name: str

    explanation: str

    supportingEvidence: list[str]

    contradictingEvidence: list[str]

    confidence: float = Field(
        ge=0,
        le=1
    )


class ReasoningOutput(BaseModel):

    hypotheses: list[Hypothesis]

    confidence: float = Field(
        ge=0,
        le=1
    )

    followupPlan: list[str]

    reportMarkdown: str


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


def reasoningAgent(
    state: FluxorState
):

    model = getModel()


    structuredModel = (
        model.with_structured_output(
            ReasoningOutput
        )
    )


    iteration = state.get(
        "iterationCount",
        0
    )


    prompt = f"""
You are Fluxor's scientific reasoning agent.

You are assisting an astronomer.

You MUST remain evidence-grounded and conservative.

You are NOT allowed to claim a new astronomical
discovery.

ML anomaly score represents statistical unusualness,
NOT scientific confidence.

────────────────────────────

OBJECT

Object ID:
{state.get("objectId")}

ML anomaly score:
{state.get("anomalyScore")}

ML priority:
{state.get("priority")}

Metadata:
{json.dumps(
    state.get("metadata", {}),
    default=str
)}

────────────────────────────

TRIAGE RESULT

{json.dumps(
    state.get("triageResult", {}),
    default=str
)}

────────────────────────────

CATALOG DATA

{json.dumps(
    state.get("catalogData", {}),
    default=str
)}

────────────────────────────

HISTORICAL DATA

{json.dumps(
    state.get("historicalData", {}),
    default=str
)}

────────────────────────────

RETRIEVED SCIENTIFIC LITERATURE

{json.dumps(
    state.get("ragEvidence", []),
    default=str
)}

────────────────────────────

PREVIOUS HYPOTHESES

{json.dumps(
    state.get("hypotheses", []),
    default=str
)}

Current investigation iteration:
{iteration + 1}

────────────────────────────

TASK

Generate multiple competing explanations where
scientifically reasonable.

Examples may include:

- stellar flare
- variable star
- transient event
- eclipsing system
- instrumental artifact

Do NOT force these hypotheses if evidence does not
support them.

For every hypothesis:

1. Explain it.
2. List supporting evidence.
3. List contradicting evidence.
4. Assign hypothesis confidence.

Then calculate an OVERALL investigation confidence.

Confidence must be LOW when:

- evidence is missing,
- catalog information is unavailable,
- literature does not support conclusions,
- multiple explanations remain equally plausible.

Provide observations that would help distinguish
between the leading hypotheses.

Your reportMarkdown must clearly state:

- this is an AI-assisted investigation,
- anomaly score is not discovery probability,
- final scientific interpretation requires human review.

Use only information supplied above.
Do not invent catalog records, observations,
citations, measurements, or papers.
"""


    result = structuredModel.invoke(
        prompt
    )


    hypothesisList = [

        item.model_dump()

        for item in result.hypotheses
    ]


    evidence = {

        "catalog":
            state.get(
                "catalogData",
                {}
            ),

        "historical":
            state.get(
                "historicalData",
                {}
            ),

        "literature":
            state.get(
                "ragEvidence",
                []
            )
    }


    return {

        "hypotheses":
            hypothesisList,

        "evidence":
            evidence,

        "confidence":
            result.confidence,

        "followupPlan":
            result.followupPlan,

        "reportMarkdown":
            result.reportMarkdown,

        "iterationCount":
            iteration + 1,

        "status":
            "reasoning_complete"
    }