import {
    useEffect,
    useState
} from "react";

import DatasetForm from "../components/dataset/DatasetForm.jsx";
import DatasetCard from "../components/dataset/DatasetCard.jsx";
import Loader from "../components/Loader.jsx";

import {
    createDataset,
    getDatasets,
    deleteDataset
} from "../services/datasetService.js";


const Datasets = () => {

    const [datasets, setDatasets] =
        useState([]);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");


    const loadDatasets = async () => {

        try {

            const data =
                await getDatasets();


            setDatasets(
                data.datasets || []
            );

        } catch (error) {

            setError(
                error.response
                    ?.data
                    ?.message
                ||
                "Failed to load datasets"
            );

        } finally {

            setLoading(false);
        }
    };


    useEffect(() => {

        loadDatasets();

    }, []);


    const handleCreate = async (
        form
    ) => {

        try {

            const data =
                await createDataset(
                    form
                );


            setDatasets(
                (current) => [
                    data.dataset,
                    ...current
                ]
            );

        } catch (error) {

            setError(
                error.response
                    ?.data
                    ?.message
                ||
                "Failed to create dataset"
            );

            throw error;
        }
    };


    const handleDelete = async (
        datasetId
    ) => {

        const confirmed =
            window.confirm(
                "Delete this dataset?"
            );


        if (!confirmed) {
            return;
        }


        try {

            await deleteDataset(
                datasetId
            );


            setDatasets(
                (current) =>
                    current.filter(
                        (dataset) =>
                            dataset._id
                            !==
                            datasetId
                    )
            );

        } catch (error) {

            setError(
                error.response
                    ?.data
                    ?.message
                ||
                "Failed to delete dataset"
            );
        }
    };


    if (loading) {

        return (
            <Loader
                text="Loading datasets..."
            />
        );
    }


    return (

        <div>

            <div className="page-header">

                <div>

                    <h1>
                        Datasets
                    </h1>

                    <p>
                        Register astronomical targets for Fluxor analysis.
                    </p>

                </div>

            </div>


            {error && (

                <div className="error-box">
                    {error}
                </div>

            )}


            <DatasetForm
                onCreate={
                    handleCreate
                }
            />


            <div className="dataset-grid">

                {
                    datasets.length === 0
                    ? (

                        <div className="empty-state">

                            <h3>
                                No datasets yet
                            </h3>

                            <p>
                                Register your first astronomical target.
                            </p>

                        </div>

                    )
                    : (

                        datasets.map(
                            (dataset) => (

                                <DatasetCard
                                    key={
                                        dataset._id
                                    }

                                    dataset={
                                        dataset
                                    }

                                    onDelete={
                                        handleDelete
                                    }
                                />

                            )
                        )

                    )
                }

            </div>

        </div>
    );
};


export default Datasets;