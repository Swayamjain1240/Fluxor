import ReportModel from "../models/reportModel.js";
import InvestigationModel from "../models/investigationModel.js";


// CREATE REPORT FROM AI RESULT
export const createReportFromAI = async (
    investigation,
    candidate,
    aiResult
) => {

    const report =
        await ReportModel.create({

            investigationId:
                investigation._id,

            candidateId:
                candidate._id,

            catalogSummary:
                aiResult.catalogSummary ||
                {},

            hypotheses:
                aiResult.hypotheses ||
                [],

            evidence:
                aiResult.evidence ||
                {},

            confidence:
                aiResult.confidence ||
                0,

            followupPlan:
                aiResult.followupPlan ||
                [],

            reportMarkdown:
                aiResult.reportMarkdown ||
                "",
        });


    return report;
};


// GET ALL REPORTS
export const getReportsService = async (
    userId
) => {

    const investigations =
        await InvestigationModel.find({
            userId,
        }).select("_id");


    const investigationIds =
        investigations.map(
            (investigation) =>
                investigation._id
        );


    return await ReportModel.find({
        investigationId: {
            $in: investigationIds,
        },
    })
    .populate(
        "candidateId",
        "objectId anomalyScore priority"
    )
    .sort({
        createdAt: -1,
    });
};


// GET REPORT BY ID
export const getReportByIdService = async (
    reportId,
    userId
) => {

    const report =
        await ReportModel.findById(
            reportId
        );


    if (!report) {

        const error = new Error(
            "Report not found"
        );

        error.statusCode = 404;
        throw error;
    }


    const investigation =
        await InvestigationModel.findOne({
            _id:
                report.investigationId,

            userId,
        });


    if (!investigation) {

        const error = new Error(
            "Report not found"
        );

        error.statusCode = 404;
        throw error;
    }


    return report;
};


// GET REPORT BY INVESTIGATION
export const getReportByInvestigationService =
    async (
        investigationId,
        userId
    ) => {

        const investigation =
            await InvestigationModel.findOne({
                _id: investigationId,
                userId,
            });


        if (!investigation) {

            const error = new Error(
                "Investigation not found"
            );

            error.statusCode = 404;
            throw error;
        }


        const report =
            await ReportModel.findOne({
                investigationId,
            });


        if (!report) {

            const error = new Error(
                "Report not found"
            );

            error.statusCode = 404;
            throw error;
        }


        return report;
    };