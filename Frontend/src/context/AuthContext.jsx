import {
    createContext,
    useEffect,
    useState
} from "react";

import {
    loginUser,
    logoutUser,
    refreshToken,
    getCurrentUser
} from "../services/authService.js";

import {
    setAccessToken
} from "../services/api.js";


export const AuthContext = createContext(null);


export const AuthProvider = ({ children }) => {

    const [user, setUser] =
        useState(null);

    const [loading, setLoading] =
        useState(true);


    const login = async (
        email,
        password
    ) => {

        const data = await loginUser({
            email,
            password
        });


        setAccessToken(
            data.accessToken
        );


        setUser(
            data.user
        );


        return data;
    };



    const logout = async () => {

        try {

            await logoutUser();

        } finally {

            setAccessToken(null);

            setUser(null);
        }
    };


    const restoreSession = async () => {

        try {

            const tokenData =
                await refreshToken();


            setAccessToken(
                tokenData.accessToken
            );


            const userData =
                await getCurrentUser();


            setUser(
                userData.user
            );

        } catch (error) {

            setAccessToken(null);

            setUser(null);

        } finally {

            setLoading(false);
        }
    };


    useEffect(() => {

        restoreSession();

    }, []);


    return (

        <AuthContext.Provider
            value={{
                user,
                loading,
                login,
                logout,
                isAuthenticated:
                    Boolean(user)
            }}
        >

            {children}

        </AuthContext.Provider>
    );
};