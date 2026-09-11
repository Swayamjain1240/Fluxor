import {
    useEffect,
    useState
} from "react";

import {
    Link,
    useParams
} from "react-router-dom";

import {
    getReportById
} from "../services/reportService.js";

import Loader from "../components/Loader.jsx";

import ScientificReport from "../components/report/ScientificReport.jsx";

import FollowupPlan from "../components/report/FollowupPlan.jsx";

import ValidationPanel from "../components/report/ValidationPanel.jsx";


const Report = () => {

    const {
        reportId
    } = useParams();


    const [
        report,
        setReport
    ] = useState(null);


    const [
        validation,
        setValidation
    ] = useState(null);


    const [
        loading,
        setLoading
    ] = useState(true);


    const [
        error,
        setError
    ] = useState("");


    useEffect(() => {

        const loadReport = async () => {

            try {

                const data =
                    await getReportById(
                        reportId
                    );


                const reportData =
                    data.report
                    ||
                    data;


                setReport(
                    reportData
                );


                setValidation(
                    reportData.validation
                    ||
                    data.validation
                    ||
                    null
                );

            } catch (error) {

                setError(
                    error.response
                        ?.data
                        ?.message
                    ||
                    "Failed to load report"
                );

            } finally {

                setLoading(false);
            }
        };


        loadReport();

    }, [reportId]);


    if (loading) {

        return (

            <Loader
                text="Loading scientific report..."
            />

        );
    }


    if (error) {

        return (

            <div
                style={{
                    padding: "16px",
                    background: "rgba(220,60,60,0.15)",
                    color: "#ff8989",
                    borderRadius: "8px"
                }}
            >

                {error}

            </div>

        );
    }


    return (

        <div>

            <Link
                to="/investigations"

                style={{
                    display: "inline-block",
                    marginBottom: "22px",
                    color: "#aab3c4",
                    textDecoration: "none"
                }}
            >

                ← Back to Investigations

            </Link>


            <div
                style={{
                    marginBottom: "28px"
                }}
            >

                <p
                    style={{
                        margin: "0 0 7px",
                        color: "#7f8999",
                        fontSize: "12px",
                        letterSpacing: "1px",
                        textTransform: "uppercase"
                    }}
                >

                    Fluxor Research Output

                </p>


                <h1
                    style={{
                        margin: 0
                    }}
                >

                    Scientific Report

                </h1>

            </div>


            <div
                style={{
                    display: "grid",
                    gap: "24px"
                }}
            >

                <ScientificReport
                    reportMarkdown={
                        report?.reportMarkdown
                        ||
                        report?.markdown
                        ||
                        ""
                    }
                />


                <FollowupPlan
                    followupPlan={
                        report?.followupPlan
                        ||
                        []
                    }
                />


                <ValidationPanel
                    reportId={
                        report?._id
                        ||
                        reportId
                    }

                    existingValidation={
                        validation
                    }

                    onValidated={(
                        newValidation
                    ) => {

                        setValidation(
                            newValidation
                        );
                    }}
                />

            </div>

        </div>
    );
};


export default Report;