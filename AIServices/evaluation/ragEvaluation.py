from rag.retriever import retrieve_scientific_evidence


def normalizeSource(source):
    """
    Normalize filename/source for comparison.
    """

    if not source:
        return ""

    return str(source).strip().lower()


def evaluateSingleQuery(
    query,
    expectedSources,
    topK=5
):
    """
    Evaluate one RAG query.

    expectedSources:
    List of filenames/documents that are expected
    to be relevant for this query.
    """

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty"
        )

    if not expectedSources:
        raise ValueError(
            "expectedSources cannot be empty"
        )


    # -------------------------
    # Retrieve documents
    # -------------------------

    retrieved = retrieve_scientific_evidence(
        query,
        top_k=topK
    )


    expectedSet = {
        normalizeSource(source)
        for source in expectedSources
    }


    retrievedSources = [
        normalizeSource(
            item.get("source")
        )
        for item in retrieved
        if item.get("source")
    ]


    retrievedSet = set(
        retrievedSources
    )


    # -------------------------
    # Relevant retrieved docs
    # -------------------------

    relevantSources = (
        retrievedSet
        &
        expectedSet
    )


    relevantCount = len(
        relevantSources
    )


    # -------------------------
    # Hit
    # -------------------------

    hit = relevantCount > 0


    # -------------------------
    # Precision
    # -------------------------

    precision = (
        relevantCount
        /
        len(retrievedSet)

        if retrievedSet
        else 0
    )


    # -------------------------
    # Recall
    # -------------------------

    recall = (
        relevantCount
        /
        len(expectedSet)

        if expectedSet
        else 0
    )


    # -------------------------
    # Citation coverage
    # -------------------------

    citationCount = sum(
        1
        for item in retrieved
        if item.get("source")
    )


    citationCoverage = (
        citationCount
        /
        len(retrieved)

        if retrieved
        else 0
    )


    return {
        "query":
            query,

        "expectedSources":
            list(expectedSet),

        "retrievedSources":
            retrievedSources,

        "relevantSources":
            list(relevantSources),

        "hit":
            hit,

        "precision":
            round(
                float(precision),
                4
            ),

        "recall":
            round(
                float(recall),
                4
            ),

        "citationCoverage":
            round(
                float(citationCoverage),
                4
            ),

        "retrievedCount":
            len(retrieved)
    }


def evaluateRag(
    testCases,
    topK=5
):
    """
    Evaluate multiple RAG queries.

    testCases example:

    [
        {
            "query": "...",
            "expectedSources": [
                "paper1.pdf"
            ]
        }
    ]
    """

    if not testCases:
        raise ValueError(
            "RAG test cases cannot be empty"
        )


    results = []


    for testCase in testCases:

        result = evaluateSingleQuery(

            query=
                testCase["query"],

            expectedSources=
                testCase["expectedSources"],

            topK=topK
        )


        results.append(
            result
        )


    # -------------------------
    # Aggregate metrics
    # -------------------------

    hitRate = sum(
        1
        for result in results
        if result["hit"]
    ) / len(results)


    averagePrecision = sum(
        result["precision"]
        for result in results
    ) / len(results)


    averageRecall = sum(
        result["recall"]
        for result in results
    ) / len(results)


    averageCitationCoverage = sum(
        result["citationCoverage"]
        for result in results
    ) / len(results)


    return {
        "totalQueries":
            len(results),

        "topK":
            topK,

        "hitRate":
            round(
                float(hitRate),
                4
            ),

        "averagePrecision":
            round(
                float(averagePrecision),
                4
            ),

        "averageRecall":
            round(
                float(averageRecall),
                4
            ),

        "citationCoverage":
            round(
                float(
                    averageCitationCoverage
                ),
                4
            ),

        "results":
            results
    }


# =========================================
# Manual Test
# =========================================

if __name__ == "__main__":

    testCases = [
        {
            "query":
                "What observational features "
                "are associated with stellar "
                "flares in TESS light curves?",

            "expectedSources": [
                "stellarFlares.pdf"
            ]
        },

        {
            "query":
                "How can instrumental artifacts "
                "appear in photometric light curves?",

            "expectedSources": [
                "tessArtifacts.pdf"
            ]
        }
    ]


    evaluation = evaluateRag(
        testCases,
        topK=5
    )


    print(evaluation)