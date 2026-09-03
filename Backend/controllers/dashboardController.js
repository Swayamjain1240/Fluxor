import {
    getDashboardSummaryService,
    getRecentActivityService
} from "../services/dashboardServices.js";


// DASHBOARD SUMMARY
export const getDashboardSummary =
    async (req, res) => {

        try {

            const summary =
                await getDashboardSummaryService(
                    req.user.userId
                );


            return res.status(200).json({
                success: true,
                summary
            });

        } catch (error) {

            return res.status(error.statusCode || 500).json({
                success: false,
                message:
                    error.message ||
                    "Internal server error"
            });
        }
    };


// RECENT ACTIVITY
export const getRecentActivity =
    async (req, res) => {

        try {

            const activity =
                await getRecentActivityService(
                    req.user.userId
                );


            return res.status(200).json({
                success: true,
                activity
            });

        } catch (error) {

            return res.status(error.statusCode || 500).json({
                success: false,
                message:
                    error.message ||
                    "Internal server error"
            });
        }
    };