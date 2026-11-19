from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)


def evaluateMl(
    yTrue,
    yPred,
    scores=None
):
    """
    0 = Normal
    1 = Anomaly

    scores: optional continuous anomaly scores where HIGHER means MORE anomalous.
    When supplied, ROC-AUC and PR-AUC are added.
    """

    if len(yTrue) != len(yPred):
        raise ValueError(
            "yTrue and yPred must have equal length"
        )

    if len(yTrue) == 0:
        raise ValueError(
            "Evaluation data cannot be empty"
        )

    if len(set(int(v) for v in yTrue)) == 1:
        # With a single class present the derived rates are not interpretable
        # as detection skill, so refuse rather than emit a misleading number.
        raise ValueError(
            "Evaluation data must contain both classes"
        )


    precision = precision_score(
        yTrue,
        yPred,
        zero_division=0
    )


    recall = recall_score(
        yTrue,
        yPred,
        zero_division=0
    )


    f1 = f1_score(
        yTrue,
        yPred,
        zero_division=0
    )


    matrix = confusion_matrix(
        yTrue,
        yPred,
        labels=[0, 1]
    )


    tn, fp, fn, tp = (
        matrix.ravel()
    )


    falsePositiveRate = (
        fp / (fp + tn)
        if (fp + tn) > 0
        else None
    )


    falseNegativeRate = (
        fn / (fn + tp)
        if (fn + tp) > 0
        else None
    )


    result = {
        "precision":
            round(float(precision), 4),

        "recall":
            round(float(recall), 4),

        "f1Score":
            round(float(f1), 4),

        "falsePositiveRate":
            None
            if falsePositiveRate is None
            else round(float(falsePositiveRate), 4),

        "falseNegativeRate":
            None
            if falseNegativeRate is None
            else round(float(falseNegativeRate), 4),

        "truePositive":
            int(tp),

        "trueNegative":
            int(tn),

        "falsePositive":
            int(fp),

        "falseNegative":
            int(fn),

        "confusionMatrix": {
            "tn": int(tn),
            "fp": int(fp),
            "fn": int(fn),
            "tp": int(tp)
        },

        "n":
            int(len(yTrue)),

        "nPositives":
            int(sum(1 for v in yTrue if int(v) == 1)),

        "positiveRate":
            round(
                float(
                    sum(1 for v in yTrue if int(v) == 1)
                    / len(yTrue)
                ),
                4
            ),

        "predictedPositiveRate":
            round(
                float(
                    sum(1 for v in yPred if int(v) == 1)
                    / len(yPred)
                ),
                4
            )
    }


    if scores is not None:

        if len(scores) != len(yTrue):
            raise ValueError(
                "scores and yTrue must have equal length"
            )

        result["rocAuc"] = round(
            float(
                roc_auc_score(
                    yTrue,
                    scores
                )
            ),
            4
        )

        result["prAuc"] = round(
            float(
                average_precision_score(
                    yTrue,
                    scores
                )
            ),
            4
        )

    return result