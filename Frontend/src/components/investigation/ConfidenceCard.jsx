const ConfidenceCard = ({
    confidence = 0,
    iterationCount = 0
}) => {

    const percentage =
        Math.round(
            confidence * 100
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

            <h3
                style={{
                    margin:
                        "0 0 20px"
                }}
            >

                AI Confidence

            </h3>


            <div
                style={{
                    fontSize:
                        "34px",

                    fontWeight:
                        "700",

                    marginBottom:
                        "14px"
                }}
            >

                {percentage}%

            </div>


            <div
                style={{
                    width:
                        "100%",

                    height:
                        "10px",

                    background:
                        "#242a34",

                    borderRadius:
                        "20px",

                    overflow:
                        "hidden"
                }}
            >

                <div
                    style={{
                        width:
                            `${percentage}%`,

                        height:
                            "100%",

                        background:
                            percentage >= 72
                                ? "#66d28f"
                                : "#d7ae59",

                        transition:
                            "width 0.4s"
                    }}
                />

            </div>


            <p
                style={{
                    color:
                        "#8992a3",

                    marginBottom:
                        0,

                    marginTop:
                        "16px"
                }}
            >

                Reasoning Iterations:{" "}

                <strong
                    style={{
                        color:
                            "#ffffff"
                    }}
                >
                    {iterationCount} / 3
                </strong>

            </p>

        </div>
    );
};


export default ConfidenceCard;