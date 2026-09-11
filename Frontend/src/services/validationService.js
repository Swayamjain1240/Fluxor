import api from "./api.js";


export const submitValidation = async (
    data
) => {

    const response = await api.post(
        "/validations",
        data
    );

    return response.data;
};


export const getValidations = async () => {

    const response = await api.get(
        "/validations"
    );

    return response.data;
};