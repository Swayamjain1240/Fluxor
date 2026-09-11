import {
    useState
} from "react";

import {
    Link,
    useNavigate
} from "react-router-dom";

import {
    signupUser
} from "../services/authService.js";


const Signup = () => {

    const navigate =
        useNavigate();


    const [form, setForm] =
        useState({
            name: "",
            email: "",
            password: ""
        });


    const [error, setError] =
        useState("");

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

        setError("");


        try {

            await signupUser(
                form
            );


            navigate(
                "/login"
            );

        } catch (error) {

            setError(
                error.response?.data?.message
                ||
                "Signup failed"
            );

        } finally {

            setLoading(false);
        }
    };


    return (

        <div className="auth-page">

            <div className="auth-card">

                <h1>Fluxor</h1>

                <h2>
                    Create Scientist Account
                </h2>


                {error && (

                    <p className="error">
                        {error}
                    </p>

                )}


                <form
                    onSubmit={
                        handleSubmit
                    }
                >

                    <input
                        type="text"
                        name="name"
                        placeholder="Name"
                        value={
                            form.name
                        }
                        onChange={
                            handleChange
                        }
                        required
                    />


                    <input
                        type="email"
                        name="email"
                        placeholder="Email"
                        value={
                            form.email
                        }
                        onChange={
                            handleChange
                        }
                        required
                    />


                    <input
                        type="password"
                        name="password"
                        placeholder="Password"
                        value={
                            form.password
                        }
                        onChange={
                            handleChange
                        }
                        required
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
                            : "Signup"
                        }

                    </button>

                </form>


                <p>

                    Already have an account?{" "}

                    <Link to="/login">
                        Login
                    </Link>

                </p>

            </div>

        </div>
    );
};


export default Signup;