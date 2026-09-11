import {
    useState
} from "react";


const DatasetForm = ({
    onCreate
}) => {

    const [form, setForm] =
        useState({
            name: "",
            source: "TESS",
            objectId: "",
            description: ""
        });


    const [loading, setLoading] =
        useState(false);


    const handleChange = (
        event
    ) => {

        setForm({

            ...form,

            [event.target.name]:
                event.target.value

        });
    };


    const handleSubmit = async (
        event
    ) => {

        event.preventDefault();

        setLoading(true);


        try {

            await onCreate(
                form
            );


            setForm({
                name: "",
                source: "TESS",
                objectId: "",
                description: ""
            });

        } finally {

            setLoading(false);
        }
    };


    return (

        <form
            className="dataset-form"
            onSubmit={
                handleSubmit
            }
        >

            <h3>
                Register Dataset
            </h3>


            <input
                type="text"
                name="name"
                placeholder="Dataset name"
                value={
                    form.name
                }
                onChange={
                    handleChange
                }
                required
            />


            <select
                name="source"
                value={
                    form.source
                }
                onChange={
                    handleChange
                }
            >

                <option value="TESS">
                    TESS
                </option>

                <option value="KEPLER">
                    Kepler
                </option>

                <option value="K2">
                    K2
                </option>

            </select>


            <input
                type="text"
                name="objectId"
                placeholder="Object ID e.g. TIC 307210830"
                value={
                    form.objectId
                }
                onChange={
                    handleChange
                }
                required
            />


            <textarea
                name="description"
                placeholder="Description"
                value={
                    form.description
                }
                onChange={
                    handleChange
                }
            />


            <button
                type="submit"
                disabled={
                    loading
                }
            >

                {
                    loading
                        ? "Creating..."
                        : "Create Dataset"
                }

            </button>

        </form>
    );
};


export default DatasetForm;