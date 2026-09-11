import api from "./api.js";


export const createDataset = async (data) => {

    const response = await api.post(
        "/datasets",
        data
    );

    return response.data;
};


export const getDatasets = async () => {

    const response = await api.get(
        "/datasets"
    );

    return response.data;
};


export const getDatasetById = async (
    datasetId
) => {

    const response = await api.get(
        `/datasets/${datasetId}`
    );

    return response.data;
};


export const deleteDataset = async (
    datasetId
) => {

    const response = await api.delete(
        `/datasets/${datasetId}`
    );

    return response.data;
};