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
import textwrap
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

# Markdown prose is reflowed here rather than hand-wrapped in the template, so a
# longer number or word cannot leave a broken line behind.
PROSE_WIDTH = 80
BOOTSTRAP_ITERATIONS = 2000
PERMUTATION_ITERATIONS = 20000


# ---------------------------------------------------------------------------
# Features
# ---------------------------------------------------------------------------

def objectWindows(objectId: str, cacheDir: Path) -> dict:
    """Window features for one clean curve, in production preprocessing order."""

    path = cacheDir / (objectId.replace(" ", "_") + ".npz")

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
        "windows": len(windows),
    }


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

def auc(labels: list[int], scores: list[float]) -> float | None:
    """sklearn's ROC-AUC, or None when only one class is present."""

    if len(set(labels)) < 2:
        return None
    return float(roc_auc_score(labels, scores))


def stratifiedBootstrapAuc(
    labels: list[int], scores: list[float], seed: int, iterations: int
) -> dict:
    """Bootstrap with positives and negatives resampled separately.

    An object-level bootstrap draws only ~5 positives in a 40-object sample, so
    it mostly measures which positives happened to be drawn. Resampling each
    class to its own size keeps every replicate at the observed 5-vs-35 balance
    and asks the question of interest: how stable is the ranking given this many
    positives?
    """

    positives = [s for s, label in zip(scores, labels) if label == 1]
    negatives = [s for s, label in zip(scores, labels) if label == 0]

    if not positives or not negatives:
        return {"iterations": 0, "skipped": iterations}

    rng = np.random.default_rng(seed)
    values = []

    for _ in range(iterations):
        drawnPositives = rng.choice(positives, size=len(positives), replace=True)
        drawnNegatives = rng.choice(negatives, size=len(negatives), replace=True)
        values.append(
            roc_auc_score(
                [1] * len(drawnPositives) + [0] * len(drawnNegatives),
                list(drawnPositives) + list(drawnNegatives),
            )
        )

    return {
        "iterations": len(values),
        "skipped": 0,
        "stratified": True,
        "median": round(float(np.median(values)), 4),
        "ci95": [
            round(float(np.percentile(values, 2.5)), 4),
            round(float(np.percentile(values, 97.5)), 4),
        ],
    }


def permutationPValue(
    labels: list[int], scores: list[float], seed: int, iterations: int
) -> dict:
    """One-sided p-value: how often shuffling labels reaches the observed AUC.

    This is the significance test that matters at this sample size. A bootstrap
    interval says how well five positives pin down an AUC; it does not say
    whether that AUC is distinguishable from chance.
    """

    observed = auc(labels, scores)

    if observed is None:
        return {"iterations": iterations, "pValue": None, "observed": None}

    labelArray = np.asarray(labels)
    scoreArray = np.asarray(scores)
    rng = np.random.default_rng(seed)
    atLeastAsHigh = 0

    for _ in range(iterations):
        if roc_auc_score(rng.permutation(labelArray), scoreArray) >= observed:
            atLeastAsHigh += 1

    return {
        "iterations": iterations,
        "observed": round(float(observed), 4),
        "pValue": round((atLeastAsHigh + 1) / (iterations + 1), 4),
        "sidedness": "one-sided, >= observed, +1 smoothing",
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------

def writeReport(payload: dict, report: Path) -> None:

    metrics = payload["metrics"]
    table = "\n".join(
        f"| {row['rank']} | {row['objectId']} | {row['label']} | "
        f"{', '.join(row['gaiaClasses']) or '-'} | {row['Tmag']} | "
        f"{row['windows']} | {row['objectScore']:.4f} |"
        for row in payload["objects"]
    )

    aucValue = metrics["rocAuc"]
    aucText = "undefined (one class only)" if aucValue is None else f"{aucValue:.4f}"
    bootstrap = metrics["stratifiedBootstrapAuc"]
    ci = bootstrap.get("ci95")
    ciText = (
        "not estimable"
        if ci is None
        else f"{ci[0]:.3f} to {ci[1]:.3f} "
        f"(median {bootstrap['median']:.3f}, {bootstrap['iterations']} replicates, "
        f"positives and negatives resampled separately)"
    )

    permutation = metrics["permutationP"]
    pText = (
        "undefined"
        if permutation.get("pValue") is None
        else f"{permutation['pValue']:.4f} over {permutation['iterations']} label "
        f"shuffles (one-sided, +1 smoothing)"
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

    counts = payload["counts"]
    nObjects = counts["objects"]
    nPositives = counts["positive"]
    pValue = permutation.get("pValue")
    pShort = "undefined" if pValue is None else f"{pValue:.4f}"

    sampleText = textwrap.fill(
        "At this sample size the permutation p-value, not the interval, is the "
        f"test that matters: the interval says how well {nPositives} positives "
        "pin down an AUC, while the p-value asks whether the ranking is "
        "distinguishable from chance at all.",
        width=PROSE_WIDTH,
    )

    if nPositives and classCount == nPositives:
        classText = (
            f"All {nPositives} positives carry an assigned class, so a positive "
            "means 'classified as that kind of variable', not merely 'a "
            "variability candidate'."
        )
    else:
        classText = (
            f"An assigned variability class exists for only {classCount} of the "
            f"{nPositives} positives; the rest are classified candidates with no "
            "reported type."
        )

    weakLabelText = textwrap.fill(
        "**Weak labels.** A Gaia variability classification of the star is not "
        "evidence that any scored window is an anomaly, and catalogue "
        "incompleteness biases the negatives: many genuine variables are absent "
        f"from `vari_summary`. {classText}",
        width=PROSE_WIDTH,
        initial_indent="1. ",
        subsequent_indent="   ",
    )

    if pValue is None:
        significanceHeading = "**Very few positives.**"
        significanceText = "The permutation test could not be computed here."
    elif pValue < 0.05:
        significanceHeading = "**Very few positives.**"
        significanceText = (
            f"The permutation test gives p={pShort}, so the ranking is "
            "unlikely under a random labelling, but it still rests on "
            f"{nPositives} positives: a single object can carry it."
        )
    else:
        significanceHeading = "**Very few positives, and no significance.**"
        significanceText = (
            f"The permutation test gives p={pShort}, so the ranking is not "
            "distinguishable from chance at this sample size."
        )
        if sensitivity:
            significanceText += (
                " A single object can carry it, as the leave-one-out row shows."
            )

    positivesText = textwrap.fill(
        f"{significanceHeading} {nPositives} of {nObjects} objects are "
        "positive, so the AUC interval is wide and the point estimate is "
        f"unstable; read it as a direction, not a validated performance figure. "
        f"{significanceText}",
        width=PROSE_WIDTH,
        initial_indent="2. ",
        subsequent_indent="   ",
    )

    report.parent.mkdir(parents=True, exist_ok=True)
    report.write_text(
        f"""# Track 2 — catalogue proxy labels (weak labels)

**These labels are not ground truth.** {payload['labelDefinition']}

Track 1 (seeded synthetic injection) and Track 2 are separate studies; nothing
here reads a Track 1 label, split or injected series.

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

No precision, recall, F1 or confusion table is reported, and no score-to-priority
bucket either. The production boolean flag is derived per curve from
`contamination="auto"` and fired on every object in the earlier Track 2 run, so
a threshold metric would only restate the configuration.

## Provenance

- Objects: {payload['provenance']}
- Light curves: clean TESS 2-minute curves (no injection).
- Positions/brightness: MAST TIC. Variability: Gaia DR3 `gaiadr3.vari_summary`
  via Gaia TAP, fetched {payload['fetchedAtUtc']}.

## Label counts

- objects: {payload['counts']['objects']}
- with a TIC row: {payload['counts'].get('withTic', 'not recorded')}
- with a Gaia source id: {payload['counts'].get('withGaiaId', 'not recorded')}
- present in `vari_summary`: {payload['counts'].get('inGaiaVariabilityTable', 'not recorded')}
- positive (weak label): {payload['counts']['positive']}
- of those, with a specific Gaia variability class: {classCount}

## Metrics (object level, n = {payload['counts']['objects']})

| Metric | Value |
|---|---|
| ROC-AUC, object max window score (global fit) | {aucText} |
| Permutation p-value (ranking against chance) | {pText} |
| ROC-AUC stratified bootstrap 95% CI | {ciText} |
| Leave-one-out sensitivity | {sensitivityText} |

{sampleText}

## Per-object results (ranked by score)

| Rank | Object | weakLabel | Gaia classes | Tmag | windows | object score |
|---|---|---|---|---|---|---|
{table}

## Limitations

{weakLabelText}
{positivesText}
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
    parser.add_argument("--cache", default=str(CACHE_DIR))
    parser.add_argument("--report", default=str(REPORT))
    parser.add_argument(
        "--provenance",
        default="the 40 frozen TESS Sector 1 targets from the Track 1 manifest, "
        "used here only as a fixed, reproducible object list",
    )
    args = parser.parse_args()

    cacheDir = Path(args.cache)
    report = Path(args.report)

    labelPayload = json.loads(Path(args.labels).read_text(encoding="utf-8"))
    objects = labelPayload["objects"]
    payloadTime = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    prepared = []
    for objectId in sorted(objects):
        entry = objects[objectId]
        if not entry.get("tic"):
            print(f"skip {objectId}: {entry.get('error')}")
            continue
        prepared.append((objectId, entry, objectWindows(objectId, cacheDir)))

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

        # Production score mapping, applied to the global fit's decision values.
        scores = 1.0 / (1.0 + np.exp(8.0 * model.decision_function(curve["X"])))

        rows.append(
            {
                "objectId": objectId,
                "label": int(entry["weakLabel"]),
                "gaiaClasses": (entry.get("gaia") or {}).get("gaiaClasses", []),
                "Tmag": round(entry["tic"]["Tmag"], 3) if entry["tic"]["Tmag"] else None,
                "windows": curve["windows"],
                "objectScore": round(float(np.max(scores)), 6),
            }
        )

    rows.sort(key=lambda row: row["objectScore"], reverse=True)
    for rank, row in enumerate(rows, start=1):
        row["rank"] = rank

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
        },
        "windowsPooled": int(pooled.shape[0]),
        "provenance": args.provenance,
        "labelDefinition": labelPayload.get(
            "labelDefinition",
            "An object is positive when Gaia DR3's `vari_summary` contains it with "
            "`in_vari_classification_result = 1` -- Gaia ran it through variability "
            "classification -- and negative when it does not. A specific class is "
            "recorded where Gaia assigned one, but most classified sources carry "
            "none, so the label means 'Gaia variability candidate', not 'known "
            "variable of type X'. A negative means 'not in that catalogue', never "
            "'not variable'.",
        ),
        "fetchedAtUtc": labelPayload.get("fetchedAtUtc", payloadTime),
        "counts": labelPayload["counts"],
        "objects": rows,
        "metrics": {
            "rocAuc": auc(labels, scores),
            "permutationP": permutationPValue(
                labels, scores, BOOTSTRAP_SEED, PERMUTATION_ITERATIONS
            ),
            "stratifiedBootstrapAuc": stratifiedBootstrapAuc(
                labels, scores, BOOTSTRAP_SEED, BOOTSTRAP_ITERATIONS
            ),
            "withoutOnlyClassedPositive": sensitivity,
        },
        "capturedAtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    outPath = RESULTS_DIR / f"{report.stem}_{stamp}.json"
    outPath.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    writeReport(payload, report)

    print(
        f"objects={len(rows)} positives={sum(labels)} "
        f"windows={payload['windowsPooled']} auc={payload['metrics']['rocAuc']} "
        f"p={payload['metrics']['permutationP']['pValue']}"
    )
    print(f"wrote {outPath}")
    print(f"wrote {report}")


if __name__ == "__main__":
    main()
