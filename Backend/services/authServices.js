import jwt from "jsonwebtoken";
import bcrypt from "bcrypt";
import { randomUUID } from "crypto";

import UserModel from "../models/userModel.js";


const generateAccessToken = (userId) => {
    return jwt.sign(
        {
            userId,
        },
        process.env.ACCESS_TOKEN_SECRET,
        {
            expiresIn:
                process.env.ACCESS_TOKEN_EXPIRES_IN || "15m",
        }
    );
};


const generateRefreshToken = (userId) => {
    return jwt.sign(
        {
            userId,
        },
        process.env.REFRESH_TOKEN_SECRET,
        {
            expiresIn:
                process.env.REFRESH_TOKEN_EXPIRES_IN || "7d",

            // Makes every refresh token different
            jwtid: randomUUID(),
        }
    );
};


// REGISTER
export const registerUser = async ({
    name,
    email,
    password,
}) => {

    if (!name || !email || !password) {
        const error = new Error(
            "Name, email and password are required"
        );

        error.statusCode = 400;
        throw error;
    }

    const normalizedEmail =
        email.toLowerCase().trim();

    const existingUser = await UserModel.findOne({
        email: normalizedEmail,
    });

    if (existingUser) {
        const error = new Error(
            "User already exists"
        );

        error.statusCode = 409;
        throw error;
    }


    // Password will be hashed automatically
    // by UserModel pre("save") middleware
    const user = await UserModel.create({
        name: name.trim(),
        email: normalizedEmail,
        password,
    });


    return {
        id: user._id,
        name: user.name,
        email: user.email,
    };
};


// LOGIN
export const loginUser = async ({
    email,
    password,
}) => {

    if (!email || !password) {
        const error = new Error(
            "Email and password are required"
        );

        error.statusCode = 400;
        throw error;
    }


    const user = await UserModel.findOne({
        email: email.toLowerCase().trim(),
    });


    if (!user) {
        const error = new Error(
            "Invalid email or password"
        );

        error.statusCode = 401;
        throw error;
    }


    const isPasswordCorrect =
        await user.comparePassword(password);


    if (!isPasswordCorrect) {
        const error = new Error(
            "Invalid email or password"
        );

        error.statusCode = 401;
        throw error;
    }


    const accessToken =
        generateAccessToken(
            user._id.toString()
        );


    const refreshToken =
        generateRefreshToken(
            user._id.toString()
        );


    // Don't store raw refresh token
    user.refreshTokenHash =
        await bcrypt.hash(
            refreshToken,
            10
        );


    await user.save();


    return {
        user: {
            id: user._id,
            name: user.name,
            email: user.email,
        },

        accessToken,
        refreshToken,
    };
};


// REFRESH ACCESS TOKEN
export const refreshAccessToken = async (
    refreshToken
) => {

    if (!refreshToken) {
        const error = new Error(
            "Refresh token required"
        );

        error.statusCode = 401;
        throw error;
    }


    let decoded;

    try {

        decoded = jwt.verify(
            refreshToken,
            process.env.REFRESH_TOKEN_SECRET
        );

    } catch (error) {

        const tokenError = new Error(
            "Invalid or expired refresh token"
        );

        tokenError.statusCode = 401;
        throw tokenError;
    }


    const user =
        await UserModel.findById(
            decoded.userId
        );


    if (!user || !user.refreshTokenHash) {

        const error = new Error(
            "Refresh token not found"
        );

        error.statusCode = 401;
        throw error;
    }


    const tokenMatch =
        await bcrypt.compare(
            refreshToken,
            user.refreshTokenHash
        );


    if (!tokenMatch) {

        const error = new Error(
            "Invalid refresh token"
        );

        error.statusCode = 401;
        throw error;
    }


    const newAccessToken =
        generateAccessToken(
            user._id.toString()
        );


    const newRefreshToken =
        generateRefreshToken(
            user._id.toString()
        );


    // Refresh-token rotation
    user.refreshTokenHash =
        await bcrypt.hash(
            newRefreshToken,
            10
        );


    await user.save();


    return {
        accessToken: newAccessToken,
        refreshToken: newRefreshToken,
    };
};


// LOGOUT
export const logoutUser = async (
    refreshToken
) => {

    if (!refreshToken) {
        return;
    }


    try {

        const decoded = jwt.verify(
            refreshToken,
            process.env.REFRESH_TOKEN_SECRET
        );


        const user =
            await UserModel.findById(
                decoded.userId
            );


        if (!user || !user.refreshTokenHash) {
            return;
        }


        const tokenMatch =
            await bcrypt.compare(
                refreshToken,
                user.refreshTokenHash
            );


        if (tokenMatch) {

            user.refreshTokenHash = null;

            await user.save();
        }

    } catch (error) {

        // Even invalid token should not
        // prevent client logout
        return;
    }
};


// CURRENT USER
export const getCurrentUser = async (
    userId
) => {

    const user =
        await UserModel.findById(
            userId
        ).select(
            "-password -refreshTokenHash"
        );


    if (!user) {
        const error = new Error(
            "User not found"
        );

        error.statusCode = 404;
        throw error;
    }


    return user;
};