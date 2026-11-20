"""Track 2 evaluation: does the detector track catalogue-known variability?

TRACK 2 IS A WEAK-LABEL STUDY AND MUST NOT BE MIXED WITH TRACK 1 RESULTS.

Labelling, in one sentence: an object is positive when Gaia DR3's
`vari_summary` contains it with `in_vari_classification_result = 1`, and
negative when it does not; any metric computed on that is a weak-label metric
(`evaluation/track2/build_labels.py` records the provenance).

Why there is no threshold metric here:

  A per-object IsolationForest is fitted to one curve, so its decision values
  are only meaningful inside that fit -- comparing a max score from star A with
  one from star B is comparing two arbitrary origins. This study therefore fits
  **one** IsolationForest over the pooled windows of all objects and ranks
  objects by their maximum window score under that single fit. A shared origin
  makes the object scores comparable, which is what a ranking metric needs.

  The production boolean flag is not reported at all: it is defined per curve by
  `contamination="auto"`, so by construction it fires on essentially every
  object and carries no object-level information.

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
from sklearn.ensemble import IsolationForest
from sklearn.metrics import roc_auc_score

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

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

N_ESTIMATORS = 200
MAX_FEATURES = 1.0
RANDOM_STATE = 42

BOOTSTRAP_SEED = 42
BOOTSTRAP_ITERATIONS = 2000


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------

def objectWindows(objectId: str) -> dict:
    """Window features for one clean curve, in production preprocessing order."""

    path = CACHE_DIR / (objectId.replace(" ", "_") + ".npz")

    with np.load(path) as data:
        timeArr = np.asarray(data["time"], dtype=float)
        fluxArr = np.asarray(data["flux"], dtype=float)

    timeClean, fluxClean = preprocess_light_curve(timeArr, fluxArr)

    features, windows = extract_window_features(
        timeClean, fluxClean, WINDOW_SIZE, STEP_SIZE, MIN_POINTS
    )

    return {
        "objectId": objectId,
        "X": np.asarray(features, dtype=float),
        "startIndex": [int(window["startIndex"]) for window in windows],
    }


def windowAnomalyScores(decisions: np.ndarray) -> np.ndarray:
    """Same squashing the production detector applies to decision values."""

    return 1.0 / (1.0 + np.exp(8.0 * decisions))


def priorityFor(score: float) -> str:
    """Production score-to-priority mapping, kept only as a descriptive bucket."""

    if score >= 0.80:
        return "HIGH"
    if score >= 0.60:
        return "MEDIUM"
    return "LOW"


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def auc(labels: list[int], scores: list[float]) -> float | None:
    """sklearn's ROC-AUC, or None when only one class is present."""

    if len(set(labels)) < 2:
        return None
    return float(roc_auc_score(labels, scores))


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
        value = auc(sampleLabels, sampleScores)
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
        f"| {row['rank']} | {row['objectId']} | {row['label']} | "
        f"{', '.join(row['gaiaClasses']) or '-'} | {row['Tmag']} | "
        f"{row['windows']} | {row['objectScore']:.4f} | {row['priority']} |"
        for row in payload["objects"]
    )

    aucValue = metrics["rocAuc"]
    aucText = "undefined (one class only)" if aucValue is None else f"{aucValue:.4f}"
    ci = metrics["bootstrapAuc"].get("ci95")
    ciText = (
        "not estimable"
        if ci is None
        else f"{ci[0]:.3f} to {ci[1]:.3f} "
        f"(median {metrics['bootstrapAuc']['median']:.3f}, "
        f"{metrics['bootstrapAuc']['iterations']} resamples)"
    )

    classCount = sum(1 for row in payload["objects"] if row["gaiaClasses"])

    sensitivity = payload["metrics"].get("withoutOnlyClassedPositive")
    sensitivityText = (
        "not applicable"
        if not sensitivity
        else f"dropping {sensitivity['dropped']} (the only positive with an assigned "
        f"class, ranked {sensitivity['rank']}) leaves AUC {sensitivity['auc']:.4f} "
        f"over {sensitivity['objects']} objects with {sensitivity['positives']} positives"
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

## Scoring

One IsolationForest ({N_ESTIMATORS} trees, `max_features={MAX_FEATURES}`,
`random_state={RANDOM_STATE}`, `contamination="auto"`) is fitted **once** over
the pooled windows of all {payload['counts']['objects']} objects
({payload['windowsPooled']} windows). Each window gets the production score
mapping `1 / (1 + exp(8 * decision))`, and an object's score is its **maximum
window score under that single fit**.

This replaces the earlier per-object fits: a per-curve IsolationForest puts each
curve in its own arbitrary units, so comparing one object's max score with
another's was not a meaningful ranking. A single shared fit gives every object
one origin.

No precision, recall, F1 or confusion table is reported. The production boolean
flag is derived per curve from `contamination="auto"` and fired on all 40 objects
in the previous run, so a threshold metric would only restate the configuration.
`priority` below is the same static score-to-bucket mapping the service uses,
included for readability, not as a validated decision.

## Provenance

- Objects: the 40 frozen TESS Sector 1 targets from the Track 1 manifest, used
  here only as a fixed, reproducible object list.
- Light curves: the clean cached TESS 2-minute curves (no injection).
- Positions/brightness: MAST TIC. Variability: Gaia DR3 `gaiadr3.vari_summary`
  via Gaia TAP, fetched {payload['fetchedAtUtc']}.

## Label counts

- objects: {payload['counts']['objects']}
- with a TIC row: {payload['counts']['withTic']}
- with a Gaia source id: {payload['counts']['withGaiaId']}
- present in `vari_summary`: {payload['counts']['inGaiaVariabilityTable']}
- positive (weak label): {payload['counts']['positive']}
- of those, with a specific Gaia variability class: {classCount}

## Metrics (object level, n = {payload['counts']['objects']})

| Metric | Value |
|---|---|
| ROC-AUC, object max window score (global fit) | {aucText} |
| ROC-AUC bootstrap 95% CI | {ciText} |
| Leave-one-out sensitivity | {sensitivityText} |

## Per-object results (ranked by score)

| Rank | Object | weakLabel | Gaia classes | Tmag | windows | object score | bucket |
|---|---|---|---|---|---|---|---|
{table}

## Limitations

1. **Weak labels.** A Gaia variability classification of the star is not
   evidence that any scored window is an anomaly, and catalogue incompleteness
   biases the negatives: many genuine variables are absent from `vari_summary`.
   An assigned variability class exists for only {classCount} of the
   {payload['counts']['positive']} positives; the rest are classified candidates
   with no reported type.
2. **Very few positives.** {payload['counts']['positive']} of
   {payload['counts']['objects']} objects are positive, so the AUC interval is
   wide and the point estimate is unstable; read it as a direction, not a
   validated performance figure. The leave-one-out row above shows how much of
   it rests on a single object.
3. **Max-over-windows bias.** An object's score is the maximum over its windows,
   so objects with more windows get more draws. Window counts are in the table
   and are not equal.
4. **Object-level only.** No window here carries a verified label, so nothing
   measures localisation (which window is anomalous).
5. **No human inspection.** No candidate was reviewed by an astronomer for this
   track.
6. **Single sector.** One TESS sector per object; behaviour across sectors is
   untested.
7. **Not comparable with Track 1.** Different unit of analysis, different label
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

    prepared = []
    for objectId in sorted(objects):
        entry = objects[objectId]
        if not entry.get("tic"):
            print(f"skip {objectId}: {entry.get('error')}")
            continue
        prepared.append((objectId, entry, objectWindows(objectId)))

    pooled = np.vstack([item[2]["X"] for item in prepared])

    model = IsolationForest(
        n_estimators=N_ESTIMATORS,
        contamination="auto",
        random_state=RANDOM_STATE,
        n_jobs=-1,
        max_features=MAX_FEATURES,
    )
    model.fit(pooled)

    rows = []
    for objectId, entry, curve in prepared:

        decisions = model.decision_function(curve["X"])
        scores = windowAnomalyScores(decisions)
        best = int(np.argmax(scores))

        rows.append(
            {
                "objectId": objectId,
                "label": int(entry["weakLabel"]),
                "gaiaClasses": (entry.get("gaia") or {}).get("gaiaClasses", []),
                "Tmag": round(entry["tic"]["Tmag"], 3) if entry["tic"]["Tmag"] else None,
                "windows": int(len(scores)),
                "objectScore": round(float(scores[best]), 6),
                "topWindowStartIndex": curve["startIndex"][best],
            }
        )

    rows.sort(key=lambda row: row["objectScore"], reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank
        row["priority"] = priorityFor(row["objectScore"])

    labels = [row["label"] for row in rows]
    scores = [row["objectScore"] for row in rows]

    # How much of the ranking rests on the one positive Gaia gave a specific
    # class to. Reported because it is not visible from the AUC alone.
    classed = [row for row in rows if row["label"] == 1 and row["gaiaClasses"]]
    sensitivity = None

    if len(classed) == 1:
        dropped = classed[0]
        remaining = [row for row in rows if row is not dropped]
        value = auc(
            [row["label"] for row in remaining],
            [row["objectScore"] for row in remaining],
        )
        sensitivity = {
            "dropped": dropped["objectId"],
            "rank": dropped["rank"],
            "objects": len(remaining),
            "positives": sum(row["label"] for row in remaining),
            "auc": value,
        }

    payload = {
        "track": "track2_catalogue_proxy",
        "groundTruth": "weak_proxy_not_ground_truth",
        "scoring": {
            "fit": "single global IsolationForest over pooled windows of all objects",
            "nEstimators": N_ESTIMATORS,
            "maxFeatures": MAX_FEATURES,
            "randomState": RANDOM_STATE,
            "objectScore": "max window score under the global fit",
            "thresholdMetrics": None,
        },
        "windowsPooled": int(pooled.shape[0]),
        "fetchedAtUtc": labelPayload["fetchedAtUtc"],
        "counts": labelPayload["counts"],
        "objects": rows,
        "metrics": {
            "rocAuc": auc(labels, scores),
            "bootstrapAuc": bootstrapAuc(
                labels, scores, BOOTSTRAP_SEED, BOOTSTRAP_ITERATIONS
            ),
            "withoutOnlyClassedPositive": sensitivity,
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
        f"windows={payload['windowsPooled']} auc={payload['metrics']['rocAuc']}"
    )
    print(f"wrote {outPath}")
    print(f"wrote {REPORT}")


if __name__ == "__main__":
    main()
