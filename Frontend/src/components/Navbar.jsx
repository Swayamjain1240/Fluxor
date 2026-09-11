import {
    useNavigate
} from "react-router-dom";

import useAuth from "../hooks/useAuth.js";


const Navbar = () => {

    const navigate =
        useNavigate();

    const {
        user,
        logout
    } = useAuth();


    const handleLogout = async () => {

        await logout();

        navigate(
            "/login"
        );
    };


    return (

        <header className="navbar">

            <div>

                <p className="navbar-label">
                    Astronomical Research Platform
                </p>

            </div>


            <div className="navbar-user">

                <div>

                    <strong>
                        {user?.name}
                    </strong>

                    <span>
                        {user?.email}
                    </span>

                </div>


                <button
                    onClick={
                        handleLogout
                    }
                    className="logout-button"
                >

                    Logout

                </button>

            </div>

        </header>
    );
};


export default Navbar;