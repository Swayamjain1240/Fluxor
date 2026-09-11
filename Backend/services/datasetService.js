import DatasetModel from "../models/datasetModel.js";


// CREATE DATASET
export const createDatasetService = async (
    userId,
    datasetData
) => {

    const {
        name,
        description,
        source,
        objectId,
    } = datasetData;


    if (!name || !source || !objectId) {

        const error = new Error(
            "Name, source and objectId are required"
        );

        error.statusCode = 400;
        throw error;
    }


    const dataset =
        await DatasetModel.create({
            userId,
            name,
            description:
                description || "",
            source,
            objectId,
            status: "created",
        });


    return dataset;
};


// GET USER DATASETS
export const getDatasetsService = async (
    userId
) => {

    const datasets =
        await DatasetModel.find({
            userId,
        })
        .sort({
            createdAt: -1,
        });


    return datasets;
};


// GET SINGLE DATASET
export const getDatasetByIdService = async (
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


    return dataset;
};


// DELETE DATASET
export const deleteDatasetService = async (
    datasetId,
    userId
) => {

    const dataset =
        await DatasetModel.findOneAndDelete({
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


    return dataset;
};