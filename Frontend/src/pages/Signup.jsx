import {
    useState
} from "react";

import {
    Link,
    useNavigate
} from "react-router-dom";

import {
    signupUser
} from "../services/authService.js";


const Signup = () => {

    const navigate =
        useNavigate();


    const [
        form,
        setForm
    ] = useState({
        name: "",
        email: "",
        password: ""
    });


    const [
        error,
        setError
    ] = useState("");


    const [
        loading,
        setLoading
    ] = useState(false);


    const handleChange = (
        event
    ) => {

        setForm({
            ...form,

            [event.target.name]:
                event.target.value
        });
    };


    const handleSubmit = async (
        event
    ) => {

        event.preventDefault();

        setError("");

        setLoading(true);


        try {

            await signupUser(
                form
            );


            navigate(
                "/login"
            );

        } catch (error) {

            setError(
                error.response
                    ?.data
                    ?.message
                ||
                "Signup failed"
            );

        } finally {

            setLoading(false);
        }
    };


    return (

        <div
            style={{
                position: "fixed",

                inset: 0,

                minHeight: "100vh",

                display: "flex",

                alignItems: "center",

                justifyContent: "center",

                background:
                    "linear-gradient(135deg, #070a10 0%, #0b1019 55%, #101725 100%)",

                color: "#ffffff",

                fontFamily:
                    "Inter, Arial, sans-serif",

                padding: "20px",

                boxSizing: "border-box"
            }}
        >

            {/* Background Glow */}

            <div
                style={{
                    position: "absolute",

                    width: "420px",

                    height: "420px",

                    borderRadius: "50%",

                    background:
                        "rgba(73, 118, 255, 0.08)",

                    filter:
                        "blur(100px)",

                    top: "-100px",

                    right: "-80px",

                    pointerEvents: "none"
                }}
            />


            <div
                style={{
                    width: "100%",

                    maxWidth: "410px",

                    padding: "38px",

                    background:
                        "rgba(15, 20, 29, 0.96)",

                    border:
                        "1px solid #252d3a",

                    borderRadius:
                        "16px",

                    boxShadow:
                        "0 20px 60px rgba(0, 0, 0, 0.45)",

                    position:
                        "relative",

                    zIndex: 1,

                    boxSizing:
                        "border-box"
                }}
            >

                {/* Brand */}

                <div
                    style={{
                        marginBottom:
                            "32px"
                    }}
                >

                    <h1
                        style={{
                            margin:
                                "0 0 6px",

                            fontSize:
                                "30px",

                            letterSpacing:
                                "4px",

                            color:
                                "#ffffff"
                        }}
                    >

                        FLUXOR

                    </h1>


                    <p
                        style={{
                            margin: 0,

                            color:
                                "#788398",

                            fontSize:
                                "12px",

                            letterSpacing:
                                "0.8px"
                        }}
                    >

                        AGENTIC ASTRONOMICAL INTELLIGENCE

                    </p>

                </div>


                {/* Heading */}

                <div
                    style={{
                        marginBottom:
                            "26px"
                    }}
                >

                    <h2
                        style={{
                            margin:
                                "0 0 8px",

                            fontSize:
                                "23px",

                            color:
                                "#f5f7fa"
                        }}
                    >

                        Create Scientist Account

                    </h2>


                    <p
                        style={{
                            margin: 0,

                            color:
                                "#8993a5",

                            fontSize:
                                "14px",

                            lineHeight:
                                "1.6"
                        }}
                    >

                        Create your Fluxor research workspace account.

                    </p>

                </div>


                {/* Error */}

                {error && (

                    <div
                        style={{
                            padding:
                                "12px 14px",

                            marginBottom:
                                "18px",

                            background:
                                "rgba(220, 60, 60, 0.12)",

                            border:
                                "1px solid rgba(220, 60, 60, 0.3)",

                            borderRadius:
                                "8px",

                            color:
                                "#ff8c8c",

                            fontSize:
                                "13px"
                        }}
                    >

                        {error}

                    </div>

                )}


                {/* Form */}

                <form
                    onSubmit={
                        handleSubmit
                    }

                    style={{
                        display:
                            "flex",

                        flexDirection:
                            "column",

                        gap:
                            "17px"
                    }}
                >

                    {/* Name */}

                    <div>

                        <label
                            style={{
                                display:
                                    "block",

                                marginBottom:
                                    "7px",

                                color:
                                    "#aab3c1",

                                fontSize:
                                    "13px",

                                fontWeight:
                                    "600"
                            }}
                        >

                            Name

                        </label>


                        <input
                            type="text"

                            name="name"

                            value={
                                form.name
                            }

                            onChange={
                                handleChange
                            }

                            placeholder="Your name"

                            autoComplete="name"

                            required

                            style={{
                                width:
                                    "100%",

                                padding:
                                    "13px 14px",

                                background:
                                    "#0b1018",

                                border:
                                    "1px solid #303947",

                                borderRadius:
                                    "8px",

                                color:
                                    "#ffffff",

                                outline:
                                    "none",

                                fontSize:
                                    "14px",

                                boxSizing:
                                    "border-box"
                            }}
                        />

                    </div>


                    {/* Email */}

                    <div>

                        <label
                            style={{
                                display:
                                    "block",

                                marginBottom:
                                    "7px",

                                color:
                                    "#aab3c1",

                                fontSize:
                                    "13px",

                                fontWeight:
                                    "600"
                            }}
                        >

                            Email

                        </label>


                        <input
                            type="email"

                            name="email"

                            value={
                                form.email
                            }

                            onChange={
                                handleChange
                            }

                            placeholder="scientist@example.com"

                            autoComplete="email"

                            required

                            style={{
                                width:
                                    "100%",

                                padding:
                                    "13px 14px",

                                background:
                                    "#0b1018",

                                border:
                                    "1px solid #303947",

                                borderRadius:
                                    "8px",

                                color:
                                    "#ffffff",

                                outline:
                                    "none",

                                fontSize:
                                    "14px",

                                boxSizing:
                                    "border-box"
                            }}
                        />

                    </div>


                    {/* Password */}

                    <div>

                        <label
                            style={{
                                display:
                                    "block",

                                marginBottom:
                                    "7px",

                                color:
                                    "#aab3c1",

                                fontSize:
                                    "13px",

                                fontWeight:
                                    "600"
                            }}
                        >

                            Password

                        </label>


                        <input
                            type="password"

                            name="password"

                            value={
                                form.password
                            }

                            onChange={
                                handleChange
                            }

                            placeholder="Create a password"

                            autoComplete="new-password"

                            required

                            style={{
                                width:
                                    "100%",

                                padding:
                                    "13px 14px",

                                background:
                                    "#0b1018",

                                border:
                                    "1px solid #303947",

                                borderRadius:
                                    "8px",

                                color:
                                    "#ffffff",

                                outline:
                                    "none",

                                fontSize:
                                    "14px",

                                boxSizing:
                                    "border-box"
                            }}
                        />

                    </div>


                    {/* Signup Button */}

                    <button
                        type="submit"

                        disabled={
                            loading
                        }

                        style={{
                            width:
                                "100%",

                            padding:
                                "13px",

                            marginTop:
                                "5px",

                            border:
                                "none",

                            borderRadius:
                                "8px",

                            background:
                                loading
                                    ? "#343c49"
                                    : "#f4f6f8",

                            color:
                                loading
                                    ? "#9199a7"
                                    : "#0b1018",

                            fontWeight:
                                "700",

                            fontSize:
                                "14px",

                            cursor:
                                loading
                                    ? "not-allowed"
                                    : "pointer"
                        }}
                    >

                        {
                            loading
                                ? "Creating Account..."
                                : "Create Account"
                        }

                    </button>

                </form>


                {/* Login Link */}

                <p
                    style={{
                        margin:
                            "24px 0 0",

                        textAlign:
                            "center",

                        color:
                            "#8993a5",

                        fontSize:
                            "13px"
                    }}
                >

                    Already have an account?{" "}

                    <Link
                        to="/login"

                        style={{
                            color:
                                "#9bc9ff",

                            textDecoration:
                                "none",

                            fontWeight:
                                "600"
                        }}
                    >

                        Login

                    </Link>

                </p>


                {/* Footer */}

                <div
                    style={{
                        marginTop:
                            "28px",

                        paddingTop:
                            "18px",

                        borderTop:
                            "1px solid #242b36",

                        textAlign:
                            "center",

                        color:
                            "#596273",

                        fontSize:
                            "11px"
                    }}
                >

                    Fluxor Scientific Intelligence Platform

                </div>

            </div>

        </div>
    );
};


export default Signup;