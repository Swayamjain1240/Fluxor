import CandidateModel from "../models/Candidate.js";
import DatasetModel from "../models/Dataset.js";
import InvestigationModel from "../models/Investigation.js";

import {
    analyzeCandidateAI,
} from "./ai.service.js";

import {
    createReportFromAI,
} from "./report.service.js";


export const startInvestigationService = async (
    candidateId,
    userId
) => {

    const candidate =
        await CandidateModel.findById(
            candidateId
        );


    if (!candidate) {

        const error = new Error(
            "Candidate not found"
        );

        error.statusCode = 404;
        throw error;
    }


    // Verify candidate belongs to user
    const dataset =
        await DatasetModel.findOne({
            _id:
                candidate.datasetId,

            userId,
        });


    if (!dataset) {

        const error = new Error(
            "Candidate not found"
        );

        error.statusCode = 404;
        throw error;
    }


    const investigation =
        await InvestigationModel.create({

            candidateId:
                candidate._id,

            userId,

            status:
                "running",

            currentStep:
                "starting",

            startedAt:
                new Date(),
        });


    candidate.status = "running";

    await candidate.save();


    try {

        // Python LangGraph
        const aiResult =
            await analyzeCandidateAI(
                candidate
            );


        investigation.status =
            "completed";

        investigation.currentStep =
            "completed";

        investigation.iterationCount =
            aiResult.iterationCount || 1;

        investigation.confidence =
            aiResult.confidence || 0;

        investigation.completedAt =
            new Date();


        await investigation.save();


        candidate.status =
            "completed";

        await candidate.save();


        // Generate MongoDB report
        const report =
            await createReportFromAI(
                investigation,
                candidate,
                aiResult
            );


        return {
            investigation,
            report,
        };


    } catch (error) {

        investigation.status =
            "failed";

        investigation.currentStep =
            "failed";

        investigation.errorMessage =
            error.message;

        investigation.completedAt =
            new Date();


        await investigation.save();


        candidate.status =
            "failed";

        await candidate.save();


        throw error;
    }
};



export const getInvestigationsService =async (userId) => {

        return await InvestigationModel.find({
            userId,
        })
        .populate(
            "candidateId",
            "objectId anomalyScore priority"
        )
        .sort({
            createdAt: -1,
        });
    };

export const getInvestigationByIdService =async (investigationId,userId) => {

        const investigation =
            await InvestigationModel.findOne({
                _id:
                    investigationId,

                userId,
            })
            .populate(
                "candidateId"
            );


        if (!investigation) {

            const error = new Error(
                "Investigation not found"
            );

            error.statusCode = 404;
            throw error;
        }


        return investigation;
    };


export const getInvestigationStatusService =async (investigationId,userId) => {

        const investigation =
            await InvestigationModel.findOne({
                _id:
                    investigationId,

                userId,
            }).select(
                "status currentStep confidence iterationCount errorMessage"
            );


        if (!investigation) {

            const error = new Error(
                "Investigation not found"
            );

            error.statusCode = 404;
            throw error;
        }


        return investigation;
    };