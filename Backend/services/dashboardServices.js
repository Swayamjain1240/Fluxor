import DatasetModel from "../models/datasetModel.js";
import CandidateModel from "../models/candidateModel.js";
import InvestigationModel from "../models/investigationModel.js";
import ValidationModel from "../models/validationModel.js";



export const getDashboardSummaryService =async (userId) => {

        
        const datasets =
            await DatasetModel.find({
                userId,
            }).select("_id");


        const datasetIds =
            datasets.map(
                (dataset) =>
                    dataset._id
            );


        const [
            candidateCount,
            highPriorityCount,
            investigationCount,
            approvedCount,
            rejectedCount,
        ] = await Promise.all([

            CandidateModel.countDocuments({
                datasetId: {
                    $in: datasetIds,
                },
            }),

            CandidateModel.countDocuments({
                datasetId: {
                    $in: datasetIds,
                },

                priority: "HIGH",
            }),

            InvestigationModel.countDocuments({
                userId,
            }),

            ValidationModel.countDocuments({
                userId,
                decision: "approved",
            }),

            ValidationModel.countDocuments({
                userId,
                decision: "rejected",
            }),
        ]);


        return {
            datasets:
                datasets.length,

            candidates:
                candidateCount,

            highPriority:
                highPriorityCount,

            investigations:
                investigationCount,

            approved:
                approvedCount,

            rejected:
                rejectedCount,
        };
    };

export const getRecentActivityService =async (userId) => {

        const recentInvestigations =
            await InvestigationModel.find({
                userId,
            })
                .populate(
                    "candidateId",
                    "objectId anomalyScore priority"
                )
                .sort({
                    createdAt: -1,
                })
                .limit(5);


        const recentValidations =
            await ValidationModel.find({
                userId,
            })
                .populate(
                    "candidateId",
                    "objectId anomalyScore priority"
                )
                .sort({
                    createdAt: -1,
                })
                .limit(5);


        return {
            recentInvestigations,
            recentValidations,
        };
    };