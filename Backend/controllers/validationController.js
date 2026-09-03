import {
    createValidationService,
    getValidationsService,
    getValidationByIdService
} from "../services/validationService.js";


// CREATE VALIDATION
export const createValidation = async (req, res) => {
    try {

        const validation =
            await createValidationService(
                req.user.userId,
                req.body
            );


        return res.status(201).json({
            success: true,
            message: "Validation submitted successfully",
            validation
        });

    } catch (error) {

        return res.status(error.statusCode || 500).json({
            success: false,
            message: error.message || "Internal server error"
        });
    }
};


// GET ALL VALIDATIONS
export const getValidations = async (req, res) => {
    try {

        const validations =
            await getValidationsService(
                req.user.userId
            );


        return res.status(200).json({
            success: true,
            count: validations.length,
            validations
        });

    } catch (error) {

        return res.status(error.statusCode || 500).json({
            success: false,
            message: error.message || "Internal server error"
        });
    }
};


// GET SINGLE VALIDATION
export const getValidationById =
    async (req, res) => {

        try {

            const validation =
                await getValidationByIdService(
                    req.params.validationId,
                    req.user.userId
                );


            return res.status(200).json({
                success: true,
                validation
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