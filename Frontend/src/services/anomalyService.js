import api from "./api.js";


export const detectAnomalies = async (datasetId) => {

    const response = await api.post(
        `/anomalies/datasets/${datasetId}/detect`
    );

    return response.data;
};


export const getCandidates = async () => {

    const response = await api.get(
        "/anomalies"
    );

    return response.data;
};


export const getCandidateById = async (candidateId) => {

    const response = await api.get(
        `/anomalies/${candidateId}`
    );

    return response.data;
};


export const getCandidateLightCurve = async (candidateId) => {

    const response = await api.get(
        `/anomalies/${candidateId}/lightcurve`
    );

    return response.data;
};