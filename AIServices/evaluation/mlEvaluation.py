from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)


def evaluateMl(
    yTrue,
    yPred
):
    """
    0 = Normal
    1 = Anomaly
    """

    if len(yTrue) != len(yPred):
        raise ValueError(
            "yTrue and yPred must have equal length"
        )

    if len(yTrue) == 0:
        raise ValueError(
            "Evaluation data cannot be empty"
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
        else 0
    )


    return {
        "precision":
            round(float(precision), 4),

        "recall":
            round(float(recall), 4),

        "f1Score":
            round(float(f1), 4),

        "falsePositiveRate":
            round(
                float(falsePositiveRate),
                4
            ),

        "truePositive":
            int(tp),

        "trueNegative":
            int(tn),

        "falsePositive":
            int(fp),

        "falseNegative":
            int(fn)
    }