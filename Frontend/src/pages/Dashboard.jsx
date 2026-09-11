import {
    useEffect,
    useState
} from "react";

import StatCard from "../components/dashboard/StatCard.jsx";
import RecentActivity from "../components/dashboard/RecentActivity.jsx";
import Loader from "../components/Loader.jsx";

import {
    getDashboardSummary,
    getRecentActivity
} from "../services/dashboardService.js";


const Dashboard = () => {

    const [summary, setSummary] =
        useState(null);

    const [activity, setActivity] =
        useState(null);

    const [loading, setLoading] =
        useState(true);

    const [error, setError] =
        useState("");


    useEffect(() => {

        const loadDashboard = async () => {

            try {

                const [
                    summaryData,
                    activityData
                ] = await Promise.all([

                    getDashboardSummary(),

                    getRecentActivity()

                ]);


                setSummary(
                    summaryData.summary
                );


                setActivity(
                    activityData.activity
                );

            } catch (error) {

                setError(
                    error.response
                        ?.data
                        ?.message
                    ||
                    "Failed to load dashboard"
                );

            } finally {

                setLoading(false);
            }
        };


        loadDashboard();

    }, []);


    if (loading) {

        return (
            <Loader
                text="Loading dashboard..."
            />
        );
    }


    if (error) {

        return (
            <div className="error-box">
                {error}
            </div>
        );
    }


    return (

        <div>

            <div className="page-header">

                <div>

                    <h1>
                        Research Dashboard
                    </h1>

                    <p>
                        Overview of Fluxor scientific activity
                    </p>

                </div>

            </div>


            <div className="stats-grid">

                <StatCard
                    title="Datasets"
                    value={
                        summary?.datasets ?? 0
                    }
                />

                <StatCard
                    title="Candidates"
                    value={
                        summary?.candidates ?? 0
                    }
                />

                <StatCard
                    title="High Priority"
                    value={
                        summary?.highPriority ?? 0
                    }
                />

                <StatCard
                    title="Investigations"
                    value={
                        summary?.investigations ?? 0
                    }
                />

                <StatCard
                    title="Approved"
                    value={
                        summary?.approved ?? 0
                    }
                />

                <StatCard
                    title="Rejected"
                    value={
                        summary?.rejected ?? 0
                    }
                />

            </div>


            <RecentActivity
                investigations={
                    activity
                        ?.recentInvestigations
                    ||
                    []
                }

                validations={
                    activity
                        ?.recentValidations
                    ||
                    []
                }
            />

        </div>
    );
};


export default Dashboard;