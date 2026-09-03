const AI_SERVICE_URL =
    process.env.AI_SERVICE_URL ||
    "http://localhost:8000";


// COMMON REQUEST FUNCTION
const callAIService = async (
    endpoint,
    body
) => {

    const response = await fetch(
        `${AI_SERVICE_URL}${endpoint}`,
        {
            method: "POST",

            headers: {
                "Content-Type":
                    "application/json",
            },

            body: JSON.stringify(body),
        }
    );


    if (!response.ok) {

        let message =
            "AI service request failed";

        try {

            const errorData =
                await response.json();

            message =
                errorData.detail ||
                errorData.message ||
                message;

        } catch (error) {
            // response wasn't JSON
        }


        const serviceError =
            new Error(message);

        serviceError.statusCode =
            response.status;

        throw serviceError;
    }


    return await response.json();
};


// ML ANOMALY DETECTION
export const detectAnomaliesAI = async (
    dataset
) => {

    return await callAIService(
        "/detect_anomalies",
        {
            datasetId:
                dataset._id.toString(),

            source:
                dataset.source,

            objectId:
                dataset.objectId,
        }
    );
};


// LANGGRAPH INVESTIGATION
export const analyzeCandidateAI = async (
    candidate
) => {

    return await callAIService(
        "/analyze_object",
        {
            candidateId:
                candidate._id.toString(),

            objectId:
                candidate.objectId,

            anomalyScore:
                candidate.anomalyScore,

            priority:
                candidate.priority,

            metadata:
                candidate.metadata,

            lightCurve:
                candidate.lightCurve,
        }
    );
};