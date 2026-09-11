import {
    useEffect,
    useState
} from "react";

import {
    Link
} from "react-router-dom";

import {
    getInvestigations
} from "../services/investigationService.js";

import Loader from "../components/Loader.jsx";

import InvestigationStatus from "../components/investigation/InvestigationStatus.jsx";


const Investigations = () => {

    const [
        investigations,
        setInvestigations
    ] = useState([]);


    const [
        loading,
        setLoading
    ] = useState(true);


    const [
        error,
        setError
    ] = useState("");


    useEffect(() => {

        const loadInvestigations = async () => {

            try {

                setError("");


                const data =
                    await getInvestigations();


                console.log(
                    "Investigations response:",
                    data
                );


                setInvestigations(
                    data.investigations
                    ||
                    []
                );

            } catch (error) {

                console.error(
                    "Investigation loading error:",
                    error
                );


                setError(
                    error.response
                        ?.data
                        ?.message
                    ||
                    "Failed to load investigations"
                );

            } finally {

                setLoading(false);
            }
        };


        loadInvestigations();

    }, []);


    if (loading) {

        return (

            <Loader
                text="Loading investigations..."
            />

        );
    }


    return (

        <div
            style={{
                width: "100%"
            }}
        >

            <div
                style={{
                    marginBottom: "28px"
                }}
            >

                <p
                    style={{
                        margin: "0 0 7px",
                        color: "#7f8999",
                        fontSize: "12px",
                        textTransform: "uppercase",
                        letterSpacing: "1px"
                    }}
                >

                    Agentic AI Research

                </p>


                <h1
                    style={{
                        margin: "0 0 8px",
                        color: "#ffffff"
                    }}
                >

                    Investigations

                </h1>


                <p
                    style={{
                        margin: 0,
                        color: "#8992a3",
                        lineHeight: "1.6"
                    }}
                >

                    Scientific investigations performed by Fluxor's
                    multi-agent reasoning system.

                </p>

            </div>


            {error && (

                <div
                    style={{
                        padding: "14px",
                        marginBottom: "20px",
                        background:
                            "rgba(220, 60, 60, 0.15)",
                        border:
                            "1px solid rgba(220, 60, 60, 0.3)",
                        borderRadius: "8px",
                        color: "#ff8989"
                    }}
                >

                    {error}

                </div>

            )}


            {
                investigations.length === 0
                    ? (

                        <div
                            style={{
                                padding: "50px",
                                textAlign: "center",
                                background: "#11151d",
                                border:
                                    "1px solid #272d39",
                                borderRadius: "12px"
                            }}
                        >

                            <h3
                                style={{
                                    margin: "0 0 10px",
                                    color: "#ffffff"
                                }}
                            >

                                No investigations yet

                            </h3>


                            <p
                                style={{
                                    margin: 0,
                                    color: "#8992a3"
                                }}
                            >

                                Analyze an anomaly candidate to start
                                your first scientific investigation.

                            </p>

                        </div>

                    )
                    : (

                        <div
                            style={{
                                display: "grid",
                                gap: "14px"
                            }}
                        >

                            {
                                investigations.map(
                                    (investigation) => (

                                        <div
                                            key={
                                                investigation._id
                                            }

                                            style={{
                                                display: "flex",
                                                justifyContent:
                                                    "space-between",
                                                alignItems:
                                                    "center",
                                                gap: "20px",
                                                flexWrap: "wrap",
                                                padding: "22px",
                                                background:
                                                    "#11151d",
                                                border:
                                                    "1px solid #272d39",
                                                borderRadius:
                                                    "10px"
                                            }}
                                        >

                                            <div>

                                                <p
                                                    style={{
                                                        margin:
                                                            "0 0 7px",
                                                        color:
                                                            "#7f8999",
                                                        fontSize:
                                                            "12px",
                                                        textTransform:
                                                            "uppercase"
                                                    }}
                                                >

                                                    Astronomical Candidate

                                                </p>


                                                <h3
                                                    style={{
                                                        margin:
                                                            "0 0 9px",
                                                        color:
                                                            "#ffffff"
                                                    }}
                                                >

                                                    {
                                                        investigation.objectId
                                                        ||
                                                        investigation
                                                            ?.candidateId
                                                            ?.objectId
                                                        ||
                                                        "Unknown Object"
                                                    }

                                                </h3>


                                                <div
                                                    style={{
                                                        display: "flex",
                                                        gap: "14px",
                                                        flexWrap: "wrap",
                                                        color:
                                                            "#8992a3",
                                                        fontSize:
                                                            "13px"
                                                    }}
                                                >

                                                    <span>

                                                        Confidence:{" "}

                                                        <strong
                                                            style={{
                                                                color:
                                                                    "#ffffff"
                                                            }}
                                                        >

                                                            {
                                                                Math.round(
                                                                    (
                                                                        investigation.confidence
                                                                        ||
                                                                        0
                                                                    )
                                                                    *
                                                                    100
                                                                )
                                                            }
                                                            %

                                                        </strong>

                                                    </span>


                                                    <span>

                                                        Iterations:{" "}

                                                        <strong
                                                            style={{
                                                                color:
                                                                    "#ffffff"
                                                            }}
                                                        >

                                                            {
                                                                investigation.iterationCount
                                                                ||
                                                                0
                                                            }
                                                            /3

                                                        </strong>

                                                    </span>

                                                </div>

                                            </div>


                                            <div
                                                style={{
                                                    display: "flex",
                                                    alignItems:
                                                        "center",
                                                    gap: "16px"
                                                }}
                                            >

                                                <InvestigationStatus
                                                    status={
                                                        investigation.status
                                                    }
                                                />


                                                <Link
                                                    to={
                                                        `/investigations/${investigation._id}`
                                                    }

                                                    style={{
                                                        padding:
                                                            "9px 14px",
                                                        background:
                                                            "#f4f6f8",
                                                        color:
                                                            "#11151d",
                                                        textDecoration:
                                                            "none",
                                                        borderRadius:
                                                            "7px",
                                                        fontWeight:
                                                            "700",
                                                        fontSize:
                                                            "13px"
                                                    }}
                                                >

                                                    View

                                                </Link>

                                            </div>

                                        </div>

                                    )
                                )
                            }

                        </div>

                    )
            }

        </div>
    );
};


export default Investigations;