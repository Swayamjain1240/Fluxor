const FollowupPlan = ({
    followupPlan = []
}) => {

    return (

        <div
            style={{
                background: "#11151d",
                border: "1px solid #272d39",
                borderRadius: "12px",
                padding: "24px"
            }}
        >

            <h3
                style={{
                    margin: "0 0 8px",
                    color: "#ffffff"
                }}
            >

                Follow-up Recommendations

            </h3>


            <p
                style={{
                    margin: "0 0 20px",
                    color: "#858e9e",
                    lineHeight: "1.6"
                }}
            >

                Suggested next scientific actions based on the evidence
                collected during the Fluxor investigation.

            </p>


            {
                followupPlan.length === 0
                    ? (

                        <p
                            style={{
                                color: "#727b8a"
                            }}
                        >

                            No follow-up recommendations available.

                        </p>

                    )
                    : (

                        <div
                            style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: "12px"
                            }}
                        >

                            {
                                followupPlan.map(
                                    (
                                        item,
                                        index
                                    ) => (

                                        <div
                                            key={index}
                                            style={{
                                                display: "flex",
                                                gap: "14px",
                                                padding: "14px",
                                                background: "#151a23",
                                                border: "1px solid #252c37",
                                                borderRadius: "8px"
                                            }}
                                        >

                                            <span
                                                style={{
                                                    minWidth: "28px",
                                                    height: "28px",
                                                    display: "flex",
                                                    alignItems: "center",
                                                    justifyContent: "center",
                                                    background: "#202733",
                                                    borderRadius: "50%",
                                                    color: "#ffffff",
                                                    fontSize: "12px",
                                                    fontWeight: "700"
                                                }}
                                            >

                                                {index + 1}

                                            </span>


                                            <p
                                                style={{
                                                    margin: 0,
                                                    color: "#a7b0c0",
                                                    lineHeight: "1.6"
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
            }

        </div>
    );
};


export default FollowupPlan;