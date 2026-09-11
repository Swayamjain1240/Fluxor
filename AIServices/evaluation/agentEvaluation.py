MAX_ITERATIONS = 3


def normalizeText(value):

    if value is None:
        return ""

    return str(value).strip().lower()


def evaluateAgentResult(
    result,
    invalidHypotheses=None
):
    """
    Evaluate one Fluxor LangGraph result.
    """

    if not isinstance(result, dict):
        raise ValueError(
            "Agent result must be a dictionary"
        )


    if invalidHypotheses is None:
        invalidHypotheses = []


    # =====================================
    # 1. Investigation status
    # =====================================

    status = result.get(
        "status",
        ""
    )


    completed = status in [
        "completed",
        "needs_review",
        "archived"
    ]


    # =====================================
    # 2. Hypotheses
    # =====================================

    hypotheses = result.get(
        "hypotheses",
        []
    )


    if not isinstance(
        hypotheses,
        list
    ):
        hypotheses = []


    hypothesisCount = len(
        hypotheses
    )


    hypothesisGenerated = (
        hypothesisCount > 0
    )


    # =====================================
    # 3. Evidence coverage
    # =====================================

    hypothesesWithEvidence = 0

    totalSupportingEvidence = 0

    totalContradictingEvidence = 0


    for hypothesis in hypotheses:

        supporting = (
            hypothesis.get(
                "supportingEvidence",
                []
            )
            or []
        )


        contradicting = (
            hypothesis.get(
                "contradictingEvidence",
                []
            )
            or []
        )


        totalSupportingEvidence += len(
            supporting
        )


        totalContradictingEvidence += len(
            contradicting
        )


        if supporting or contradicting:

            hypothesesWithEvidence += 1


    evidenceCoverage = (
        hypothesesWithEvidence
        /
        hypothesisCount

        if hypothesisCount > 0
        else 0
    )


    # =====================================
    # 4. Invalid hypotheses
    # =====================================

    invalidSet = {
        normalizeText(item)
        for item in invalidHypotheses
    }


    invalidCount = 0


    for hypothesis in hypotheses:

        hypothesisName = normalizeText(
            hypothesis.get(
                "name"
            )
        )


        if hypothesisName in invalidSet:

            invalidCount += 1


    invalidHypothesisRate = (
        invalidCount
        /
        hypothesisCount

        if hypothesisCount > 0
        else 0
    )


    # =====================================
    # 5. Confidence
    # =====================================

    confidence = result.get(
        "confidence",
        0
    )


    validConfidence = (
        isinstance(
            confidence,
            (int, float)
        )
        and
        0 <= confidence <= 1
    )


    # =====================================
    # 6. Iteration safety
    # =====================================

    iterationCount = result.get(
        "iterationCount",
        0
    )


    validIterationCount = (
        isinstance(
            iterationCount,
            int
        )
        and
        0 <= iterationCount <= MAX_ITERATIONS
    )


    # =====================================
    # 7. Report
    # =====================================

    reportMarkdown = result.get(
        "reportMarkdown",
        ""
    )


    reportGenerated = bool(
        isinstance(
            reportMarkdown,
            str
        )
        and
        reportMarkdown.strip()
    )


    # =====================================
    # 8. Follow-up
    # =====================================

    followupPlan = result.get(
        "followupPlan",
        []
    )


    followupGenerated = (
        isinstance(
            followupPlan,
            list
        )
        and
        len(followupPlan) > 0
    )


    # =====================================
    # 9. RAG evidence
    # =====================================

    evidence = result.get(
        "evidence",
        {}
    )


    literatureEvidence = []


    if isinstance(
        evidence,
        dict
    ):

        literatureEvidence = (
            evidence.get(
                "literature",
                []
            )
            or []
        )


    ragEvidencePresent = (
        len(literatureEvidence) > 0
    )


    # =====================================
    # 10. Catalog evidence
    # =====================================

    catalogEvidence = {}


    if isinstance(
        evidence,
        dict
    ):

        catalogEvidence = (
            evidence.get(
                "catalog",
                {}
            )
            or {}
        )


    catalogEvidencePresent = bool(
        catalogEvidence
    )


    # =====================================
    # Overall task-completion score
    # =====================================

    checks = [
        completed,
        validConfidence,
        validIterationCount,
        reportGenerated
    ]


    # Archived candidates don't require
    # hypotheses / RAG / follow-up.

    if status != "archived":

        checks.extend([
            hypothesisGenerated,
            evidenceCoverage > 0,
            ragEvidencePresent,
            followupGenerated
        ])


    taskCompletionScore = (
        sum(
            1
            for check in checks
            if check
        )
        /
        len(checks)
    )


    return {
        "status":
            status,

        "completed":
            completed,

        "taskCompletionScore":
            round(
                float(taskCompletionScore),
                4
            ),

        "hypothesisCount":
            hypothesisCount,

        "hypothesisGenerated":
            hypothesisGenerated,

        "evidenceCoverage":
            round(
                float(evidenceCoverage),
                4
            ),

        "supportingEvidenceCount":
            totalSupportingEvidence,

        "contradictingEvidenceCount":
            totalContradictingEvidence,

        "invalidHypothesisCount":
            invalidCount,

        "invalidHypothesisRate":
            round(
                float(
                    invalidHypothesisRate
                ),
                4
            ),

        "confidence":
            confidence,

        "validConfidence":
            validConfidence,

        "iterationCount":
            iterationCount,

        "iterationLimitRespected":
            validIterationCount,

        "ragEvidencePresent":
            ragEvidencePresent,

        "catalogEvidencePresent":
            catalogEvidencePresent,

        "reportGenerated":
            reportGenerated,

        "followupGenerated":
            followupGenerated
    }


def evaluateAgentRuns(
    results,
    invalidHypotheses=None
):
    """
    Evaluate multiple Fluxor investigations.
    """

    if not results:
        raise ValueError(
            "Agent results cannot be empty"
        )


    evaluations = [
        evaluateAgentResult(
            result,
            invalidHypotheses
        )

        for result in results
    ]


    total = len(
        evaluations
    )


    # =====================================
    # Completion Rate
    # =====================================

    completionRate = sum(
        1
        for result in evaluations
        if result["completed"]
    ) / total


    # =====================================
    # Average Task Completion
    # =====================================

    averageTaskCompletion = sum(
        result[
            "taskCompletionScore"
        ]
        for result in evaluations
    ) / total


    # =====================================
    # Average evidence coverage
    # =====================================

    averageEvidenceCoverage = sum(
        result[
            "evidenceCoverage"
        ]
        for result in evaluations
    ) / total


    # =====================================
    # Invalid hypothesis rate
    # =====================================

    totalHypotheses = sum(
        result[
            "hypothesisCount"
        ]
        for result in evaluations
    )


    totalInvalidHypotheses = sum(
        result[
            "invalidHypothesisCount"
        ]
        for result in evaluations
    )


    invalidHypothesisRate = (
        totalInvalidHypotheses
        /
        totalHypotheses

        if totalHypotheses > 0
        else 0
    )


    # =====================================
    # Report generation rate
    # =====================================

    reportGenerationRate = sum(
        1
        for result in evaluations
        if result[
            "reportGenerated"
        ]
    ) / total


    # =====================================
    # Iteration safety rate
    # =====================================

    iterationSafetyRate = sum(
        1
        for result in evaluations
        if result[
            "iterationLimitRespected"
        ]
    ) / total


    return {
        "totalInvestigations":
            total,

        "completionRate":
            round(
                float(completionRate),
                4
            ),

        "averageTaskCompletion":
            round(
                float(
                    averageTaskCompletion
                ),
                4
            ),

        "averageEvidenceCoverage":
            round(
                float(
                    averageEvidenceCoverage
                ),
                4
            ),

        "invalidHypothesisRate":
            round(
                float(
                    invalidHypothesisRate
                ),
                4
            ),

        "reportGenerationRate":
            round(
                float(
                    reportGenerationRate
                ),
                4
            ),

        "iterationSafetyRate":
            round(
                float(
                    iterationSafetyRate
                ),
                4
            ),

        "evaluations":
            evaluations
    }


# =========================================
# Manual Test
# =========================================

if __name__ == "__main__":

    sampleResult = {

        "status":
            "completed",

        "iterationCount":
            2,

        "confidence":
            0.81,

        "hypotheses": [
            {
                "name":
                    "Stellar flare",

                "supportingEvidence": [
                    "Rapid flux increase",
                    "Literature evidence"
                ],

                "contradictingEvidence": [
                    "Duration is slightly unusual"
                ]
            },

            {
                "name":
                    "Variable star",

                "supportingEvidence": [
                    "Photometric variability"
                ],

                "contradictingEvidence": [
                    "No strong periodic evidence"
                ]
            }
        ],

        "evidence": {

            "catalog": {
                "simbad": {
                    "found": True
                }
            },

            "historical": {},

            "literature": [
                {
                    "source":
                        "stellarFlares.pdf",

                    "content":
                        "Example evidence"
                }
            ]
        },

        "followupPlan": [
            "Obtain additional photometry"
        ],

        "reportMarkdown":
            "# Fluxor Scientific Investigation"
    }


    result = evaluateAgentResult(
        sampleResult
    )


    print(result)