const AgentTrace = ({
    investigation
}) => {

    const evidence =
        investigation?.evidence
        ||
        {};


    const agents = [

        {
            name:
                "Triage Agent",

            description:
                "Determines scientific interest and artifact risk.",

            completed:
                Boolean(
                    investigation
                        ?.triageResult
                )
        },

        {
            name:
                "Catalog Agent",

            description:
                "Queries astronomical catalog information.",

            completed:
                Boolean(
                    investigation
                        ?.catalogSummary
                    ||
                    evidence
                        ?.catalog
                )
        },

        {
            name:
                "Historical Agent",

            description:
                "Analyzes historical photometric behaviour.",

            completed:
                Boolean(
                    evidence
                        ?.historical
                )
        },

        {
            name:
                "RAG Agent",

            description:
                "Retrieves relevant scientific literature.",

            completed:
                Array.isArray(
                    evidence
                        ?.literature
                )
                    ? evidence
                        .literature
                        .length > 0
                    : Boolean(
                        evidence
                            ?.literature
                    )
        },

        {
            name:
                "Reasoning Agent",

            description:
                "Generates evidence-grounded scientific hypotheses.",

            completed:
                Boolean(
                    investigation
                        ?.hypotheses
                        ?.length
                )
        }

    ];


    return (

        <div
            style={{
                background:
                    "#11151d",

                border:
                    "1px solid #272d39",

                borderRadius:
                    "12px",

                padding:
                    "24px"
            }}
        >

            <h3
                style={{
                    margin:
                        "0 0 22px"
                }}
            >

                Agent Trace

            </h3>


            <div
                style={{
                    display:
                        "flex",

                    flexDirection:
                        "column",

                    gap:
                        "14px"
                }}
            >

                {
                    agents.map(
                        (
                            agent,
                            index
                        ) => (

                            <div
                                key={
                                    agent.name
                                }

                                style={{
                                    display:
                                        "flex",

                                    alignItems:
                                        "center",

                                    gap:
                                        "16px",

                                    padding:
                                        "14px",

                                    border:
                                        "1px solid #242b36",

                                    borderRadius:
                                        "9px",

                                    background:
                                        "#151a23"
                                }}
                            >

                                <div
                                    style={{
                                        width:
                                            "32px",

                                        height:
                                            "32px",

                                        borderRadius:
                                            "50%",

                                        display:
                                            "flex",

                                        alignItems:
                                            "center",

                                        justifyContent:
                                            "center",

                                        background:
                                            agent.completed
                                                ? "#254a35"
                                                : "#292f39",

                                        color:
                                            agent.completed
                                                ? "#80e9a4"
                                                : "#7e8796",

                                        fontWeight:
                                            "700"
                                    }}
                                >

                                    {
                                        agent.completed
                                            ? "✓"
                                            : index + 1
                                    }

                                </div>


                                <div>

                                    <strong>
                                        {
                                            agent.name
                                        }
                                    </strong>


                                    <p
                                        style={{
                                            color:
                                                "#8992a3",

                                            margin:
                                                "4px 0 0",

                                            fontSize:
                                                "13px"
                                        }}
                                    >

                                        {
                                            agent.description
                                        }

                                    </p>

                                </div>

                            </div>

                        )
                    )
                }

            </div>

        </div>
    );
};


export default AgentTrace;