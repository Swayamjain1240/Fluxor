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
    getInvestigationById
} from "../services/investigationService.js";

import {
    getReportByInvestigation
} from "../services/reportService.js";

import Loader from "../components/Loader.jsx";

import InvestigationStatus from "../components/investigation/InvestigationStatus.jsx";

import AgentTrace from "../components/investigation/AgentTrace.jsx";

import ConfidenceCard from "../components/investigation/ConfidenceCard.jsx";

import HypothesisCard from "../components/investigation/HypothesisCard.jsx";

import EvidenceCard from "../components/investigation/EvidenceCard.jsx";


const Investigation = () => {

    const {
        investigationId
    } = useParams();


    const navigate =
        useNavigate();


    const [
        investigation,
        setInvestigation
    ] = useState(null);


    const [
        loading,
        setLoading
    ] = useState(true);


    const [
        openingReport,
        setOpeningReport
    ] = useState(false);


    const [
        error,
        setError
    ] = useState("");


    // =========================================
    // Load Investigation
    // =========================================

    useEffect(() => {

        const loadInvestigation = async () => {

            try {

                setError("");


                const data =
                    await getInvestigationById(
                        investigationId
                    );


                setInvestigation(
                    data.investigation
                    ||
                    data
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
                    "Failed to load investigation"
                );

            } finally {

                setLoading(false);
            }
        };


        loadInvestigation();

    }, [investigationId]);


    // =========================================
    // Open Scientific Report
    // =========================================

    const handleOpenReport = async () => {

        try {

            setOpeningReport(true);

            setError("");


            const data =
                await getReportByInvestigation(
                    investigationId
                );


            const report =
                data.report
                ||
                data;


            if (!report?._id) {

                throw new Error(
                    "Scientific report not found"
                );
            }


            navigate(
                `/reports/${report._id}`
            );

        } catch (error) {

            console.error(
                "Report loading error:",
                error
            );


            setError(
                error.response
                    ?.data
                    ?.message
                ||
                error.message
                ||
                "Failed to open scientific report"
            );

        } finally {

            setOpeningReport(false);
        }
    };


    // =========================================
    // Loading
    // =========================================

    if (loading) {

        return (

            <Loader
                text="Loading scientific investigation..."
            />

        );
    }


    // =========================================
    // Error
    // =========================================

    if (
        error
        &&
        !investigation
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
                        "#ff8989"
                }}
            >

                {error}

            </div>

        );
    }


    const hypotheses =
        investigation
            ?.hypotheses
        ||
        [];


    const followupPlan =
        investigation
            ?.followupPlan
        ||
        [];


    return (

        <div
            style={{
                width: "100%"
            }}
        >

            {/* ================================= */}
            {/* Back */}
            {/* ================================= */}

            <Link
                to="/investigations"

                style={{
                    display:
                        "inline-block",

                    marginBottom:
                        "22px",

                    color:
                        "#aab3c4",

                    textDecoration:
                        "none",

                    fontSize:
                        "14px"
                }}
            >

                ← Back to Investigations

            </Link>


            {/* ================================= */}
            {/* Error Message */}
            {/* ================================= */}

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
                            "#ff8989"
                    }}
                >

                    {error}

                </div>

            )}


            {/* ================================= */}
            {/* Header */}
            {/* ================================= */}

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
                        "wrap",

                    marginBottom:
                        "28px"
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
                                "uppercase",

                            letterSpacing:
                                "1px"
                        }}
                    >

                        Scientific Investigation

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
                            investigation
                                ?.objectId
                            ||
                            investigation
                                ?.candidateId
                                ?.objectId
                            ||
                            "Fluxor Investigation"
                        }

                    </h1>

                </div>


                <InvestigationStatus
                    status={
                        investigation
                            ?.status
                    }
                />

            </div>


            {/* ================================= */}
            {/* Investigation Summary */}
            {/* ================================= */}

            <div
                style={{
                    display:
                        "grid",

                    gridTemplateColumns:
                        "repeat(auto-fit, minmax(180px, 1fr))",

                    gap:
                        "16px",

                    marginBottom:
                        "24px"
                }}
            >

                <SummaryCard
                    label="Confidence"

                    value={
                        `${Math.round(
                            (
                                investigation
                                    ?.confidence
                                ||
                                0
                            )
                            *
                            100
                        )}%`
                    }
                />


                <SummaryCard
                    label="Iterations"

                    value={
                        `${
                            investigation
                                ?.iterationCount
                            ||
                            0
                        } / 3`
                    }
                />


                <SummaryCard
                    label="Status"

                    value={
                        investigation
                            ?.status
                        ||
                        "UNKNOWN"
                    }
                />


                <SummaryCard
                    label="Hypotheses"

                    value={
                        hypotheses.length
                    }
                />

            </div>


            {/* ================================= */}
            {/* Confidence + Agent Trace */}
            {/* ================================= */}

            <div
                style={{
                    display:
                        "grid",

                    gridTemplateColumns:
                        "repeat(auto-fit, minmax(320px, 1fr))",

                    gap:
                        "22px",

                    marginBottom:
                        "28px"
                }}
            >

                <ConfidenceCard
                    confidence={
                        investigation
                            ?.confidence
                        ||
                        0
                    }

                    iterationCount={
                        investigation
                            ?.iterationCount
                        ||
                        0
                    }
                />


                <AgentTrace
                    investigation={
                        investigation
                    }
                />

            </div>


            {/* ================================= */}
            {/* Hypotheses */}
            {/* ================================= */}

            <div
                style={{
                    marginBottom:
                        "28px"
                }}
            >

                <div
                    style={{
                        marginBottom:
                            "18px"
                    }}
                >

                    <h2
                        style={{
                            margin:
                                "0 0 8px",

                            color:
                                "#ffffff"
                        }}
                    >

                        Scientific Hypotheses

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

                        Competing astrophysical explanations generated
                        from catalog, historical and literature evidence.

                    </p>

                </div>


                {
                    hypotheses.length === 0
                        ? (

                            <div
                                style={{
                                    padding:
                                        "25px",

                                    background:
                                        "#11151d",

                                    border:
                                        "1px solid #272d39",

                                    borderRadius:
                                        "12px",

                                    color:
                                        "#8992a3"
                                }}
                            >

                                No scientific hypotheses were generated.

                            </div>

                        )
                        : (

                            <div
                                style={{
                                    display:
                                        "grid",

                                    gap:
                                        "18px"
                                }}
                            >

                                {
                                    hypotheses.map(
                                        (
                                            hypothesis,
                                            index
                                        ) => (

                                            <HypothesisCard
                                                key={
                                                    `${hypothesis?.name || "hypothesis"}-${index}`
                                                }

                                                hypothesis={
                                                    hypothesis
                                                }

                                                index={
                                                    index
                                                }
                                            />

                                        )
                                    )
                                }

                            </div>

                        )
                }

            </div>


            {/* ================================= */}
            {/* Scientific Evidence */}
            {/* ================================= */}

            <EvidenceCard
                evidence={
                    investigation
                        ?.evidence
                }
            />


            {/* ================================= */}
            {/* Follow-up Recommendations */}
            {/* ================================= */}

            <div
                style={{
                    marginTop:
                        "24px",

                    padding:
                        "24px",

                    background:
                        "#11151d",

                    border:
                        "1px solid #272d39",

                    borderRadius:
                        "12px"
                }}
            >

                <h3
                    style={{
                        margin:
                            "0 0 8px",

                        color:
                            "#ffffff"
                    }}
                >

                    Follow-up Recommendations

                </h3>


                <p
                    style={{
                        margin:
                            "0 0 18px",

                        color:
                            "#8992a3",

                        lineHeight:
                            "1.6"
                    }}
                >

                    Suggested next observations or analysis steps based
                    on the current evidence.

                </p>


                {
                    followupPlan.length > 0
                        ? (

                            <div
                                style={{
                                    display:
                                        "flex",

                                    flexDirection:
                                        "column",

                                    gap:
                                        "10px"
                                }}
                            >

                                {
                                    followupPlan.map(
                                        (
                                            item,
                                            index
                                        ) => (

                                            <div
                                                key={
                                                    index
                                                }

                                                style={{
                                                    display:
                                                        "flex",

                                                    gap:
                                                        "14px",

                                                    alignItems:
                                                        "flex-start",

                                                    padding:
                                                        "14px",

                                                    background:
                                                        "#151a23",

                                                    border:
                                                        "1px solid #252c37",

                                                    borderRadius:
                                                        "8px"
                                                }}
                                            >

                                                <span
                                                    style={{
                                                        minWidth:
                                                            "28px",

                                                        height:
                                                            "28px",

                                                        display:
                                                            "flex",

                                                        alignItems:
                                                            "center",

                                                        justifyContent:
                                                            "center",

                                                        borderRadius:
                                                            "50%",

                                                        background:
                                                            "#202733",

                                                        color:
                                                            "#ffffff",

                                                        fontSize:
                                                            "12px",

                                                        fontWeight:
                                                            "700"
                                                    }}
                                                >

                                                    {
                                                        index + 1
                                                    }

                                                </span>


                                                <p
                                                    style={{
                                                        margin: 0,

                                                        color:
                                                            "#a0a9b8",

                                                        lineHeight:
                                                            "1.7"
                                                    }}
                                                >

                                                    {item}

                                                </p>

                                            </div>

                                        )
                                    )
                                }

                            </div>

                        )
                        : (

                            <p
                                style={{
                                    color:
                                        "#7f8797"
                                }}
                            >

                                No follow-up recommendations available.

                            </p>

                        )
                }

            </div>


            {/* ================================= */}
            {/* Scientific Report */}
            {/* ================================= */}

            <div
                style={{
                    marginTop:
                        "24px",

                    padding:
                        "28px",

                    background:
                        "#11151d",

                    border:
                        "1px solid #272d39",

                    borderRadius:
                        "12px"
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

                            Final Research Output

                        </p>


                        <h2
                            style={{
                                margin:
                                    "0 0 10px",

                                color:
                                    "#ffffff"
                            }}
                        >

                            Scientific Report

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

                            Open Fluxor's complete AI-generated scientific
                            report, review the reasoning and submit the
                            final scientist approval or rejection.

                        </p>

                    </div>


                    <button
                        onClick={
                            handleOpenReport
                        }

                        disabled={
                            openingReport
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
                                openingReport
                                    ? "#343b48"
                                    : "#f4f6f8",

                            color:
                                openingReport
                                    ? "#939ba9"
                                    : "#11151d",

                            cursor:
                                openingReport
                                    ? "not-allowed"
                                    : "pointer",

                            fontWeight:
                                "700",

                            transition:
                                "0.2s"
                        }}
                    >

                        {
                            openingReport
                                ? "Opening Report..."
                                : "View Scientific Report"
                        }

                    </button>

                </div>


                <div
                    style={{
                        marginTop:
                            "22px",

                        padding:
                            "14px",

                        background:
                            "#0d1118",

                        border:
                            "1px solid #242b36",

                        borderRadius:
                            "8px",

                        color:
                            "#7f8999",

                        fontSize:
                            "12px",

                        lineHeight:
                            "1.6"
                    }}
                >

                    Fluxor provides AI-assisted scientific analysis.
                    Final interpretation and validation remain with
                    the scientist.

                </div>

            </div>

        </div>
    );
};


// =========================================
// Summary Card
// =========================================

const SummaryCard = ({
    label,
    value
}) => {

    return (

        <div
            style={{
                padding:
                    "18px",

                background:
                    "#11151d",

                border:
                    "1px solid #272d39",

                borderRadius:
                    "10px"
            }}
        >

            <span
                style={{
                    display:
                        "block",

                    marginBottom:
                        "7px",

                    color:
                        "#7f8999",

                    fontSize:
                        "12px",

                    textTransform:
                        "uppercase",

                    letterSpacing:
                        "0.6px"
                }}
            >

                {label}

            </span>


            <strong
                style={{
                    color:
                        "#ffffff",

                    fontSize:
                        "20px"
                }}
            >

                {value}

            </strong>

        </div>
    );
};


export default Investigation;