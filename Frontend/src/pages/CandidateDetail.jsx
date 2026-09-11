import {
    useEffect,
    useState
} from "react";

import {
    Link,
    useNavigate,
    useParams
} from "react-router-dom";

import {
    getCandidateById,
    getCandidateLightCurve
} from "../services/anomalyService.js";

import {
    startInvestigation
} from "../services/investigationService.js";

import PriorityBadge from "../components/anomaly/PriorityBadge.jsx";

import LightCurveChart from "../components/anomaly/LightCurveChart.jsx";

import Loader from "../components/Loader.jsx";


const CandidateDetail = () => {

    const {
        candidateId
    } = useParams();


    const navigate =
        useNavigate();


    const [
        candidate,
        setCandidate
    ] = useState(null);


    const [
        lightCurve,
        setLightCurve
    ] = useState([]);


    const [
        loading,
        setLoading
    ] = useState(true);


    const [
        analyzing,
        setAnalyzing
    ] = useState(false);


    const [
        error,
        setError
    ] = useState("");


    // =========================================
    // Load Candidate + Light Curve
    // =========================================

    useEffect(() => {

        const loadCandidate = async () => {

            try {

                setError("");


                const [
                    candidateData,
                    lightCurveData
                ] = await Promise.all([

                    getCandidateById(
                        candidateId
                    ),

                    getCandidateLightCurve(
                        candidateId
                    )

                ]);


                setCandidate(
                    candidateData.candidate
                );


                setLightCurve(
                    lightCurveData.lightCurve
                    ||
                    []
                );

            } catch (error) {

                console.error(
                    "Candidate loading error:",
                    error
                );


                setError(
                    error.response
                        ?.data
                        ?.message
                    ||
                    "Failed to load candidate"
                );

            } finally {

                setLoading(false);
            }
        };


        loadCandidate();

    }, [candidateId]);


    // =========================================
    // Start Scientific Investigation
    // =========================================

    const handleAnalyze = async () => {

        try {

            setAnalyzing(true);

            setError("");


            const data =
                await startInvestigation(
                    candidateId
                );


            console.log(
                "Investigation response:",
                data
            );


            const investigationId =
                data.investigation?._id
                ||
                data.investigationId
                ||
                data._id;


            if (!investigationId) {

                throw new Error(
                    "Investigation ID missing from backend response"
                );
            }


            navigate(
                `/investigations/${investigationId}`
            );

        } catch (error) {

            console.error(
                "Investigation error:",
                error
            );


            setError(
                error.response
                    ?.data
                    ?.message
                ||
                error.message
                ||
                "Scientific investigation failed"
            );

        } finally {

            setAnalyzing(false);
        }
    };


    // =========================================
    // Initial Loading
    // =========================================

    if (loading) {

        return (

            <Loader
                text="Loading candidate..."
            />

        );
    }


    // =========================================
    // Candidate Not Available
    // =========================================

    if (
        error
        &&
        !candidate
    ) {

        return (

            <div
                style={{
                    padding: "18px",

                    background:
                        "rgba(220, 60, 60, 0.15)",

                    border:
                        "1px solid rgba(220, 60, 60, 0.3)",

                    borderRadius:
                        "10px",

                    color:
                        "#ff8b8b"
                }}
            >

                {error}

            </div>

        );
    }


    return (

        <div
            style={{
                width: "100%"
            }}
        >

            {/* =============================== */}
            {/* Back Button */}
            {/* =============================== */}

            <Link
                to="/candidates"

                style={{
                    display:
                        "inline-block",

                    color:
                        "#aab3c4",

                    textDecoration:
                        "none",

                    marginBottom:
                        "22px",

                    fontSize:
                        "14px"
                }}
            >

                ← Back to Candidates

            </Link>


            {/* =============================== */}
            {/* Error Message */}
            {/* =============================== */}

            {error && (

                <div
                    style={{
                        padding:
                            "14px",

                        marginBottom:
                            "20px",

                        background:
                            "rgba(220, 60, 60, 0.15)",

                        border:
                            "1px solid rgba(220, 60, 60, 0.3)",

                        borderRadius:
                            "8px",

                        color:
                            "#ff8b8b"
                    }}
                >

                    {error}

                </div>

            )}


            {/* =============================== */}
            {/* Candidate Main Card */}
            {/* =============================== */}

            <div
                style={{
                    background:
                        "#11151d",

                    border:
                        "1px solid #272d39",

                    borderRadius:
                        "12px",

                    padding:
                        "28px",

                    marginBottom:
                        "24px"
                }}
            >

                {/* Header */}

                <div
                    style={{
                        display:
                            "flex",

                        justifyContent:
                            "space-between",

                        alignItems:
                            "center",

                        gap:
                            "20px",

                        flexWrap:
                            "wrap"
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
                                    "13px",

                                textTransform:
                                    "uppercase",

                                letterSpacing:
                                    "1px"
                            }}
                        >

                            Anomaly Candidate

                        </p>


                        <h1
                            style={{
                                margin: 0,

                                color:
                                    "#ffffff",

                                fontSize:
                                    "30px"
                            }}
                        >

                            {
                                candidate
                                    ?.objectId
                            }

                        </h1>

                    </div>


                    <PriorityBadge
                        priority={
                            candidate
                                ?.priority
                        }
                    />

                </div>


                {/* Candidate Information */}

                <div
                    style={{
                        display:
                            "grid",

                        gridTemplateColumns:
                            "repeat(auto-fit, minmax(170px, 1fr))",

                        gap:
                            "24px",

                        marginTop:
                            "32px"
                    }}
                >

                    <InfoItem
                        label="Anomaly Score"

                        value={
                            typeof candidate
                                ?.anomalyScore
                                === "number"

                                ? candidate
                                    .anomalyScore
                                    .toFixed(4)

                                : candidate
                                    ?.anomalyScore
                        }
                    />


                    <InfoItem
                        label="Priority"

                        value={
                            candidate
                                ?.priority
                        }
                    />


                    <InfoItem
                        label="Status"

                        value={
                            candidate
                                ?.status
                            ||
                            "DETECTED"
                        }
                    />


                    <InfoItem
                        label="Mission"

                        value={
                            candidate
                                ?.metadata
                                ?.mission
                            ||
                            candidate
                                ?.metadata
                                ?.source
                            ||
                            "Unknown"
                        }
                    />


                    <InfoItem
                        label="RA"

                        value={
                            candidate
                                ?.metadata
                                ?.ra
                            ??
                            "N/A"
                        }
                    />


                    <InfoItem
                        label="DEC"

                        value={
                            candidate
                                ?.metadata
                                ?.dec
                            ??
                            "N/A"
                        }
                    />


                    <InfoItem
                        label="Data Points"

                        value={
                            candidate
                                ?.metadata
                                ?.points
                            ??
                            lightCurve.length
                            ??
                            "N/A"
                        }
                    />


                    <InfoItem
                        label="Total Windows"

                        value={
                            candidate
                                ?.metadata
                                ?.totalWindows
                            ??
                            "N/A"
                        }
                    />

                </div>


                {/* Scientific Note */}

                <div
                    style={{
                        marginTop:
                            "30px",

                        padding:
                            "16px",

                        background:
                            "#0d1118",

                        border:
                            "1px solid #242b36",

                        borderRadius:
                            "8px",

                        color:
                            "#8f98a8",

                        lineHeight:
                            "1.6",

                        fontSize:
                            "13px"
                    }}
                >

                    The anomaly score represents statistical unusualness
                    detected by the Isolation Forest pipeline. It should
                    not be interpreted as a calibrated probability of an
                    astronomical discovery.

                </div>

            </div>


            {/* =============================== */}
            {/* Light Curve */}
            {/* =============================== */}

            <div
                style={{
                    marginBottom:
                        "24px"
                }}
            >

                <LightCurveChart
                    lightCurve={
                        lightCurve
                    }
                />

            </div>


            {/* =============================== */}
            {/* Metadata */}
            {/* =============================== */}

            <div
                style={{
                    background:
                        "#11151d",

                    border:
                        "1px solid #272d39",

                    borderRadius:
                        "12px",

                    padding:
                        "24px",

                    marginBottom:
                        "24px"
                }}
            >

                <h3
                    style={{
                        margin:
                            "0 0 18px"
                    }}
                >

                    Candidate Metadata

                </h3>


                {
                    candidate
                        ?.metadata

                        ? (

                            <pre
                                style={{
                                    margin: 0,

                                    background:
                                        "#0d1118",

                                    borderRadius:
                                        "8px",

                                    padding:
                                        "16px",

                                    color:
                                        "#aab3c4",

                                    fontSize:
                                        "12px",

                                    whiteSpace:
                                        "pre-wrap",

                                    wordBreak:
                                        "break-word",

                                    overflowX:
                                        "auto"
                                }}
                            >

                                {
                                    JSON.stringify(
                                        candidate.metadata,
                                        null,
                                        2
                                    )
                                }

                            </pre>

                        )

                        : (

                            <p
                                style={{
                                    color:
                                        "#7f8797"
                                }}
                            >

                                No candidate metadata available.

                            </p>

                        )
                }

            </div>


            {/* =============================== */}
            {/* Agentic Investigation */}
            {/* =============================== */}

            <div
                style={{
                    background:
                        "#11151d",

                    border:
                        "1px solid #272d39",

                    borderRadius:
                        "12px",

                    padding:
                        "28px"
                }}
            >

                <div
                    style={{
                        display:
                            "flex",

                        justifyContent:
                            "space-between",

                        alignItems:
                            "center",

                        gap:
                            "24px",

                        flexWrap:
                            "wrap"
                    }}
                >

                    <div
                        style={{
                            maxWidth:
                                "700px"
                        }}
                    >

                        <p
                            style={{
                                margin:
                                    "0 0 7px",

                                color:
                                    "#7f8999",

                                fontSize:
                                    "12px",

                                textTransform:
                                    "uppercase",

                                letterSpacing:
                                    "1px"
                            }}
                        >

                            Agentic AI

                        </p>


                        <h2
                            style={{
                                margin:
                                    "0 0 10px",

                                color:
                                    "#ffffff"
                            }}
                        >

                            Scientific Investigation

                        </h2>


                        <p
                            style={{
                                margin: 0,

                                color:
                                    "#8992a3",

                                lineHeight:
                                    "1.6"
                            }}
                        >

                            Launch Fluxor's multi-agent investigation to
                            analyze catalog information, historical
                            photometry, scientific literature and competing
                            astrophysical hypotheses.

                        </p>

                    </div>


                    <button
                        onClick={
                            handleAnalyze
                        }

                        disabled={
                            analyzing
                        }

                        style={{
                            minWidth:
                                "210px",

                            padding:
                                "13px 22px",

                            border:
                                "none",

                            borderRadius:
                                "8px",

                            background:
                                analyzing
                                    ? "#343b48"
                                    : "#f4f6f8",

                            color:
                                analyzing
                                    ? "#949cab"
                                    : "#11151d",

                            fontWeight:
                                "700",

                            cursor:
                                analyzing
                                    ? "not-allowed"
                                    : "pointer",

                            transition:
                                "0.2s"
                        }}
                    >

                        {
                            analyzing
                                ? "Running Investigation..."
                                : "Analyze Candidate"
                        }

                    </button>

                </div>


                {/* Agent Workflow */}

                <div
                    style={{
                        marginTop:
                            "26px",

                        paddingTop:
                            "22px",

                        borderTop:
                            "1px solid #272d39"
                    }}
                >

                    <p
                        style={{
                            color:
                                "#7f8999",

                            margin:
                                "0 0 14px",

                            fontSize:
                                "13px"
                        }}
                    >

                        Investigation workflow

                    </p>


                    <div
                        style={{
                            display:
                                "flex",

                            alignItems:
                                "center",

                            flexWrap:
                                "wrap",

                            gap:
                                "8px",

                            color:
                                "#a4adbd",

                            fontSize:
                                "13px"
                        }}
                    >

                        <WorkflowItem
                            text="Triage"
                        />

                        <Arrow />


                        <WorkflowItem
                            text="Catalog"
                        />

                        <Arrow />


                        <WorkflowItem
                            text="Historical"
                        />

                        <Arrow />


                        <WorkflowItem
                            text="RAG"
                        />

                        <Arrow />


                        <WorkflowItem
                            text="Reasoning"
                        />

                        <Arrow />


                        <WorkflowItem
                            text="Confidence Loop"
                        />

                    </div>

                </div>


                {/* Analyzing State */}

                {analyzing && (

                    <div
                        style={{
                            marginTop:
                                "24px",

                            padding:
                                "16px",

                            border:
                                "1px solid #303744",

                            borderRadius:
                                "8px",

                            background:
                                "#151a22",

                            color:
                                "#a5afbf"
                        }}
                    >

                        Fluxor is running catalog queries, historical
                        analysis, RAG retrieval and scientific reasoning.
                        This request may take some time.

                    </div>

                )}

            </div>

        </div>
    );
};


// =========================================
// Reusable Information Item
// =========================================

const InfoItem = ({
    label,
    value
}) => {

    return (

        <div>

            <span
                style={{
                    display:
                        "block",

                    color:
                        "#7f8999",

                    fontSize:
                        "13px",

                    marginBottom:
                        "7px"
                }}
            >

                {label}

            </span>


            <strong
                style={{
                    display:
                        "block",

                    color:
                        "#ffffff",

                    fontSize:
                        "15px",

                    wordBreak:
                        "break-word"
                }}
            >

                {
                    value
                    ??
                    "N/A"
                }

            </strong>

        </div>
    );
};


// =========================================
// Workflow Item
// =========================================

const WorkflowItem = ({
    text
}) => {

    return (

        <span
            style={{
                padding:
                    "7px 11px",

                borderRadius:
                    "20px",

                background:
                    "#202733",

                border:
                    "1px solid #303744",

                color:
                    "#b4bdcc",

                whiteSpace:
                    "nowrap"
            }}
        >

            {text}

        </span>
    );
};


// =========================================
// Workflow Arrow
// =========================================

const Arrow = () => {

    return (

        <span
            style={{
                color:
                    "#5f6877"
            }}
        >

            →

        </span>
    );
};


export default CandidateDetail;