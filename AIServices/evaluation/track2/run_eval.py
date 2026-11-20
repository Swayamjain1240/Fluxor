"""Track 2 evaluation: does the detector track catalogue-known variability?

TRACK 2 IS A WEAK-LABEL STUDY AND MUST NOT BE MIXED WITH TRACK 1 RESULTS.

Labelling, in one sentence: an object is "positive" when Gaia DR3's
`vari_summary` places it in at least one variability class, and "negative" when
it does not; any metric computed on that is a weak-label metric
(`evaluation/track2/build_labels.py` records the provenance).

Differences from Track 1, all deliberate:

  * the unit is the **object**, not the window;
  * the light curves are the **clean** cached TESS curves -- the Track 1
    injections were applied in memory and never written to the cache, so no
    synthetic signal enters this track;
  * no Track 1 label, split or manifest field is read here;
  * the label comes from an external catalogue classification of the star, not
    from an inspection of the light curve.

Run:
    python evaluation/track2/run_eval.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

from evaluation.mlEvaluation import evaluateMl  # noqa: E402
from ml.anomalyDetector import AnomalyDetector  # noqa: E402
from ml.features import extract_window_features  # noqa: E402
from ml.preprocessing import preprocess_light_curve  # noqa: E402

DATA_DIR = AI_ROOT / "evaluation" / "data"
CACHE_DIR = DATA_DIR / "cache"
LABELS = AI_ROOT / "evaluation" / "track2" / "labels.json"
RESULTS_DIR = AI_ROOT / "evaluation" / "results"
REPORT = AI_ROOT / "evaluation" / "reports" / "track2_catalog_proxy.md"

WINDOW_SIZE = 200
STEP_SIZE = 100
MIN_POINTS = 80

BOOTSTRAP_SEED = 42
BOOTSTRAP_ITERATIONS = 2000


# ---------------------------------------------------------------------------
# Per-object detection
# ---------------------------------------------------------------------------

def scoreObject(objectId: str, sector: int) -> dict:
    """Production detector on one clean curve; object-level summary only."""

    path = CACHE_DIR / (objectId.replace(" ", "_") + ".npz")

    with np.load(path) as data:
        timeArr = np.asarray(data["time"], dtype=float)
        fluxArr = np.asarray(data["flux"], dtype=float)

    timeClean, fluxClean = preprocess_light_curve(timeArr, fluxArr)

    features, windows = extract_window_features(
        timeClean, fluxClean, WINDOW_SIZE, STEP_SIZE, MIN_POINTS
    )

    detector = AnomalyDetector()
    result = detector.detect(features, windows)

    labels = detector.model.predict(features)
    decision = detector.model.decision_function(features)
    scores = 1.0 / (1.0 + np.exp(8.0 * decision))

    return {
        "sector": sector,
        "windows": int(result["totalWindows"]),
        "flaggedWindows": int(np.sum(labels == -1)),
        "flaggedFraction": round(float(np.mean(labels == -1)), 4),
        "isAnomalous": bool(result["isAnomalous"]),
        "productionScore": float(result["anomalyScore"]),
        "priority": result["priority"],
        "maxWindowScore": round(float(np.max(scores)), 6),
    }


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def rocAuc(labels: list[int], scores: list[float]) -> float | None:
    """Mann-Whitney AUC with tie handling; None when one class is absent."""

    positives = sum(labels)
    negatives = len(labels) - positives
    if positives == 0 or negatives == 0:
        return None

    order = sorted(range(len(scores)), key=lambda i: scores[i])
    ranks = [0.0] * len(scores)
    index = 0

    while index < len(order):
        end = index
        while end + 1 < len(order) and scores[order[end + 1]] == scores[order[index]]:
            end += 1
        averageRank = (index + end) / 2.0 + 1.0
        for position in range(index, end + 1):
            ranks[order[position]] = averageRank
        index = end + 1

    rankSum = sum(rank for rank, label in zip(ranks, labels) if label == 1)

    return (rankSum - positives * (positives + 1) / 2.0) / (positives * negatives)


def bootstrapAuc(
    labels: list[int], scores: list[float], seed: int, iterations: int
) -> dict:
    """Object-level bootstrap; reflects how thin the label set is."""

    rng = np.random.default_rng(seed)
    values = []
    skipped = 0

    for _ in range(iterations):
        picks = rng.integers(0, len(labels), len(labels))
        sampleLabels = [labels[i] for i in picks]
        sampleScores = [scores[i] for i in picks]
        value = rocAuc(sampleLabels, sampleScores)
        if value is None:
            skipped += 1
            continue
        values.append(value)

    if not values:
        return {"iterations": 0, "skipped": skipped}

    return {
        "iterations": len(values),
        "skipped": skipped,
        "median": round(float(np.median(values)), 4),
        "ci95": [
            round(float(np.percentile(values, 2.5)), 4),
            round(float(np.percentile(values, 97.5)), 4),
        ],
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def writeReport(payload: dict) -> None:

    metrics = payload["metrics"]
    table = "\n".join(
        f"| {row['objectId']} | {row['label']} | "
        f"{', '.join(row['gaiaClasses']) or '-'} | {row['Tmag']} | "
        f"{row['windows']} | {row['flaggedFraction']:.3f} | "
        f"{row['maxWindowScore']:.3f} | {row['priority']} |"
        for row in payload["objects"]
    )

    confusion = metrics["confusion"]
    auc = metrics["rocAuc"]
    aucText = "undefined (one class only)" if auc is None else f"{auc:.4f}"
    ci = metrics["bootstrapAuc"].get("ci95")
    ciText = (
        "not estimable"
        if ci is None
        else f"{ci[0]:.3f} to {ci[1]:.3f} "
        f"(median {metrics['bootstrapAuc']['median']:.3f}, "
        f"{metrics['bootstrapAuc']['iterations']} resamples)"
    )

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        f"""# Track 2 — catalogue proxy labels (weak labels)

**These labels are not ground truth.** An object is positive when Gaia DR3's
`vari_summary` contains it with `in_vari_classification_result = 1` — Gaia ran
it through variability classification — and negative when it does not. A
specific class (`in_vari_*`) is recorded where Gaia assigned one, but most
classified sources carry none, so the label means "Gaia variability candidate",
not "known variable of type X". A negative means "not in that catalogue", never
"not variable". Track 1 (seeded synthetic injection) and Track 2 are separate
studies; nothing here reads a Track 1 label, split or injected series.

## Provenance

- Objects: the 40 frozen TESS Sector 1 targets from the Track 1 manifest, used
  here only as a fixed, reproducible object list.
- Light curves: the clean cached TESS 2-minute curves (no injection).
- Positions/brightness: MAST TIC. Variability classes: Gaia DR3
  `gaiadr3.vari_summary` via Gaia TAP, fetched {payload['fetchedAtUtc']}.
- Detector: production `AnomalyDetector` (IsolationForest, 200 trees,
  contamination `auto`), fitted per curve exactly as the service does.

## Label counts

- objects: {payload['counts']['objects']}
- with a TIC row: {payload['counts']['withTic']}
- with a Gaia source id: {payload['counts']['withGaiaId']}
- present in `vari_summary`: {payload['counts']['inGaiaVariabilityTable']}
- positive (weak label): {payload['counts']['positive']}
- of those, with a specific Gaia variability class:
  {sum(1 for row in payload['objects'] if row['gaiaClasses'])}

## Metrics (object level, n = {payload['counts']['objects']})

| Metric | Value |
|---|---|
| ROC-AUC, max window score (production continuous score) | {aucText} |
| ROC-AUC bootstrap 95% CI | {ciText} |
| Precision at the production flag | {metrics['precision']:.4f} |
| Recall at the production flag | {metrics['recall']:.4f} |
| F1 at the production flag | {metrics['f1Score']:.4f} |
| Confusion (tp / fp / fn / tn) | {confusion['tp']} / {confusion['fp']} / {confusion['fn']} / {confusion['tn']} |

## Per-object results

| Object | weakLabel | Gaia classes | Tmag | windows | flagged frac | max score | priority |
|---|---|---|---|---|---|---|---|
{table}

## Limitations

1. **Weak labels.** A Gaia variability classification of the star is not
   evidence that any scored window is an anomaly, and catalogue incompleteness
   biases the negatives: many genuine variables are absent from `vari_summary`.
   Only {sum(1 for row in payload['objects'] if row['gaiaClasses'])} of the
   {payload['counts']['positive']} positives carry an assigned variability
   class; the rest are classified candidates with no reported type.
2. **Very few positives.** {payload['counts']['positive']} of {payload['counts']['objects']}
   objects are positive, so the AUC interval above is wide and the point
   estimate is unstable; it should be read as a direction, not a validated
   performance figure.
3. **Object-level only.** No window in this study carries a verified label, so
   nothing here measures localisation (which window is anomalous).
4. **No human inspection.** No candidate was reviewed by an astronomer for this
   track.
5. **Single sector.** One TESS sector per object; behaviour across sectors is
   untested.
6. **Not comparable with Track 1.** Different unit of analysis, different label
   source, different (clean) light curves. Track 1 P/R/F1 numbers must never be
   averaged, pooled or compared with these.
""",
        encoding="utf-8",
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--labels", default=str(LABELS))
    args = parser.parse_args()

    labelPayload = json.loads(Path(args.labels).read_text(encoding="utf-8"))
    objects = labelPayload["objects"]

    rows = []
    for objectId in sorted(objects):
        entry = objects[objectId]
        if not entry.get("tic"):
            print(f"skip {objectId}: {entry.get('error')}")
            continue

        scored = scoreObject(objectId, int(entry["tic"].get("sector", 1)))
        rows.append(
            {
                "objectId": objectId,
                "label": int(entry["weakLabel"]),
                "gaiaClasses": (entry.get("gaia") or {}).get("gaiaClasses", []),
                "Tmag": round(entry["tic"]["Tmag"], 3) if entry["tic"]["Tmag"] else None,
                **scored,
            }
        )

    labels = [row["label"] for row in rows]
    scores = [row["maxWindowScore"] for row in rows]
    flags = [1 if row["isAnomalous"] else 0 for row in rows]

    binary = evaluateMl(labels, flags, scores=scores)

    payload = {
        "track": "track2_catalogue_proxy",
        "groundTruth": "weak_proxy_not_ground_truth",
        "fetchedAtUtc": labelPayload["fetchedAtUtc"],
        "counts": labelPayload["counts"],
        "objects": rows,
        "metrics": {
            "rocAuc": rocAuc(labels, scores),
            "bootstrapAuc": bootstrapAuc(
                labels, scores, BOOTSTRAP_SEED, BOOTSTRAP_ITERATIONS
            ),
            "precision": binary["precision"],
            "recall": binary["recall"],
            "f1Score": binary["f1Score"],
            "confusion": binary["confusionMatrix"],
        },
        "capturedAtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    outPath = RESULTS_DIR / f"track2_catalog_{stamp}.json"
    outPath.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    writeReport(payload)

    print(
        f"objects={len(rows)} positives={sum(labels)} "
        f"auc={payload['metrics']['rocAuc']} "
        f"precision={payload['metrics']['precision']} "
        f"recall={payload['metrics']['recall']}"
    )
    print(f"wrote {outPath}")
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
