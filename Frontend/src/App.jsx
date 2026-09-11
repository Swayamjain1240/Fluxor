import {
    BrowserRouter,
    Navigate,
    Route,
    Routes
} from "react-router-dom";

import Login from "./pages/Login.jsx";
import Signup from "./pages/Signup.jsx";

import Dashboard from "./pages/Dashboard.jsx";

import Datasets from "./pages/Datasets.jsx";
import DatasetDetail from "./pages/DatasetDetail.jsx";

import Candidates from "./pages/Candidates.jsx";
import CandidateDetail from "./pages/CandidateDetail.jsx";

import Investigations from "./pages/Investigations.jsx";
import Investigation from "./pages/Investigation.jsx";

import Report from "./pages/Report.jsx";

import Validations from "./pages/Validations.jsx";

import ProtectedRoute from "./components/ProtectedRoute.jsx";
import AppLayout from "./components/AppLayout.jsx";


const App = () => {

    return (

        <BrowserRouter>

            <Routes>

                {/* ========================= */}
                {/* Public Routes */}
                {/* ========================= */}

                <Route
                    path="/login"
                    element={
                        <Login />
                    }
                />


                <Route
                    path="/signup"
                    element={
                        <Signup />
                    }
                />


                {/* ========================= */}
                {/* Protected Application */}
                {/* ========================= */}

                <Route
                    element={

                        <ProtectedRoute>

                            <AppLayout />

                        </ProtectedRoute>

                    }
                >

                    <Route
                        path="/dashboard"
                        element={
                            <Dashboard />
                        }
                    />


                    <Route
                        path="/datasets"
                        element={
                            <Datasets />
                        }
                    />


                    <Route
                        path="/datasets/:datasetId"
                        element={
                            <DatasetDetail />
                        }
                    />


                    <Route
                        path="/candidates"
                        element={
                            <Candidates />
                        }
                    />


                    <Route
                        path="/candidates/:candidateId"
                        element={
                            <CandidateDetail />
                        }
                    />


                    <Route
                        path="/investigations"
                        element={
                            <Investigations />
                        }
                    />


                    <Route
                        path="/investigations/:investigationId"
                        element={
                            <Investigation />
                        }
                    />


                    <Route
                        path="/reports/:reportId"
                        element={
                            <Report />
                        }
                    />


                    <Route
                        path="/validations"
                        element={
                            <Validations />
                        }
                    />

                </Route>


                {/* ========================= */}
                {/* Redirects */}
                {/* ========================= */}

                <Route
                    path="/"
                    element={

                        <Navigate
                            to="/dashboard"
                            replace
                        />

                    }
                />


                <Route
                    path="*"
                    element={

                        <Navigate
                            to="/dashboard"
                            replace
                        />

                    }
                />

            </Routes>

        </BrowserRouter>
    );
};


export default App;