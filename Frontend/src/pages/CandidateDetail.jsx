import {
    useEffect,
    useState
} from "react";

import {
    Link,
    useParams
} from "react-router-dom";

import {
    getCandidateById,
    getCandidateLightCurve
} from "../services/anomalyService.js";

import PriorityBadge from "../components/anomaly/PriorityBadge.jsx";
import LightCurveChart from "../components/anomaly/LightCurveChart.jsx";
import Loader from "../components/Loader.jsx";


const CandidateDetail = () => {

    const {
        candidateId
    } = useParams();


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
        error,
        setError
    ] = useState("");


    useEffect(() => {

        const loadCandidate = async () => {

            try {

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


    if (loading) {

        return (

            <Loader
                text="Loading candidate..."
            />

        );
    }


    if (error) {

        return (

            <div
                style={{
                    padding: "16px",

                    background:
                        "rgba(200,50,50,0.15)",

                    color: "#ff8c8c",

                    borderRadius: "8px"
                }}
            >

                {error}

            </div>

        );
    }


    return (

        <div>

            <Link
                to="/candidates"

                style={{
                    color: "#aab3c4",

                    textDecoration:
                        "none"
                }}
            >

                ← Back to Candidates

            </Link>


            <div
                style={{
                    marginTop: "24px",

                    padding: "28px",

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
                        display: "flex",

                        justifyContent:
                            "space-between",

                        alignItems:
                            "center"
                    }}
                >

                    <div>

                        <p
                            style={{
                                color:
                                    "#8991a1",

                                marginBottom:
                                    "6px"
                            }}
                        >
                            Candidate
                        </p>


                        <h1
                            style={{
                                margin: 0
                            }}
                        >

                            {
                                candidate.objectId
                            }

                        </h1>

                    </div>


                    <PriorityBadge
                        priority={
                            candidate.priority
                        }
                    />

                </div>


                <div
                    style={{
                        display: "grid",

                        gridTemplateColumns:
                            "repeat(auto-fit, minmax(180px, 1fr))",

                        gap: "20px",

                        marginTop: "30px"
                    }}
                >

                    <InfoItem
                        label="Anomaly Score"

                        value={
                            typeof candidate.anomalyScore === "number"
                                ? candidate.anomalyScore.toFixed(4)
                                : candidate.anomalyScore
                        }
                    />


                    <InfoItem
                        label="Status"

                        value={
                            candidate.status
                        }
                    />


                    <InfoItem
                        label="Mission"

                        value={
                            candidate.metadata
                                ?.mission
                            ||
                            "Unknown"
                        }
                    />


                    <InfoItem
                        label="RA"

                        value={
                            candidate.metadata
                                ?.ra
                            ??
                            "N/A"
                        }
                    />


                    <InfoItem
                        label="DEC"

                        value={
                            candidate.metadata
                                ?.dec
                            ??
                            "N/A"
                        }
                    />

                </div>

            </div>


            <div
                style={{
                    marginTop: "24px"
                }}
            >

                <LightCurveChart
                    lightCurve={
                        lightCurve
                    }
                />

            </div>


            <div
                style={{
                    marginTop: "24px",

                    padding: "24px",

                    background:
                        "#11151d",

                    border:
                        "1px solid #272d39",

                    borderRadius:
                        "12px"
                }}
            >

                <h3>
                    Scientific Investigation
                </h3>


                <p
                    style={{
                        color: "#8991a1"
                    }}
                >

                    Start Fluxor's multi-agent scientific investigation for this candidate.

                </p>


                <button
                    disabled
                    style={{
                        padding:
                            "12px 20px",

                        border:
                            "none",

                        borderRadius:
                            "8px",

                        opacity:
                            0.5
                    }}
                >

                    Analyze Candidate — Part 4

                </button>

            </div>

        </div>
    );
};


const InfoItem = ({
    label,
    value
}) => {

    return (

        <div>

            <span
                style={{
                    color: "#858d9c",

                    fontSize: "13px"
                }}
            >

                {label}

            </span>


            <strong
                style={{
                    display: "block",

                    marginTop: "6px",

                    color: "#ffffff"
                }}
            >

                {value}

            </strong>

        </div>
    );
};


export default CandidateDetail;