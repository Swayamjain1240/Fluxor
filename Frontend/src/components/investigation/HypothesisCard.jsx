const HypothesisCard = ({
    hypothesis,
    index
}) => {

    const confidence =
        Math.round(
            (
                hypothesis
                    ?.confidence
                ||
                0
            )
            *
            100
        );


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

            <div
                style={{
                    display:
                        "flex",

                    justifyContent:
                        "space-between",

                    gap:
                        "20px",

                    marginBottom:
                        "16px"
                }}
            >

                <div>

                    <span
                        style={{
                            color:
                                "#7e8797",

                            fontSize:
                                "12px"
                        }}
                    >

                        HYPOTHESIS {index + 1}

                    </span>


                    <h3
                        style={{
                            margin:
                                "6px 0 0"
                        }}
                    >

                        {
                            hypothesis
                                ?.name
                        }

                    </h3>

                </div>


                <strong>

                    {confidence}%

                </strong>

            </div>


            <p
                style={{
                    color:
                        "#a0a8b7",

                    lineHeight:
                        "1.7"
                }}
            >

                {
                    hypothesis
                        ?.explanation
                }

            </p>


            <EvidenceList
                title="Supporting Evidence"

                items={
                    hypothesis
                        ?.supportingEvidence
                    ||
                    []
                }
            />


            <EvidenceList
                title="Contradicting Evidence"

                items={
                    hypothesis
                        ?.contradictingEvidence
                    ||
                    []
                }
            />

        </div>
    );
};


const EvidenceList = ({
    title,
    items
}) => {

    return (

        <div
            style={{
                marginTop:
                    "20px"
            }}
        >

            <h4
                style={{
                    marginBottom:
                        "10px"
                }}
            >

                {title}

            </h4>


            {
                items.length === 0
                    ? (

                        <p
                            style={{
                                color:
                                    "#777f8f"
                            }}
                        >

                            No evidence recorded.

                        </p>

                    )
                    : (

                        <ul
                            style={{
                                color:
                                    "#9ca5b5",

                                lineHeight:
                                    "1.7",

                                paddingLeft:
                                    "20px"
                            }}
                        >

                            {
                                items.map(
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
            }

        </div>
    );
};


export default HypothesisCard;