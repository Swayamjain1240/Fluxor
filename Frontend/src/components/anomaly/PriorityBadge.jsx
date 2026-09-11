const PriorityBadge = ({ priority }) => {

    const getStyle = () => {

        switch (priority) {

            case "HIGH":

                return {
                    background: "rgba(255, 80, 80, 0.15)",
                    color: "#ff7b7b",
                    border: "1px solid rgba(255, 80, 80, 0.35)"
                };


            case "MEDIUM":

                return {
                    background: "rgba(255, 190, 70, 0.15)",
                    color: "#ffc761",
                    border: "1px solid rgba(255, 190, 70, 0.35)"
                };


            default:

                return {
                    background: "rgba(90, 180, 255, 0.15)",
                    color: "#7bc8ff",
                    border: "1px solid rgba(90, 180, 255, 0.35)"
                };
        }
    };


    return (

        <span
            style={{
                ...getStyle(),

                padding: "5px 10px",

                borderRadius: "20px",

                fontSize: "12px",

                fontWeight: "600"
            }}
        >
            {priority || "LOW"}
        </span>
    );
};


export default PriorityBadge;