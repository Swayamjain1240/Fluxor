import api from "./api.js";


export const getReports = async () => {

    const response = await api.get(
        "/reports"
    );

    return response.data;
};


export const getReportById = async (
    reportId
) => {

    const response = await api.get(
        `/reports/${reportId}`
    );

    return response.data;
};


export const getReportByInvestigation = async (
    investigationId
) => {

    const response = await api.get(
        `/reports/investigation/${investigationId}`
    );

    return response.data;
};