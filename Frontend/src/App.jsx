import {
    BrowserRouter,
    Routes,
    Route,
    Navigate
} from "react-router-dom";

import Login from "./pages/Login";
import Signup from "./pages/Signup";

import Dashboard from "./pages/Dashboard";
import Datasets from "./pages/Datasets";
import DatasetDetail from "./pages/DatasetDetail";

import Candidates from "./pages/Candidates.jsx";
import CandidateDetail from "./pages/CandidateDetail.jsx";

import ProtectedRoute from "./components/ProtectedRoute";
import AppLayout from "./components/AppLayout";


const App = () => {

    return (

        <BrowserRouter>

            <Routes>

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

                </Route>


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