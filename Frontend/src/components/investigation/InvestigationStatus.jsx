const InvestigationStatus = ({
    status = "unknown"
}) => {

    const statusUpper =
        status.toUpperCase();


    const getStatusStyle = () => {

        switch (statusUpper) {

            case "COMPLETED":

                return {
                    background:
                        "rgba(75, 200, 120, 0.15)",

                    color:
                        "#7be49c",

                    border:
                        "1px solid rgba(75, 200, 120, 0.3)"
                };


            case "NEEDS_REVIEW":

                return {
                    background:
                        "rgba(255, 190, 60, 0.15)",

                    color:
                        "#ffc761",

                    border:
                        "1px solid rgba(255, 190, 60, 0.3)"
                };


            case "FAILED":

                return {
                    background:
                        "rgba(220, 60, 60, 0.15)",

                    color:
                        "#ff8585",

                    border:
                        "1px solid rgba(220, 60, 60, 0.3)"
                };


            default:

                return {
                    background:
                        "#202733",

                    color:
                        "#aeb8c9",

                    border:
                        "1px solid #343c4a"
                };
        }
    };


    return (

        <span
            style={{
                ...getStatusStyle(),

                padding:
                    "6px 12px",

                borderRadius:
                    "20px",

                fontSize:
                    "12px",

                fontWeight:
                    "700"
            }}
        >

            {statusUpper}

        </span>
    );
};


export default InvestigationStatus;