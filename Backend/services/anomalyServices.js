import DatasetModel from "../models/Dataset.js";
import CandidateModel from "../models/Candidate.js";

import {
    detectAnomaliesAI,
} from "./ai.service.js";


// RUN ANOMALY DETECTION
export const detectAnomaliesService = async (
    datasetId,
    userId
) => {

    const dataset =
        await DatasetModel.findOne({
            _id: datasetId,
            userId,
        });


    if (!dataset) {

        const error = new Error(
            "Dataset not found"
        );

        error.statusCode = 404;
        throw error;
    }


    try {

        dataset.status = "processing";

        await dataset.save();


        // Call Python ML service
        const aiResult =
            await detectAnomaliesAI(
                dataset
            );


        const candidatesData =
            aiResult.candidates || [];


        const candidates = [];


        for (const item of candidatesData) {

            const candidate =
                await CandidateModel.create({

                    datasetId:
                        dataset._id,

                    objectId:
                        item.objectId,

                    anomalyScore:
                        item.anomalyScore,

                    priority:
                        item.priority ||
                        "LOW",

                    metadata:
                        item.metadata || {},

                    lightCurve:
                        item.lightCurve || [],

                    status:
                        "detected",
                });


            candidates.push(
                candidate
            );
        }


        dataset.status = "completed";

        await dataset.save();


        return candidates;

    } catch (error) {

        dataset.status = "failed";

        await dataset.save();

        throw error;
    }
};


// GET ALL CANDIDATES OF USER
export const getCandidatesService = async (
    userId
) => {

    const datasets =
        await DatasetModel.find({
            userId,
        }).select("_id");


    const datasetIds =
        datasets.map(
            (dataset) =>
                dataset._id
        );


    const candidates =
        await CandidateModel.find({
            datasetId: {
                $in: datasetIds,
            },
        })
        .populate(
            "datasetId",
            "name source objectId"
        )
        .sort({
            anomalyScore: -1,
        });


    return candidates;
};


// GET SINGLE CANDIDATE
export const getCandidateByIdService = async (
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


    const dataset =
        await DatasetModel.findOne({
            _id: candidate.datasetId,
            userId,
        });


    if (!dataset) {

        const error = new Error(
            "Candidate not found"
        );

        error.statusCode = 404;
        throw error;
    }


    return candidate;
};


// GET LIGHT CURVE
export const getCandidateLightCurveService =
    async (
        candidateId,
        userId
    ) => {

        const candidate =
            await getCandidateByIdService(
                candidateId,
                userId
            );


        return {
            candidateId:
                candidate._id,

            objectId:
                candidate.objectId,

            lightCurve:
                candidate.lightCurve,
        };
    };