import {
    registerUser,
    loginUser,
    logoutUser,
    refreshAccessToken,
    getCurrentUser,
} from "../services/authServices.js";


const cookieOptions = {
    httpOnly: true,
    secure: process.env.NODE_ENV === "production",
    sameSite: "strict",
    maxAge: 7 * 24 * 60 * 60 * 1000,
};


// SIGNUP
export const Signup = async (req, res) => {
    try {

        const user = await registerUser(req.body);

        return res.status(201).json({
            success: true,
            message: "Account created successfully",
            user,
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


// LOGIN
export const Login = async (req, res) => {
    try {

        const {
            user,
            accessToken,
            refreshToken,
        } = await loginUser(req.body);


        res.cookie(
            "refreshToken",
            refreshToken,
            cookieOptions
        );


        return res.status(200).json({
            success: true,
            message: "Login successful",
            accessToken,
            user,
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


// REFRESH TOKEN
export const Refresh = async (req, res) => {
    try {

        const refreshToken =
            req.cookies.refreshToken;


        const tokens =
            await refreshAccessToken(
                refreshToken
            );


        res.cookie(
            "refreshToken",
            tokens.refreshToken,
            cookieOptions
        );


        return res.status(200).json({
            success: true,
            accessToken:
                tokens.accessToken,
        });

    } catch (error) {

        return res.status(
            error.statusCode || 401
        ).json({
            success: false,
            message:
                error.message ||
                "Unable to refresh token",
        });
    }
};


// LOGOUT
export const Logout = async (req, res) => {
    try {

        const refreshToken =
            req.cookies.refreshToken;


        await logoutUser(
            refreshToken
        );


        res.clearCookie(
            "refreshToken",
            cookieOptions
        );


        return res.status(200).json({
            success: true,
            message: "Logout successful",
        });

    } catch (error) {

        return res.status(500).json({
            success: false,
            message:
                "Internal server error",
        });
    }
};


// CURRENT USER
export const me = async (req, res) => {
    try {

        const user =
            await getCurrentUser(
                req.user.userId
            );


        return res.status(200).json({
            success: true,
            user,
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