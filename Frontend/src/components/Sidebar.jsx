import {
    NavLink
} from "react-router-dom";


const Sidebar = () => {

    return (

        <aside className="sidebar">

            <div className="sidebar-brand">

                <h2>
                    FLUXOR
                </h2>

                <span>
                    Scientific Intelligence
                </span>

            </div>


            <nav className="sidebar-nav">

                <NavLink
                    to="/dashboard"
                    className={({ isActive }) =>
                        isActive
                            ? "nav-link active"
                            : "nav-link"
                    }
                >
                    Dashboard
                </NavLink>


                <NavLink
                    to="/datasets"
                    className={({ isActive }) =>
                        isActive
                            ? "nav-link active"
                            : "nav-link"
                    }
                >
                    Datasets
                </NavLink>

            </nav>

        </aside>
    );
};


export default Sidebar;