import api from "./api.js";


export const startInvestigation = async (
    candidateId
) => {

    const response = await api.post(
        `/investigations/${candidateId}/analyze`
    );

    return response.data;
};


export const getInvestigations = async () => {

    const response = await api.get(
        "/investigations"
    );

    return response.data;
};


export const getInvestigationById = async (
    investigationId
) => {

    const response = await api.get(
        `/investigations/${investigationId}`
    );

    return response.data;
};


export const getInvestigationStatus = async (
    investigationId
) => {

    const response = await api.get(
        `/investigations/${investigationId}/status`
    );

    return response.data;
};