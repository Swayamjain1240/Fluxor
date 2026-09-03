import {
    startInvestigationService,
    getInvestigationsService,
    getInvestigationByIdService,
    getInvestigationStatusService,
} from "../services/investigationService.js";


// START INVESTIGATION
export const startInvestigation = async (
    req,
    res
) => {
    try {

        const result =
            await startInvestigationService(
                req.params.candidateId,
                req.user.userId
            );


        return res.status(201).json({
            success: true,
            message:
                "Investigation completed successfully",
            investigation:
                result.investigation,
            report:
                result.report,
        });

    } catch (error) {

        return res.status(
            error.statusCode || 500
        ).json({
            success: false,
            message:
                error.message ||
                "Investigation failed",
        });
    }
};


// GET ALL INVESTIGATIONS
export const getInvestigations =
    async (req, res) => {

        try {

            const investigations =
                await getInvestigationsService(
                    req.user.userId
                );


            return res.status(200).json({
                success: true,
                count:
                    investigations.length,
                investigations,
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


// GET SINGLE INVESTIGATION
export const getInvestigationById =
    async (req, res) => {

        try {

            const investigation =
                await getInvestigationByIdService(
                    req.params
                        .investigationId,

                    req.user.userId
                );


            return res.status(200).json({
                success: true,
                investigation,
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


// GET INVESTIGATION STATUS
export const getInvestigationStatus =
    async (req, res) => {

        try {

            const status =
                await getInvestigationStatusService(
                    req.params
                        .investigationId,

                    req.user.userId
                );


            return res.status(200).json({
                success: true,
                status,
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