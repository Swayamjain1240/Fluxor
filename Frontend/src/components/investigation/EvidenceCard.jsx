const EvidenceCard = ({
    evidence
}) => {

    if (!evidence) {

        return null;
    }


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
                    marginTop:
                        0
                }}
            >

                Scientific Evidence

            </h3>


            <EvidenceSection
                title="Catalog Evidence"

                data={
                    evidence.catalog
                }
            />


            <EvidenceSection
                title="Historical Evidence"

                data={
                    evidence.historical
                }
            />


            <EvidenceSection
                title="Literature / RAG Evidence"

                data={
                    evidence.literature
                }
            />

        </div>
    );
};


const EvidenceSection = ({
    title,
    data
}) => {

    return (

        <div
            style={{
                marginTop:
                    "22px",

                paddingTop:
                    "18px",

                borderTop:
                    "1px solid #252b36"
            }}
        >

            <h4>
                {title}
            </h4>


            {
                !data
                    ? (

                        <p
                            style={{
                                color:
                                    "#7e8797"
                            }}
                        >

                            No evidence available.

                        </p>

                    )
                    : (

                        <pre
                            style={{
                                whiteSpace:
                                    "pre-wrap",

                                wordBreak:
                                    "break-word",

                                background:
                                    "#0d1118",

                                padding:
                                    "15px",

                                borderRadius:
                                    "8px",

                                color:
                                    "#aeb7c7",

                                fontSize:
                                    "12px",

                                overflowX:
                                    "auto"
                            }}
                        >

                            {
                                JSON.stringify(
                                    data,
                                    null,
                                    2
                                )
                            }

                        </pre>

                    )
            }

        </div>
    );
};


export default EvidenceCard;