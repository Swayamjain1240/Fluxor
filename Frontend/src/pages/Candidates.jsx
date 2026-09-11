import {
    useEffect,
    useState
} from "react";

import {
    getCandidates
} from "../services/anomalyService.js";

import CandidateTable from "../components/anomaly/CandidateTable.jsx";
import Loader from "../components/Loader.jsx";


const Candidates = () => {

    const [
        candidates,
        setCandidates
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

        const loadCandidates = async () => {

            try {

                const data =
                    await getCandidates();


                setCandidates(
                    data.candidates || []
                );

            } catch (error) {

                setError(
                    error.response
                        ?.data
                        ?.message
                    ||
                    "Failed to load candidates"
                );

            } finally {

                setLoading(false);
            }
        };


        loadCandidates();

    }, []);


    if (loading) {

        return (

            <Loader
                text="Loading candidates..."
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
                        marginBottom: "8px"
                    }}
                >

                    Anomaly Candidates

                </h1>


                <p
                    style={{
                        color: "#8991a1"
                    }}
                >

                    Astronomical objects ranked by Fluxor's ML anomaly detector.

                </p>

            </div>


            {error && (

                <div
                    style={{
                        padding: "14px",

                        background:
                            "rgba(200,50,50,0.15)",

                        color: "#ff8c8c",

                        borderRadius: "8px",

                        marginBottom: "20px"
                    }}
                >

                    {error}

                </div>

            )}


            {
                candidates.length === 0
                    ? (

                        <div
                            style={{
                                padding: "50px",

                                textAlign: "center",

                                background:
                                    "#11151d",

                                border:
                                    "1px solid #272d39",

                                borderRadius:
                                    "12px",

                                color:
                                    "#8991a1"
                            }}
                        >

                            No anomaly candidates detected yet.

                        </div>

                    )
                    : (

                        <CandidateTable
                            candidates={
                                candidates
                            }
                        />

                    )
            }

        </div>
    );
};


export default Candidates;