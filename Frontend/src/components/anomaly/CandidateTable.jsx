import {
    Link
} from "react-router-dom";

import PriorityBadge from "./PriorityBadge.jsx";


const CandidateTable = ({ candidates }) => {

    return (

        <div
            style={{
                overflowX: "auto",

                background: "#11151d",

                border: "1px solid #272d39",

                borderRadius: "12px"
            }}
        >

            <table
                style={{
                    width: "100%",

                    borderCollapse: "collapse"
                }}
            >

                <thead>

                    <tr>

                        {
                            [
                                "Object",
                                "Score",
                                "Priority",
                                "Status",
                                "Action"
                            ].map(
                                (heading) => (

                                    <th
                                        key={heading}

                                        style={{
                                            textAlign: "left",

                                            padding: "16px",

                                            color: "#8d95a4",

                                            borderBottom:
                                                "1px solid #272d39"
                                        }}
                                    >

                                        {heading}

                                    </th>

                                )
                            )
                        }

                    </tr>

                </thead>


                <tbody>

                    {
                        candidates.map(
                            (candidate) => (

                                <tr
                                    key={
                                        candidate._id
                                    }
                                >

                                    <td
                                        style={{
                                            padding: "16px",

                                            borderBottom:
                                                "1px solid #1d222c"
                                        }}
                                    >

                                        {
                                            candidate.objectId
                                        }

                                    </td>


                                    <td
                                        style={{
                                            padding: "16px",

                                            borderBottom:
                                                "1px solid #1d222c"
                                        }}
                                    >

                                        {
                                            typeof candidate.anomalyScore === "number"
                                                ? candidate.anomalyScore.toFixed(3)
                                                : candidate.anomalyScore
                                        }

                                    </td>


                                    <td
                                        style={{
                                            padding: "16px",

                                            borderBottom:
                                                "1px solid #1d222c"
                                        }}
                                    >

                                        <PriorityBadge
                                            priority={
                                                candidate.priority
                                            }
                                        />

                                    </td>


                                    <td
                                        style={{
                                            padding: "16px",

                                            borderBottom:
                                                "1px solid #1d222c"
                                        }}
                                    >

                                        {
                                            candidate.status
                                        }

                                    </td>


                                    <td
                                        style={{
                                            padding: "16px",

                                            borderBottom:
                                                "1px solid #1d222c"
                                        }}
                                    >

                                        <Link
                                            to={
                                                `/candidates/${candidate._id}`
                                            }

                                            style={{
                                                color: "#9ccfff"
                                            }}
                                        >

                                            View

                                        </Link>

                                    </td>

                                </tr>

                            )
                        )
                    }

                </tbody>

            </table>

        </div>
    );
};


export default CandidateTable;