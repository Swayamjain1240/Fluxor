import {
    getReportsService,
    getReportByIdService,
    getReportByInvestigationService,
} from "../services/reportServices.js";


// GET ALL REPORTS
export const getReports = async (
    req,
    res
) => {
    try {

        const reports =
            await getReportsService(
                req.user.userId
            );


        return res.status(200).json({
            success: true,
            count: reports.length,
            reports,
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


// GET REPORT BY ID
export const getReportById = async (
    req,
    res
) => {
    try {

        const report =
            await getReportByIdService(
                req.params.reportId,
                req.user.userId
            );


        return res.status(200).json({
            success: true,
            report,
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


// GET REPORT USING INVESTIGATION ID
export const getReportByInvestigation =
    async (req, res) => {

        try {

            const report =
                await getReportByInvestigationService(
                    req.params
                        .investigationId,

                    req.user.userId
                );


            return res.status(200).json({
                success: true,
                report,
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