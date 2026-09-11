import {
    Outlet
} from "react-router-dom";

import Navbar from "./Navbar.jsx";
import Sidebar from "./Sidebar.jsx";


const AppLayout = () => {

    return (
        <div className="app-layout">

            <Sidebar />

            <div className="main-section">

                <Navbar />

                <main className="main-content">

                    <Outlet />

                </main>

            </div>

        </div>
    );
};


export default AppLayout;