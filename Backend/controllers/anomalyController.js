import {
    detectAnomaliesService,
    getCandidatesService,
    getCandidateByIdService,
    getCandidateLightCurveService,
} from "../services/anomalyServices.js";


// DETECT ANOMALIES
export const detectAnomalies = async (
    req,
    res
) => {
    try {

        const candidates =
            await detectAnomaliesService(
                req.params.datasetId,
                req.user.userId
            );


        return res.status(200).json({
            success: true,
            message:
                "Anomaly detection completed",
            count: candidates.length,
            candidates,
        });

    } catch (error) {

        return res.status(
            error.statusCode || 500
        ).json({
            success: false,
            message:
                error.message ||
                "Anomaly detection failed",
        });
    }
};


// GET ALL CANDIDATES
export const getCandidates = async (
    req,
    res
) => {
    try {

        const candidates =
            await getCandidatesService(
                req.user.userId
            );


        return res.status(200).json({
            success: true,
            count: candidates.length,
            candidates,
        });

    } catch (error) {

        return res.status(
            error.statusCode || 500
        ).json({
            success: false,
            message:
                error.message ||
                "Internal server error",
        });
    }
};


// GET SINGLE CANDIDATE
export const getCandidateById = async (
    req,
    res
) => {
    try {

        const candidate =
            await getCandidateByIdService(
                req.params.candidateId,
                req.user.userId
            );


        return res.status(200).json({
            success: true,
            candidate,
        });

    } catch (error) {

        return res.status(
            error.statusCode || 500
        ).json({
            success: false,
            message:
                error.message ||
                "Internal server error",
        });
    }
};


// GET LIGHT CURVE
export const getCandidateLightCurve =
    async (req, res) => {

        try {

            const data =
                await getCandidateLightCurveService(
                    req.params.candidateId,
                    req.user.userId
                );


            return res.status(200).json({
                success: true,
                data,
            });

        } catch (error) {

            return res.status(
                error.statusCode || 500
            ).json({
                success: false,
                message:
                    error.message ||
                    "Internal server error",
            });
        }
    };