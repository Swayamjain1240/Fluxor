import {
    useEffect,
    useState
} from "react";

import {
    Link,
    useParams
} from "react-router-dom";

import {
    getInvestigationById
} from "../services/investigationService.js";

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


    const [
        investigation,
        setInvestigation
    ] = useState(null);


    const [
        loading,
        setLoading
    ] = useState(true);


    const [
        error,
        setError
    ] = useState("");


    useEffect(() => {

        const loadInvestigation = async () => {

            try {

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


    if (loading) {

        return (

            <Loader
                text="Loading scientific investigation..."
            />

        );
    }


    if (error) {

        return (

            <div
                style={{
                    padding:
                        "16px",

                    background:
                        "rgba(220,60,60,0.15)",

                    color:
                        "#ff8989",

                    borderRadius:
                        "8px"
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


    return (

        <div>

            <Link
                to="/candidates"

                style={{
                    color:
                        "#aab3c4",

                    textDecoration:
                        "none"
                }}
            >

                ← Back to Candidates

            </Link>


            {/* Header */}

            <div
                style={{
                    marginTop:
                        "22px",

                    marginBottom:
                        "28px",

                    display:
                        "flex",

                    justifyContent:
                        "space-between",

                    alignItems:
                        "center",

                    gap:
                        "20px"
                }}
            >

                <div>

                    <p
                        style={{
                            margin:
                                "0 0 8px",

                            color:
                                "#7f8999"
                        }}
                    >

                        Scientific Investigation

                    </p>


                    <h1
                        style={{
                            margin: 0
                        }}
                    >

                        {
                            investigation
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


            {/* Confidence + Agent Trace */}

            <div
                style={{
                    display:
                        "grid",

                    gridTemplateColumns:
                        "minmax(280px, 0.7fr) minmax(400px, 1.3fr)",

                    gap:
                        "22px",

                    marginBottom:
                        "24px"
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


            {/* Hypotheses */}

            <div
                style={{
                    marginBottom:
                        "28px"
                }}
            >

                <h2>
                    Scientific Hypotheses
                </h2>


                <p
                    style={{
                        color:
                            "#8992a3"
                    }}
                >

                    Competing explanations generated from catalog, historical and literature evidence.

                </p>


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

                                No hypotheses were generated.

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
                                                    index
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


            {/* Evidence */}

            <EvidenceCard
                evidence={
                    investigation
                        ?.evidence
                }
            />


            {/* Follow-up */}

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
                        marginTop: 0
                    }}
                >

                    Follow-up Recommendations

                </h3>


                {
                    investigation
                        ?.followupPlan
                        ?.length
                        > 0
                        ? (

                            <ul
                                style={{
                                    color:
                                        "#a0a8b7",

                                    lineHeight:
                                        "1.8"
                                }}
                            >

                                {
                                    investigation
                                        .followupPlan
                                        .map(
                                            (
                                                item,
                                                index
                                            ) => (

                                                <li
                                                    key={
                                                        index
                                                    }
                                                >

                                                    {item}

                                                </li>

                                            )
                                        )
                                }

                            </ul>

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


            {/* Report */}

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
                        marginTop: 0
                    }}
                >

                    Scientific Report

                </h3>


                <p
                    style={{
                        color:
                            "#8992a3"
                    }}
                >

                    The complete structured report and scientist validation interface will be available in Part 5.

                </p>

            </div>

        </div>
    );
};


export default Investigation;