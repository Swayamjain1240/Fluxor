import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyDetector:

    def __init__(self,contamination="auto",random_state=42):
        self.model = IsolationForest(
            n_estimators=200,
            contamination=contamination,
            random_state=random_state,
            n_jobs=-1
        )

    def detect(
        self,
        feature_vectors,
        windows
    ):

        if len(feature_vectors) < 5:
            raise ValueError(
                "At least 5 feature samples are required"
            )


        # Train + classify
        labels = self.model.fit_predict(
            feature_vectors
        )


        # Lower = more abnormal
        decision_scores = (
            self.model.decision_function(
                feature_vectors
            )
        )


        results = []


        for index, window in enumerate(windows):

            decision = float(
                decision_scores[index]
            )


            # Convert decision score into
            # convenient 0..1 anomaly score.
            #
            # IMPORTANT:
            # This is NOT a calibrated probability.

            anomaly_score = (
                1
                /
                (
                    1
                    +
                    np.exp(
                        8 * decision
                    )
                )
            )


            result = {
                **window,

                "isAnomaly":
                    bool(
                        labels[index] == -1
                    ),

                "decisionScore":
                    decision,

                "anomalyScore":
                    float(anomaly_score),
            }


            results.append(result)


        # Most suspicious first
        results.sort(
            key=lambda item:
                item["anomalyScore"],

            reverse=True
        )


        anomalous_windows = [
            item
            for item in results
            if item["isAnomaly"]
        ]


        if anomalous_windows:

            overall_score = (
                anomalous_windows[0][
                    "anomalyScore"
                ]
            )

            is_anomalous = True

        else:

            overall_score = 0.0

            is_anomalous = False


        priority = self._get_priority(
            overall_score
        )


        return {
            "isAnomalous":
                is_anomalous,

            "anomalyScore":
                round(
                    float(overall_score),
                    4
                ),

            "priority":
                priority,

            "anomalousWindows":
                anomalous_windows[:10],

            "totalWindows":
                len(results),
        }


    @staticmethod
    def _get_priority(score):

        if score >= 0.80:
            return "HIGH"

        if score >= 0.60:
            return "MEDIUM"

        return "LOW"