import {
    useEffect,
    useState
} from "react";

import {
    Link,
    useNavigate,
    useParams
} from "react-router-dom";

import Loader from "../components/Loader.jsx";

import {
    getDatasetById
} from "../services/datasetService.js";

import {
    detectAnomalies
} from "../services/anomalyService.js";


const DatasetDetail = () => {

    const {
        datasetId
    } = useParams();


    const navigate =
        useNavigate();


    const [
        dataset,
        setDataset
    ] = useState(null);


    const [
        loading,
        setLoading
    ] = useState(true);


    const [
        detecting,
        setDetecting
    ] = useState(false);


    const [
        error,
        setError
    ] = useState("");


    const [
        message,
        setMessage
    ] = useState("");


    // ==============================
    // Load Dataset
    // ==============================

    useEffect(() => {

        const loadDataset = async () => {

            try {

                setError("");


                const data =
                    await getDatasetById(
                        datasetId
                    );


                setDataset(
                    data.dataset
                );

            } catch (error) {

                setError(
                    error.response
                        ?.data
                        ?.message
                    ||
                    "Failed to load dataset"
                );

            } finally {

                setLoading(false);
            }
        };


        loadDataset();

    }, [datasetId]);


    // ==============================
    // Detect Anomalies
    // ==============================

    const handleDetectAnomalies = async () => {

        try {

            setDetecting(true);

            setError("");

            setMessage("");


            const data =
                await detectAnomalies(
                    datasetId
                );


            if (
                data.candidates
                &&
                data.candidates.length > 0
            ) {

                setMessage(
                    `${data.candidates.length} candidate(s) detected successfully.`
                );


                setTimeout(() => {

                    navigate(
                        "/candidates"
                    );

                }, 1000);

            } else {

                setMessage(
                    "Detection completed successfully, but no anomaly candidates were found."
                );
            }

        } catch (error) {

            console.error(
                "Detection error:",
                error
            );


            setError(
                error.response
                    ?.data
                    ?.message
                ||
                "Anomaly detection failed"
            );

        } finally {

            setDetecting(false);
        }
    };


    // ==============================
    // Loading
    // ==============================

    if (loading) {

        return (

            <Loader
                text="Loading dataset..."
            />

        );
    }


    // ==============================
    // Dataset Error
    // ==============================

    if (
        error
        &&
        !dataset
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

            {/* Back */}

            <Link
                to="/datasets"

                style={{
                    display:
                        "inline-block",

                    marginBottom:
                        "22px",

                    color:
                        "#aeb7c7",

                    textDecoration:
                        "none",

                    fontSize:
                        "14px"
                }}
            >

                ← Back to Datasets

            </Link>


            {/* Page Header */}

            <div
                style={{
                    display:
                        "flex",

                    justifyContent:
                        "space-between",

                    alignItems:
                        "flex-start",

                    gap:
                        "20px",

                    marginBottom:
                        "24px"
                }}
            >

                <div>

                    <p
                        style={{
                            margin:
                                "0 0 8px",

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

                        Dataset Detail

                    </p>


                    <h1
                        style={{
                            margin: 0,

                            fontSize:
                                "30px",

                            color:
                                "#ffffff"
                        }}
                    >

                        {
                            dataset?.name
                        }

                    </h1>

                </div>


                <span
                    style={{
                        padding:
                            "7px 12px",

                        borderRadius:
                            "20px",

                        background:
                            "#202733",

                        color:
                            "#dce5f4",

                        fontSize:
                            "12px",

                        fontWeight:
                            "600"
                    }}
                >

                    {
                        dataset?.status
                        ||
                        "REGISTERED"
                    }

                </span>

            </div>


            {/* Error */}

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


            {/* Success Message */}

            {message && (

                <div
                    style={{
                        padding:
                            "14px",

                        marginBottom:
                            "20px",

                        background:
                            "rgba(80, 200, 120, 0.12)",

                        border:
                            "1px solid rgba(80, 200, 120, 0.3)",

                        borderRadius:
                            "8px",

                        color:
                            "#7be49c"
                    }}
                >

                    {message}

                </div>

            )}


            {/* Dataset Information */}

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

                <div
                    style={{
                        display:
                            "flex",

                        justifyContent:
                            "space-between",

                        alignItems:
                            "center",

                        marginBottom:
                            "28px"
                    }}
                >

                    <div>

                        <span
                            style={{
                                display:
                                    "inline-block",

                                padding:
                                    "5px 10px",

                                borderRadius:
                                    "20px",

                                background:
                                    "#222936",

                                color:
                                    "#aeb8c9",

                                fontSize:
                                    "12px",

                                fontWeight:
                                    "600"
                            }}
                        >

                            {
                                dataset?.source
                            }

                        </span>

                    </div>


                    <span
                        style={{
                            color:
                                "#7f8999",

                            fontSize:
                                "13px"
                        }}
                    >

                        Astronomical Dataset

                    </span>

                </div>


                {/* Information Grid */}

                <div
                    style={{
                        display:
                            "grid",

                        gridTemplateColumns:
                            "repeat(auto-fit, minmax(180px, 1fr))",

                        gap:
                            "24px"
                    }}
                >

                    <InfoItem
                        label="Object ID"
                        value={
                            dataset?.objectId
                        }
                    />


                    <InfoItem
                        label="Source / Mission"
                        value={
                            dataset?.source
                        }
                    />


                    <InfoItem
                        label="Status"
                        value={
                            dataset?.status
                            ||
                            "REGISTERED"
                        }
                    />


                    <InfoItem
                        label="Created"
                        value={
                            dataset?.createdAt

                                ? new Date(
                                    dataset.createdAt
                                ).toLocaleString()

                                : "N/A"
                        }
                    />

                </div>


                {/* Description */}

                <div
                    style={{
                        marginTop:
                            "30px",

                        paddingTop:
                            "24px",

                        borderTop:
                            "1px solid #272d39"
                    }}
                >

                    <h3
                        style={{
                            margin:
                                "0 0 10px",

                            color:
                                "#ffffff"
                        }}
                    >

                        Description

                    </h3>


                    <p
                        style={{
                            margin: 0,

                            color:
                                "#9099aa",

                            lineHeight:
                                "1.7"
                        }}
                    >

                        {
                            dataset?.description
                            ||
                            "No description provided."
                        }

                    </p>

                </div>

            </div>


            {/* ML Detection Section */}

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
                            "20px",

                        flexWrap:
                            "wrap"
                    }}
                >

                    <div
                        style={{
                            maxWidth:
                                "650px"
                        }}
                    >

                        <h2
                            style={{
                                margin:
                                    "0 0 10px",

                                fontSize:
                                    "21px",

                                color:
                                    "#ffffff"
                            }}
                        >

                            ML Anomaly Detection

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

                            Fetch the astronomical light curve and run Fluxor's Isolation Forest pipeline to identify statistically unusual regions.

                        </p>

                    </div>


                    <button
                        onClick={
                            handleDetectAnomalies
                        }

                        disabled={
                            detecting
                        }

                        style={{
                            minWidth:
                                "175px",

                            padding:
                                "13px 20px",

                            border:
                                "none",

                            borderRadius:
                                "8px",

                            background:
                                detecting
                                    ? "#343b48"
                                    : "#f4f6f8",

                            color:
                                detecting
                                    ? "#9299a7"
                                    : "#11151d",

                            fontWeight:
                                "700",

                            cursor:
                                detecting
                                    ? "not-allowed"
                                    : "pointer",

                            transition:
                                "0.2s"
                        }}
                    >

                        {
                            detecting
                                ? "Detecting..."
                                : "Detect Anomalies"
                        }

                    </button>

                </div>


                {/* Detection Flow */}

                <div
                    style={{
                        marginTop:
                            "24px",

                        display:
                            "flex",

                        flexWrap:
                            "wrap",

                        gap:
                            "8px",

                        alignItems:
                            "center",

                        color:
                            "#7f8999",

                        fontSize:
                            "13px"
                    }}
                >

                    <span>
                        MAST
                    </span>

                    <span>
                        →
                    </span>

                    <span>
                        Preprocessing
                    </span>

                    <span>
                        →
                    </span>

                    <span>
                        Feature Extraction
                    </span>

                    <span>
                        →
                    </span>

                    <span>
                        Isolation Forest
                    </span>

                    <span>
                        →
                    </span>

                    <span>
                        Candidate Ranking
                    </span>

                </div>

            </div>

        </div>
    );
};


// =====================================
// Reusable Info Component
// =====================================

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


export default DatasetDetail;