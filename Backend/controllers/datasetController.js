import {
    createDatasetService,
    getDatasetsService,
    getDatasetByIdService,
    deleteDatasetService,
} from "../services/datasetService.js";


// CREATE DATASET
export const createDataset = async (
    req,
    res
) => {
    try {

        const dataset =
            await createDatasetService(
                req.user.userId,
                req.body
            );


        return res.status(201).json({
            success: true,
            message:
                "Dataset created successfully",
            dataset,
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


// GET ALL DATASETS
export const getDatasets = async (
    req,
    res
) => {
    try {

        const datasets =
            await getDatasetsService(
                req.user.userId
            );


        return res.status(200).json({
            success: true,
            count: datasets.length,
            datasets,
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


// GET SINGLE DATASET
export const getDatasetById = async (
    req,
    res
) => {
    try {

        const dataset =
            await getDatasetByIdService(
                req.params.datasetId,
                req.user.userId
            );


        return res.status(200).json({
            success: true,
            dataset,
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


// DELETE DATASET
export const deleteDataset = async (
    req,
    res
) => {
    try {

        await deleteDatasetService(
            req.params.datasetId,
            req.user.userId
        );


        return res.status(200).json({
            success: true,
            message:
                "Dataset deleted successfully",
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