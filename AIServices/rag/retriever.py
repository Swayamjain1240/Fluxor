from rag.vectorstore import (
    get_vectorstore
)


def retrieve_scientific_evidence(
    query: str,
    top_k: int = 5
):

    if not query.strip():

        raise ValueError(
            "Retrieval query cannot be empty"
        )


    vectorstore = (
        get_vectorstore()
    )


    results = (
        vectorstore.similarity_search_with_score(
            query,
            k=top_k
        )
    )


    evidence = []


    for document, score in results:

        evidence.append({

            "content":
                document.page_content,

            "source":
                document.metadata.get(
                    "source"
                ),

            "page":
                document.metadata.get(
                    "page"
                ),

            "startIndex":
                document.metadata.get(
                    "start_index"
                ),

            "distance":
                float(score)
        })


    return evidence