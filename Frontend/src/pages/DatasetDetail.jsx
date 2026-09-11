import {
    useEffect,
    useState
} from "react";

import {
    Link,
    useParams
} from "react-router-dom";

import Loader from "../components/Loader.jsx";

import {
    getDatasetById
} from "../services/datasetService.js";


const DatasetDetail = () => {

    const {
        datasetId
    } = useParams();


    const [dataset, setDataset] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");


    useEffect(() => {

        const loadDataset = async () => {

            try {

                const data =
                    await getDatasetById(
                        datasetId
                    );


                setDataset(
                    data.dataset
                );

            } catch (error) {

                setError(
                    error.response
                        ?.data
                        ?.message
                    ||
                    "Dataset not found"
                );

            } finally {

                setLoading(false);
            }
        };


        loadDataset();

    }, [datasetId]);


    if (loading) {

        return (
            <Loader
                text="Loading dataset..."
            />
        );
    }


    if (error) {

        return (
            <div className="error-box">
                {error}
            </div>
        );
    }


    return (

        <div>

            <Link
                to="/datasets"
                className="back-link"
            >
                ← Back to Datasets
            </Link>


            <div className="detail-card">

                <div className="detail-header">

                    <div>

                        <span className="source-badge">
                            {dataset.source}
                        </span>

                        <h1>
                            {dataset.name}
                        </h1>

                    </div>


                    <span className="dataset-status">
                        {dataset.status}
                    </span>

                </div>


                <div className="detail-grid">

                    <div>

                        <span>
                            Object ID
                        </span>

                        <strong>
                            {dataset.objectId}
                        </strong>

                    </div>


                    <div>

                        <span>
                            Source
                        </span>

                        <strong>
                            {dataset.source}
                        </strong>

                    </div>


                    <div>

                        <span>
                            Created
                        </span>

                        <strong>

                            {
                                new Date(
                                    dataset.createdAt
                                ).toLocaleString()
                            }

                        </strong>

                    </div>


                    <div>

                        <span>
                            Status
                        </span>

                        <strong>
                            {dataset.status}
                        </strong>

                    </div>

                </div>


                <div className="description-box">

                    <h3>
                        Description
                    </h3>

                    <p>
                        {
                            dataset.description
                            ||
                            "No description provided."
                        }
                    </p>

                </div>


                <div className="future-action">

                    Anomaly detection will be available in Part 3.

                </div>

            </div>

        </div>
    );
};


export default DatasetDetail;