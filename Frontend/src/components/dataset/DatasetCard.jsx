import {
    Link
} from "react-router-dom";


const DatasetCard = ({
    dataset,
    onDelete
}) => {

    return (

        <div className="dataset-card">

            <div>

                <span className="source-badge">
                    {dataset.source}
                </span>


                <h3>
                    {dataset.name}
                </h3>


                <p>
                    Object: {dataset.objectId}
                </p>


                <p className="muted">
                    {
                        dataset.description
                        ||
                        "No description"
                    }
                </p>


                <span className="dataset-status">
                    {dataset.status}
                </span>

            </div>


            <div className="dataset-actions">

                <Link
                    to={
                        `/datasets/${dataset._id}`
                    }
                >
                    View
                </Link>


                <button
                    onClick={() =>
                        onDelete(
                            dataset._id
                        )
                    }
                >
                    Delete
                </button>

            </div>

        </div>
    );
};


export default DatasetCard;