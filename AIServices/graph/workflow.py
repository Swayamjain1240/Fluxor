import os

from dotenv import load_dotenv

from typing import Literal

from langgraph.graph import (
    StateGraph,
    START,
    END
)

from graph.state import (
    FluxorState
)

from agents.triageAgent import (
    triageAgent
)

from agents.catalogAgent import (
    catalogAgent
)

from agents.historicalAgent import (
    historicalAgent
)

from agents.ragAgent import (
    ragAgent
)

from agents.reasoningAgent import (
    reasoningAgent
)


load_dotenv()


CONFIDENCE_THRESHOLD = float(
    os.getenv(
        "CONFIDENCE_THRESHOLD",
        "0.72"
    )
)


MAX_ITERATIONS = int(
    os.getenv(
        "MAX_ITERATIONS",
        "3"
    )
)


# ========================================
# TRIAGE ROUTER
# ========================================

def routeAfterTriage(
    state: FluxorState
) -> Literal[
    "catalogAgent",
    "archive"
]:

    triage = state.get(
        "triageResult",
        {}
    )


    if triage.get(
        "scientificallyInteresting",
        False
    ):

        return "catalogAgent"


    return "archive"


# ========================================
# CONFIDENCE ROUTER
# ========================================

def routeAfterReasoning(
    state: FluxorState
) -> Literal[
    "ragAgent",
    "finalize"
]:

    confidence = state.get(
        "confidence",
        0
    )

    iteration = state.get(
        "iterationCount",
        0
    )


    # Enough evidence
    if confidence >= CONFIDENCE_THRESHOLD:

        return "finalize"


    # Safety: never loop forever
    if iteration >= MAX_ITERATIONS:

        return "finalize"


    # Re-investigate using a more targeted
    # RAG query based on previous hypotheses
    return "ragAgent"


# ========================================
# ARCHIVE NODE
# ========================================

def archiveNode(
    state: FluxorState
):

    triage = state.get(
        "triageResult",
        {}
    )


    reason = triage.get(
        "reason",
        "Candidate did not pass scientific triage."
    )


    return {

        "confidence": 0,

        "hypotheses": [],

        "evidence": {},

        "followupPlan": [
            "No deeper AI investigation recommended at this stage."
        ],

        "reportMarkdown": f"""
# Fluxor Triage Report

## Result

Candidate was not escalated for deeper investigation.

## Reason

{reason}

## Important

This decision is an automated triage recommendation
and can be reviewed by a scientist.
""",

        "status":
            "archived"
    }


# ========================================
# FINALIZE NODE
# ========================================

def finalizeNode(
    state: FluxorState
):

    confidence = state.get(
        "confidence",
        0
    )


    if confidence >= CONFIDENCE_THRESHOLD:

        status = "completed"

    else:

        status = "needs_review"


    return {
        "status": status
    }


# ========================================
# BUILD LANGGRAPH
# ========================================

workflow = StateGraph(
    FluxorState
)


# Nodes

workflow.add_node(
    "triageAgent",
    triageAgent
)

workflow.add_node(
    "catalogAgent",
    catalogAgent
)

workflow.add_node(
    "historicalAgent",
    historicalAgent
)

workflow.add_node(
    "ragAgent",
    ragAgent
)

workflow.add_node(
    "reasoningAgent",
    reasoningAgent
)

workflow.add_node(
    "archive",
    archiveNode
)

workflow.add_node(
    "finalize",
    finalizeNode
)


# ========================================
# EDGES
# ========================================

workflow.add_edge(
    START,
    "triageAgent"
)


workflow.add_conditional_edges(
    "triageAgent",
    routeAfterTriage
)


workflow.add_edge(
    "catalogAgent",
    "historicalAgent"
)


workflow.add_edge(
    "historicalAgent",
    "ragAgent"
)


workflow.add_edge(
    "ragAgent",
    "reasoningAgent"
)


workflow.add_conditional_edges(
    "reasoningAgent",
    routeAfterReasoning
)


workflow.add_edge(
    "archive",
    END
)


workflow.add_edge(
    "finalize",
    END
)


# Compile graph

fluxorWorkflow = (
    workflow.compile()
)