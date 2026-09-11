import {
    Link
} from "react-router-dom";

import PriorityBadge from "./PriorityBadge.jsx";


const CandidateCard = ({ candidate }) => {

    return (

        <div
            style={{
                background: "#11151d",

                border: "1px solid #272d39",

                borderRadius: "12px",

                padding: "22px",

                display: "flex",

                flexDirection: "column",

                gap: "14px"
            }}
        >

            <div
                style={{
                    display: "flex",

                    justifyContent: "space-between",

                    alignItems: "center"
                }}
            >

                <h3
                    style={{
                        margin: 0,
                        color: "#ffffff"
                    }}
                >

                    {candidate.objectId}

                </h3>


                <PriorityBadge
                    priority={
                        candidate.priority
                    }
                />

            </div>


            <div>

                <p
                    style={{
                        color: "#8b93a3",

                        margin: "0 0 5px"
                    }}
                >
                    Anomaly Score
                </p>


                <strong
                    style={{
                        fontSize: "24px",

                        color: "#ffffff"
                    }}
                >

                    {
                        typeof candidate.anomalyScore === "number"
                            ? candidate.anomalyScore.toFixed(3)
                            : candidate.anomalyScore
                    }

                </strong>

            </div>


            <p
                style={{
                    color: "#8b93a3",

                    margin: 0
                }}
            >

                Status: {candidate.status}

            </p>


            <Link
                to={
                    `/candidates/${candidate._id}`
                }

                style={{
                    textDecoration: "none",

                    textAlign: "center",

                    padding: "10px",

                    background: "#ffffff",

                    color: "#111111",

                    borderRadius: "7px",

                    fontWeight: "600"
                }}
            >

                View Candidate

            </Link>

        </div>
    );
};


export default CandidateCard;