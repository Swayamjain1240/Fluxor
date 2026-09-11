const RecentActivity = ({
    investigations = [],
    validations = []
}) => {

    return (

        <div className="activity-panel">

            <h3>
                Recent Activity
            </h3>


            <div className="activity-section">

                <h4>
                    Investigations
                </h4>


                {investigations.length === 0 ? (

                    <p className="muted">
                        No investigations yet.
                    </p>

                ) : (

                    investigations.map(
                        (item) => (

                            <div
                                key={item._id}
                                className="activity-item"
                            >

                                <span>
                                    {
                                        item.candidateId
                                            ?.objectId
                                        ||
                                        "Candidate"
                                    }
                                </span>

                                <span>
                                    {item.status}
                                </span>

                            </div>

                        )
                    )

                )}

            </div>


            <div className="activity-section">

                <h4>
                    Validations
                </h4>


                {validations.length === 0 ? (

                    <p className="muted">
                        No validations yet.
                    </p>

                ) : (

                    validations.map(
                        (item) => (

                            <div
                                key={item._id}
                                className="activity-item"
                            >

                                <span>
                                    {
                                        item.candidateId
                                            ?.objectId
                                        ||
                                        "Candidate"
                                    }
                                </span>

                                <span>
                                    {item.decision}
                                </span>

                            </div>

                        )
                    )

                )}

            </div>

        </div>
    );
};


export default RecentActivity;