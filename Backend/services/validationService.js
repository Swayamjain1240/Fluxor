import ValidationModel from "../models/Validation.js";
import ReportModel from "../models/Report.js";
import InvestigationModel from "../models/Investigation.js";

export const createValidationService =async (userId, validationData) => {

        const {
            reportId,
            decision,
            notes,
        } = validationData;


        if (!reportId || !decision) {

            const error = new Error(
                "Report ID and decision are required"
            );

            error.statusCode = 400;
            throw error;
        }


        if (
            ![
                "approved",
                "rejected",
            ].includes(decision)
        ) {

            const error = new Error(
                "Decision must be approved or rejected"
            );

            error.statusCode = 400;
            throw error;
        }


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
                "You cannot validate this report"
            );

            error.statusCode = 403;
            throw error;
        }


        const existingValidation =
            await ValidationModel.findOne({
                userId,
                reportId,
            });


        if (existingValidation) {

            const error = new Error(
                "Report already validated"
            );

            error.statusCode = 409;
            throw error;
        }


        const validation =
            await ValidationModel.create({

                userId,

                reportId:
                    report._id,

                investigationId:
                    investigation._id,

                candidateId:
                    report.candidateId,

                decision,

                notes:
                    notes || "",
            });


        return validation;
    };

export const getValidationsService = async (userId) => {

        return await ValidationModel.find({
            userId,
        })
        .populate(
            "candidateId",
            "objectId anomalyScore priority"
        )
        .populate(
            "reportId",
            "confidence createdAt"
        )
        .sort({
            createdAt: -1,
        });
    };

export const getValidationByIdService = async (validationId,userId) => {

        const validation =
            await ValidationModel.findOne({
                _id:
                    validationId,

                userId,
            })
            .populate(
                "candidateId"
            )
            .populate(
                "reportId"
            );


        if (!validation) {

            const error = new Error(
                "Validation not found"
            );

            error.statusCode = 404;
            throw error;
        }


        return validation;
    };