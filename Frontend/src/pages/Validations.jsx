import {
    useEffect,
    useState
} from "react";

import {
    getValidations
} from "../services/validationService.js";

import Loader from "../components/Loader.jsx";


const Validations = () => {

    const [
        validations,
        setValidations
    ] = useState([]);


    const [
        loading,
        setLoading
    ] = useState(true);


    const [
        error,
        setError
    ] = useState("");


    useEffect(() => {

        const loadValidations = async () => {

            try {

                const data =
                    await getValidations();


                setValidations(
                    data.validations
                    ||
                    []
                );

            } catch (error) {

                setError(
                    error.response
                        ?.data
                        ?.message
                    ||
                    "Failed to load validations"
                );

            } finally {

                setLoading(false);
            }
        };


        loadValidations();

    }, []);


    if (loading) {

        return (

            <Loader
                text="Loading validations..."
            />

        );
    }


    return (

        <div>

            <div
                style={{
                    marginBottom: "28px"
                }}
            >

                <h1
                    style={{
                        margin: "0 0 8px"
                    }}
                >

                    Scientist Validations

                </h1>


                <p
                    style={{
                        margin: 0,
                        color: "#8992a3"
                    }}
                >

                    Human review decisions for Fluxor-generated scientific reports.

                </p>

            </div>


            {error && (

                <div
                    style={{
                        padding: "14px",
                        marginBottom: "20px",
                        background: "rgba(220,60,60,0.15)",
                        color: "#ff8989",
                        borderRadius: "8px"
                    }}
                >

                    {error}

                </div>

            )}


            {
                validations.length === 0
                    ? (

                        <div
                            style={{
                                padding: "50px",
                                textAlign: "center",
                                background: "#11151d",
                                border: "1px solid #272d39",
                                borderRadius: "12px",
                                color: "#8992a3"
                            }}
                        >

                            No scientist validations yet.

                        </div>

                    )
                    : (

                        <div
                            style={{
                                display: "grid",
                                gap: "14px"
                            }}
                        >

                            {
                                validations.map(
                                    (
                                        validation
                                    ) => (

                                        <div
                                            key={
                                                validation._id
                                            }

                                            style={{
                                                padding: "20px",
                                                background: "#11151d",
                                                border: "1px solid #272d39",
                                                borderRadius: "10px"
                                            }}
                                        >

                                            <div
                                                style={{
                                                    display: "flex",
                                                    justifyContent: "space-between",
                                                    alignItems: "center",
                                                    gap: "20px"
                                                }}
                                            >

                                                <strong>

                                                    Report Review

                                                </strong>


                                                <span
                                                    style={{
                                                        padding: "6px 11px",
                                                        borderRadius: "20px",

                                                        background:
                                                            validation.decision === "approved"
                                                                ? "rgba(70,200,120,0.15)"
                                                                : "rgba(220,60,60,0.15)",

                                                        color:
                                                            validation.decision === "approved"
                                                                ? "#7be49c"
                                                                : "#ff8585",

                                                        textTransform: "uppercase",
                                                        fontSize: "11px",
                                                        fontWeight: "700"
                                                    }}
                                                >

                                                    {
                                                        validation.decision
                                                    }

                                                </span>

                                            </div>


                                            <p
                                                style={{
                                                    color: "#8992a3",
                                                    marginBottom: 0,
                                                    lineHeight: "1.6"
                                                }}
                                            >

                                                {
                                                    validation.notes
                                                    ||
                                                    "No scientist notes."
                                                }

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


export default Validations;