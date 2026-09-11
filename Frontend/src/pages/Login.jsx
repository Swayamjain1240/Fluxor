import {
    useState
} from "react";

import {
    Link,
    useNavigate
} from "react-router-dom";

import useAuth from "../hooks/useAuth.js";


const Login = () => {

    const navigate = useNavigate();

    const { login } = useAuth();


    const [form, setForm] =
        useState({
            email: "",
            password: ""
        });


    const [error, setError] =
        useState("");

    const [loading, setLoading] =
        useState(false);


    const handleChange = (event) => {

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

        setError("");

        setLoading(true);


        try {

            await login(
                form.email,
                form.password
            );


            navigate(
                "/dashboard"
            );

        } catch (error) {

            setError(
                error.response?.data?.message
                ||
                "Login failed"
            );

        } finally {

            setLoading(false);
        }
    };


    return (

        <div className="auth-page">

            <div className="auth-card">

                <h1>Fluxor</h1>

                <p>
                    Astronomical Research Platform
                </p>


                <h2>
                    Scientist Login
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
                            ? "Logging in..."
                            : "Login"
                        }

                    </button>

                </form>


                <p>

                    Don't have an account?{" "}

                    <Link to="/signup">
                        Signup
                    </Link>

                </p>

            </div>

        </div>
    );
};


export default Login;