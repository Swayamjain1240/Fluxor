import {
    useState
} from "react";

import {
    submitValidation
} from "../../services/validationService.js";


const ValidationPanel = ({
    reportId,
    existingValidation = null,
    onValidated
}) => {

    const [
        decision,
        setDecision
    ] = useState("");


    const [
        notes,
        setNotes
    ] = useState("");


    const [
        loading,
        setLoading
    ] = useState(false);


    const [
        error,
        setError
    ] = useState("");


    const handleValidation = async () => {

        if (!decision) {

            setError(
                "Please choose Approve or Reject."
            );

            return;
        }


        try {

            setLoading(true);

            setError("");


            const data =
                await submitValidation({
                    reportId,
                    decision,
                    notes
                });


            if (onValidated) {

                onValidated(
                    data.validation
                    ||
                    data
                );
            }

        } catch (error) {

            setError(
                error.response
                    ?.data
                    ?.message
                ||
                "Failed to submit validation"
            );

        } finally {

            setLoading(false);
        }
    };


    if (existingValidation) {

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
                        marginTop: 0
                    }}
                >

                    Scientist Validation

                </h3>


                <div
                    style={{
                        display: "inline-block",
                        padding: "7px 12px",
                        borderRadius: "20px",

                        background:
                            existingValidation.decision === "approved"
                                ? "rgba(70, 200, 120, 0.15)"
                                : "rgba(220, 60, 60, 0.15)",

                        color:
                            existingValidation.decision === "approved"
                                ? "#7be49c"
                                : "#ff8585",

                        fontWeight: "700",
                        textTransform: "uppercase",
                        fontSize: "12px"
                    }}
                >

                    {existingValidation.decision}

                </div>


                {
                    existingValidation.notes && (

                        <p
                            style={{
                                marginTop: "18px",
                                color: "#a0a9b8",
                                lineHeight: "1.6"
                            }}
                        >

                            {
                                existingValidation.notes
                            }

                        </p>

                    )
                }

            </div>
        );
    }


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
                    margin: "0 0 8px"
                }}
            >

                Scientist Validation

            </h3>


            <p
                style={{
                    margin: "0 0 22px",
                    color: "#8992a3",
                    lineHeight: "1.6"
                }}
            >

                Review Fluxor's evidence and hypotheses before making
                the final scientific decision.

            </p>


            {error && (

                <div
                    style={{
                        padding: "12px",
                        marginBottom: "16px",
                        background: "rgba(220,60,60,0.15)",
                        color: "#ff8989",
                        borderRadius: "8px"
                    }}
                >

                    {error}

                </div>

            )}


            <div
                style={{
                    display: "flex",
                    gap: "12px",
                    marginBottom: "20px"
                }}
            >

                <button
                    onClick={() =>
                        setDecision(
                            "approved"
                        )
                    }
                    style={{
                        flex: 1,
                        padding: "13px",
                        borderRadius: "8px",

                        border:
                            decision === "approved"
                                ? "1px solid #70df9a"
                                : "1px solid #303744",

                        background:
                            decision === "approved"
                                ? "rgba(70, 200, 120, 0.18)"
                                : "#171c25",

                        color:
                            decision === "approved"
                                ? "#80e8a4"
                                : "#a0a8b6",

                        cursor: "pointer",
                        fontWeight: "700"
                    }}
                >

                    Approve

                </button>


                <button
                    onClick={() =>
                        setDecision(
                            "rejected"
                        )
                    }
                    style={{
                        flex: 1,
                        padding: "13px",
                        borderRadius: "8px",

                        border:
                            decision === "rejected"
                                ? "1px solid #ff7777"
                                : "1px solid #303744",

                        background:
                            decision === "rejected"
                                ? "rgba(220, 60, 60, 0.18)"
                                : "#171c25",

                        color:
                            decision === "rejected"
                                ? "#ff8585"
                                : "#a0a8b6",

                        cursor: "pointer",
                        fontWeight: "700"
                    }}
                >

                    Reject

                </button>

            </div>


            <textarea
                value={notes}

                onChange={(event) =>
                    setNotes(
                        event.target.value
                    )
                }

                placeholder="Scientist notes..."

                style={{
                    width: "100%",
                    minHeight: "120px",
                    padding: "14px",
                    background: "#0d1118",
                    color: "#ffffff",
                    border: "1px solid #303744",
                    borderRadius: "8px",
                    resize: "vertical",
                    outline: "none",
                    fontFamily: "inherit"
                }}
            />


            <button
                onClick={
                    handleValidation
                }

                disabled={
                    loading
                }

                style={{
                    marginTop: "16px",
                    padding: "12px 20px",
                    border: "none",
                    borderRadius: "8px",

                    background:
                        loading
                            ? "#343b48"
                            : "#f4f6f8",

                    color:
                        loading
                            ? "#939ba9"
                            : "#11151d",

                    cursor:
                        loading
                            ? "not-allowed"
                            : "pointer",

                    fontWeight: "700"
                }}
            >

                {
                    loading
                        ? "Submitting..."
                        : "Submit Validation"
                }

            </button>

        </div>
    );
};


export default ValidationPanel;