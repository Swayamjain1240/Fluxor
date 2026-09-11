from graph.state import FluxorState

from rag.retriever import (
    retrieve_scientific_evidence
)


def buildRagQuery(
    state: FluxorState
):

    objectId = state.get(
        "objectId"
    )

    triage = state.get(
        "triageResult",
        {}
    )

    history = state.get(
        "historicalData",
        {}
    )

    hypotheses = state.get(
        "hypotheses",
        []
    )

    iteration = state.get(
        "iterationCount",
        0
    )


    query = f"""
Astronomical interpretation of an unusual
photometric light curve.

Object: {objectId}

Triage:
{triage}

Historical observations:
{history}

Relevant topics:

stellar flare,
variable star,
astronomical transient,
instrumental artifact,
photometric variability,
TESS or Kepler light curves.
"""


    # Re-investigation:
    # search around previous hypotheses

    if (
        iteration > 0
        and
        hypotheses
    ):

        hypothesisNames = [
            item.get(
                "name",
                ""
            )
            for item in hypotheses
        ]


        query += f"""

Previous hypotheses:
{hypothesisNames}

Find evidence that can CONFIRM OR REFUTE these
hypotheses, especially distinguishing observations.
"""


    return query


def ragAgent(
    state: FluxorState
):

    query = buildRagQuery(
        state
    )


    evidence = (
        retrieve_scientific_evidence(
            query,
            top_k=5
        )
    )


    return {

        "ragQuery":
            query,

        "ragEvidence":
            evidence,

        "status":
            "rag_complete"
    }