"""Behavioural tests for the agent-result evaluator.

The rule under test: an archived candidate is a finished triage decision, not a
finished investigation, so it must never be counted as completed.
Run: python -m pytest evaluation/tests -q
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

from evaluation.agentEvaluation import (  # noqa: E402
    evaluateAgentResult,
    evaluateAgentRuns,
)


# ---------------------------------------------------------------------------
# Fixtures: the state shapes the graph actually produces
# ---------------------------------------------------------------------------

def archivedResult() -> dict:
    """Exactly what archiveNode returns for a rejected candidate."""

    return {
        "confidence": 0,
        "hypotheses": [],
        "evidence": {},
        "followupPlan": ["No deeper AI investigation recommended at this stage."],
        "reportMarkdown": "# Fluxor Triage Report\n\nCandidate was not escalated.",
        "status": "archived",
    }


def investigatedResult(status: str, confidence: float = 0.9) -> dict:
    """A run that reached finalizeNode."""

    return {
        "confidence": confidence,
        "iterationCount": 2,
        "hypotheses": [
            {
                "name": "Stellar flare",
                "supportingEvidence": ["Rapid flux increase"],
                "contradictingEvidence": [],
            },
            {
                "name": "Variable star",
                "supportingEvidence": ["Photometric variability"],
                "contradictingEvidence": ["No periodic evidence"],
            },
        ],
        "evidence": {
            "catalog": {"simbad": {"found": True}},
            "historical": {},
            "literature": [{"source": "D04.pdf", "page": 3, "content": "text"}],
        },
        "followupPlan": ["Obtain additional photometry"],
        "reportMarkdown": "# Fluxor Scientific Investigation",
        "status": status,
    }


# ---------------------------------------------------------------------------
# Completed flag
# ---------------------------------------------------------------------------

def test_archived_is_not_completed():
    assert evaluateAgentResult(archivedResult())["completed"] is False


def test_completed_is_completed():
    result = evaluateAgentResult(investigatedResult("completed"))
    assert result["completed"] is True


def test_needs_review_is_completed():
    """Low confidence still finishes the investigation, so it counts as done."""

    result = evaluateAgentResult(investigatedResult("needs_review", confidence=0.4))
    assert result["completed"] is True


def test_unknown_status_is_not_completed():
    result = archivedResult()
    result["status"] = "started"
    assert evaluateAgentResult(result)["completed"] is False


# ---------------------------------------------------------------------------
# Score consequences
# ---------------------------------------------------------------------------

def test_archived_does_not_score_as_a_complete_run():
    """Regression: archived used to earn a perfect score on a shortened rubric."""

    archived = evaluateAgentResult(archivedResult())
    assert archived["taskCompletionScore"] < 1.0
    # valid confidence, valid iteration count, report written; `completed` fails.
    assert archived["taskCompletionScore"] == pytest.approx(0.75)


def test_full_investigation_scores_one():
    assert evaluateAgentResult(investigatedResult("completed"))[
        "taskCompletionScore"
    ] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# Aggregate
# ---------------------------------------------------------------------------

def test_completion_rate_excludes_archived_runs():
    summary = evaluateAgentRuns(
        [
            investigatedResult("completed"),
            archivedResult(),
        ]
    )

    assert summary["totalInvestigations"] == 2
    assert summary["completionRate"] == pytest.approx(0.5)
    assert [item["completed"] for item in summary["evaluations"]] == [True, False]


def test_all_archived_run_has_zero_completion_rate():
    summary = evaluateAgentRuns([archivedResult(), archivedResult()])
    assert summary["completionRate"] == pytest.approx(0.0)
