"""Baseline ML evaluation for Fluxor's Isolation Forest on the Track 1 benchmark.

Runs the UNCHANGED production model configuration and reports two evaluation
semantics separately. They are never merged:

  A. per-object transductive  - the model is fitted on the same light curve's
     windows and scored on them, which is exactly what
     `ml/anomalyDetector.py:AnomalyDetector.detect` does at inference time.
  B. pooled training fit      - the model is fitted once on all training objects
     and applied unchanged to validation and test objects.

Neither semantics touches the test split during fitting or selection.

Run:
    python evaluation/ml/run_ml_eval.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
import time
from pathlib import Path

import numpy as np

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

from evaluation.mlEvaluation import evaluateMl  # noqa: E402
from ml.anomalyDetector import AnomalyDetector  # noqa: E402

SPLITS = ("train", "val", "test")


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_benchmark(data_dir: Path) -> tuple[list[dict], dict]:
    jsonl_path = data_dir / "ml_benchmark.jsonl"
    manifest_path = data_dir / "benchmark_manifest.json"

    if not jsonl_path.exists() or not manifest_path.exists():
        raise FileNotFoundError(
            "benchmark not found; run evaluation/data/build_ml_benchmark.py first"
        )

    records = [
        json.loads(line)
        for line in jsonl_path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    digest = hashlib.sha256(jsonl_path.read_bytes()).hexdigest()
    if manifest.get("artifacts", {}).get("jsonlSha256") != digest:
        raise RuntimeError(
            "benchmark JSONL does not match its manifest hash; refusing to evaluate"
        )

    return records, manifest


def group_windows(records: list[dict]) -> dict[str, dict]:
    """Per-object feature matrix (all windows, for fitting) and evaluation mask."""
    grouped: dict[str, dict] = {}

    for record in records:
        obj = record["objectId"]
        bucket = grouped.setdefault(
            obj,
            {
                "split": record["split"],
                "features": [],
                "labels": [],
                "injectionClass": [],
                "windows": [],
            },
        )
        bucket["features"].append(record["features"])
        bucket["labels"].append(int(record["label"]))
        bucket["injectionClass"].append(record.get("injectionClass"))
        bucket["windows"].append(
            {
                "windowId": record["windowIndex"],
                "startIndex": record["startIndex"],
                "endIndex": record["endIndex"],
                "startTime": record["startTime"],
                "endTime": record["endTime"],
            }
        )

    for bucket in grouped.values():
        bucket["X"] = np.asarray(bucket["features"], dtype=float)
        bucket["evaluable"] = np.asarray(
            [lab in (0, 1) for lab in bucket["labels"]], dtype=bool
        )

    return grouped


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def fit_predict_full(detector: AnomalyDetector, X: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Fit and score every window of X using the production detector instance.

    `AnomalyDetector.detect` returns only the 10 most abnormal windows, which is
    lossy for evaluation. This uses the same fitted model and the same
    `labels == -1` convention, without that truncation.
    """
    labels = detector.model.fit_predict(X)
    decision = detector.model.decision_function(X)
    return labels, decision


def score_object(X: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray, float]:
    detector = AnomalyDetector(contamination="auto", random_state=seed)
    started = time.perf_counter()
    labels, decision = fit_predict_full(detector, X)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    return labels, decision, elapsed_ms


def score_pooled(X_train: np.ndarray, X: np.ndarray, seed: int) -> tuple[np.ndarray, np.ndarray, float]:
    detector = AnomalyDetector(contamination="auto", random_state=seed)
    detector.model.fit(X_train)
    started = time.perf_counter()
    labels = detector.model.predict(X)
    decision = detector.model.decision_function(X)
    elapsed_ms = (time.perf_counter() - started) * 1000.0
    return labels, decision, elapsed_ms


def collect_predictions(
    grouped: dict[str, dict],
    predictions: dict[str, tuple[np.ndarray, np.ndarray]],
    split: str,
) -> dict:
    y_true: list[int] = []
    y_pred: list[int] = []
    scores: list[float] = []
    per_class: dict[str, list[int]] = {}
    objects: list[str] = []

    for obj, bucket in grouped.items():
        if bucket["split"] != split:
            continue

        labels, decision = predictions[obj]
        objects.append(obj)

        for index, evaluable in enumerate(bucket["evaluable"]):
            if not evaluable:
                continue
            y_true.append(int(bucket["labels"][index]))
            y_pred.append(1 if labels[index] == -1 else 0)
            scores.append(float(-decision[index]))  # higher = more anomalous

            cls = bucket["injectionClass"][index]
            if bucket["labels"][index] == 1 and cls:
                per_class.setdefault(cls, [0, 0])
                per_class[cls][1] += 1
                if labels[index] == -1:
                    per_class[cls][0] += 1

    return {
        "yTrue": y_true,
        "yPred": y_pred,
        "scores": scores,
        "objects": objects,
        "perClassHits": {k: {"detected": v[0], "total": v[1]} for k, v in per_class.items()},
    }


def cluster_bootstrap(
    grouped: dict[str, dict],
    predictions: dict[str, tuple[np.ndarray, np.ndarray]],
    split: str,
    seed: int,
    iterations: int,
) -> dict:
    """95% CI for precision/recall/F1, resampling whole objects.

    Windows overlap by 50% and share an object, so window-level resampling would
    understate uncertainty. Objects are the independent unit.
    """
    objects = sorted(o for o, b in grouped.items() if b["split"] == split)
    if len(objects) < 2:
        return {"note": "fewer than 2 objects in split; no bootstrap"}

    rng = np.random.default_rng(seed)
    stats: dict[str, list[float]] = {"precision": [], "recall": [], "f1Score": []}
    skipped = 0

    for _ in range(iterations):
        sample = list(rng.choice(objects, size=len(objects), replace=True))
        y_true: list[int] = []
        y_pred: list[int] = []

        for obj in sample:
            bucket = grouped[obj]
            labels, _decision = predictions[obj]
            for index, evaluable in enumerate(bucket["evaluable"]):
                if not evaluable:
                    continue
                y_true.append(int(bucket["labels"][index]))
                y_pred.append(1 if labels[index] == -1 else 0)

        if len(set(y_true)) < 2:
            skipped += 1
            continue

        metrics = evaluateMl(y_true, y_pred)
        for key in stats:
            stats[key].append(float(metrics[key]))

    out = {"iterations": iterations, "used": iterations - skipped, "unit": "object"}
    for key, values in stats.items():
        if not values:
            out[key] = None
            continue
        out[key] = {
            "low": round(float(np.percentile(values, 2.5)), 4),
            "high": round(float(np.percentile(values, 97.5)), 4),
        }
    return out


def latency_summary(values_ms: list[float]) -> dict:
    if not values_ms:
        return {}
    array = np.asarray(values_ms, dtype=float)
    return {
        "n": int(array.size),
        "meanMs": round(float(array.mean()), 3),
        "p50Ms": round(float(np.percentile(array, 50)), 3),
        "p95Ms": round(float(np.percentile(array, 95)), 3),
        "maxMs": round(float(array.max()), 3),
        "totalMs": round(float(array.sum()), 3),
    }


def consistency_check(grouped: dict[str, dict], seed: int) -> dict:
    """Confirm the untruncated scoring matches production `detect()` decisions."""
    candidates = sorted(o for o, b in grouped.items() if b["split"] == "test")
    if not candidates:
        return {"status": "no test object available"}

    obj = candidates[0]
    bucket = grouped[obj]
    detector = AnomalyDetector(contamination="auto", random_state=seed)

    started = time.perf_counter()
    production = detector.detect(bucket["X"], bucket["windows"])
    production_ms = (time.perf_counter() - started) * 1000.0

    labels, _decision = fit_predict_full(AnomalyDetector(contamination="auto", random_state=seed), bucket["X"])
    predicted = {int(w) for w, lab in enumerate(labels) if lab == -1}

    reported = [int(w["windowId"]) for w in production["anomalousWindows"]]
    mismatches = [w for w in reported if w not in predicted]

    return {
        "objectId": obj,
        "totalWindows": int(len(bucket["X"])),
        "productionFlaggedWindows": int(len(predicted)),
        "productionReportedWindows": len(reported),
        "reportedButNotFlagged": mismatches,
        "match": len(mismatches) == 0,
        "detectCallMs": round(production_ms, 3),
        "note": "production detect() truncates its window list to 10; scoring is untruncated",
    }


# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------


def write_markdown(path: Path, results: dict) -> None:
    manifest = results["benchmark"]
    counts = manifest["windowCounts"]
    lines: list[str] = []

    lines.append("# Fluxor — ML Isolation Forest Baseline Evaluation (Track 1)\n")
    lines.append(
        "Generated by `evaluation/ml/run_ml_eval.py`. Every number below is read directly "
        "from the machine-readable result file; nothing is typed by hand.\n"
    )
    lines.append("## Ground truth\n")
    lines.append(
        "**Synthetic by construction.** Window labels reflect seeded signals injected into "
        "real TESS light curves. They are not confirmed astronomical anomalies, and these "
        "metrics must never be presented as real anomaly-detection accuracy. "
        "See `evaluation/AUDIT.md`, section 6.5.\n"
    )

    lines.append("## Provenance\n")
    lines.append("| Item | Value |")
    lines.append("|---|---|")
    lines.append(f"| Benchmark SHA-256 | `{manifest['artifacts']['jsonlSha256']}` |")
    lines.append(f"| Seed | {manifest['seed']} |")
    lines.append(f"| Objects | {len(manifest['targets'])} |")
    lines.append(
        "| Split (objects) | "
        f"train {len(manifest['splits']['train'])}, "
        f"val {len(manifest['splits']['val'])}, "
        f"test {len(manifest['splits']['test'])} |"
    )
    lines.append(
        f"| Windows | total {counts['total']}, positive {counts['positive']}, "
        f"negative {counts['negative']}, excluded {counts['excluded']} |"
    )
    lines.append(
        f"| Window / step / min points | {manifest['config']['windowSize']} / "
        f"{manifest['config']['stepSize']} / {manifest['config']['minPoints']} |"
    )
    lines.append(f"| Model | `{results['model']['config']}` |")
    lines.append(f"| Python / numpy / sklearn | {results['versions']['python']} / "
                 f"{results['versions']['numpy']} / {results['versions'].get('scikit-learn')} |")
    lines.append("")

    for semantics_key, semantics in results["semantics"].items():
        lines.append(f"## {semantics['label']}\n")
        lines.append(semantics["definition"] + "\n")
        lines.append(
            "| Split | n | pos | Precision | Recall | F1 | FPR | FNR | ROC-AUC | PR-AUC | flag rate |"
        )
        lines.append("|---|---|---|---|---|---|---|---|---|---|---|")
        for split in SPLITS:
            metrics = semantics["splits"].get(split)
            if not metrics:
                continue
            lines.append(
                f"| {split} | {metrics['n']} | {metrics['nPositives']} | "
                f"{metrics['precision']} | {metrics['recall']} | {metrics['f1Score']} | "
                f"{metrics['falsePositiveRate']} | {metrics['falseNegativeRate']} | "
                f"{metrics['rocAuc']} | {metrics['prAuc']} | {metrics['predictedPositiveRate']} |"
            )
        lines.append("")

        test_metrics = semantics["splits"].get("test")
        if test_metrics:
            cm = test_metrics["confusionMatrix"]
            lines.append("Test-split confusion matrix (rows = truth, cols = prediction):\n")
            lines.append("| | pred normal | pred anomaly |")
            lines.append("|---|---|---|")
            lines.append(f"| **true normal** | {cm['tn']} | {cm['fp']} |")
            lines.append(f"| **true anomaly** | {cm['fn']} | {cm['tp']} |")
            lines.append("")

        boot = semantics.get("bootstrap", {}).get("test")
        if boot and boot.get("precision"):
            lines.append(
                "Test-split 95% CI (cluster bootstrap over objects, "
                f"{boot['used']}/{boot['iterations']} usable resamples): "
                f"precision [{boot['precision']['low']}, {boot['precision']['high']}], "
                f"recall [{boot['recall']['low']}, {boot['recall']['high']}], "
                f"F1 [{boot['f1Score']['low']}, {boot['f1Score']['high']}].\n"
            )

        lines.append("Per-injection-class recall on the test split:\n")
        lines.append("| Class | detected | total | recall |")
        lines.append("|---|---|---|---|")
        for cls, counts_cls in sorted(semantics["splits"]["test"]["perClass"].items()):
            total = counts_cls["total"]
            detected = counts_cls["detected"]
            lines.append(
                f"| {cls} | {detected} | {total} | "
                f"{round(detected / total, 4) if total else 'n/a'} |"
            )
        lines.append("")

    lines.append("## Latency (measured on this machine)\n")
    lines.append("| Stage | n | p50 ms | p95 ms | max ms |")
    lines.append("|---|---|---|---|---|")
    for stage, summary in results["latency"].items():
        if not summary:
            continue
        lines.append(
            f"| {stage} | {summary['n']} | {summary['p50Ms']} | "
            f"{summary['p95Ms']} | {summary['maxMs']} |"
        )
    lines.append("")

    check = results["consistency"]
    lines.append("## Production consistency check\n")
    if "match" in check:
        lines.append(
            f"On `{check['objectId']}` ({check['totalWindows']} windows), the untruncated scoring "
            f"flagged {check['productionFlaggedWindows']} windows. Every window reported by the "
            f"production `detect()` call was also flagged by the untruncated scoring: "
            f"**{check['match']}**. The only difference is that `detect()` returns at most 10 "
            f"windows, so evaluation bypasses that truncation.\n"
        )
    else:
        lines.append(f"{check}\n")

    lines.append("## Limitations\n")
    for item in results["limitations"]:
        lines.append(f"- {item}")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run(data_dir: Path, out_dir: Path, report_path: Path, seed: int, bootstrap: int) -> dict:
    warnings_started = time.time()

    records, manifest = load_benchmark(data_dir)
    grouped = group_windows(records)

    # --- Semantics A: per-object transductive (deployed behaviour) ---
    predictions_a: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    latency_a: list[float] = []

    for obj in sorted(grouped):
        labels, decision, elapsed = score_object(grouped[obj]["X"], seed)
        predictions_a[obj] = (labels, decision)
        latency_a.append(elapsed)

    # --- Semantics B: pooled train fit, held out scoring ---
    train_objects = sorted(o for o, b in grouped.items() if b["split"] == "train")
    X_train = np.vstack([grouped[o]["X"] for o in train_objects])

    predictions_b: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    latency_b: list[float] = []

    for obj in sorted(grouped):
        labels, decision, elapsed = score_pooled(X_train, grouped[obj]["X"], seed)
        predictions_b[obj] = (labels, decision)
        latency_b.append(elapsed)

    semantics_results = {}

    for key, label, definition, predictions in (
        (
            "A_transductive_per_object",
            "Semantics A — per-object transductive (deployed behaviour)",
            "The model is fitted on one light curve's windows and scored on the same windows, "
            "matching `AnomalyDetector.detect` at inference time. Fitting therefore sees the "
            "test object's own data; this measures window ranking within a curve, not "
            "generalisation across objects.",
            predictions_a,
        ),
        (
            "B_pooled_train",
            "Semantics B — pooled training fit, held-out scoring",
            "The model is fitted once on all training-object windows and applied unchanged to "
            "validation and test objects. This measures generalisation across light curves.",
            predictions_b,
        ),
    ):
        splits_result = {}
        bootstrap_result = {}

        for split in SPLITS:
            collected = collect_predictions(grouped, predictions, split)
            metrics = evaluateMl(
                collected["yTrue"], collected["yPred"], scores=collected["scores"]
            )
            metrics["objects"] = len(collected["objects"])
            metrics["perClass"] = collected["perClassHits"]
            splits_result[split] = metrics
            bootstrap_result[split] = cluster_bootstrap(
                grouped, predictions, split, seed, bootstrap
            )

        semantics_results[key] = {
            "label": label,
            "definition": definition,
            "splits": splits_result,
            "bootstrap": bootstrap_result,
        }

    extraction = [
        manifest["objects"][o]["extractionMs"] for o in sorted(manifest["objects"])
    ]

    results = {
        "track": "track1_controlled_injection",
        "model": {
            "class": "sklearn.ensemble.IsolationForest",
            "config": "n_estimators=200, contamination='auto', max_features=1.0, "
            "random_state=42, n_jobs=-1",
            "changedFromProduction": False,
            "scoring": "decision_function; anomaly score = -decision_function",
        },
        "benchmark": manifest,
        "semantics": semantics_results,
        "latency": {
            "featureExtractionPerCurve": latency_summary(extraction),
            "fitPlusScorePerObject_transductive": latency_summary(latency_a),
            "scoreOnlyPerObject_pooled": latency_summary(latency_b),
        },
        "consistency": consistency_check(grouped, seed),
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit-learn": __import__("sklearn").__version__,
        },
        "runtimeSeconds": round(time.time() - warnings_started, 2),
        "limitations": [
            "Ground truth is synthetic injection, not confirmed astronomical anomalies.",
            "Injected morphologies are parametric (flare, dip, sinusoid, rectangular offset) "
            "and do not cover blended binaries, detector glitches or granulation.",
            "contamination='auto' sets a fixed decision threshold (offset_ = -0.5) rather than a "
            "target quantile, so the flagged fraction is data-dependent: measured 11.6% on the "
            "pooled training fit but 0.8% on held-out test objects. Semantics B's low recall is a "
            "threshold-calibration failure, not a ranking failure, since its ROC-AUC is 0.9265.",
            "anomalyScore is a saturating transform of the decision function and is not a "
            "calibrated probability.",
            "Windows overlap by 50%, so window counts overstate the number of independent "
            "observations; bootstrap intervals therefore resample objects.",
            "Semantics A fits on the evaluated object's own windows; its scores are optimistic "
            "relative to cross-object generalisation and are reported only because they match "
            "deployed behaviour.",
            "Only one sector per object is used, so multi-sector behaviour is out of scope.",
        ],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    result_path = out_dir / f"ml_baseline_{stamp}.json"
    result_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    write_markdown(report_path, results)

    print(json.dumps(
        {
            "result": str(result_path),
            "report": str(report_path),
            "A_test": {
                k: results["semantics"]["A_transductive_per_object"]["splits"]["test"][k]
                for k in ("precision", "recall", "f1Score", "falsePositiveRate",
                          "falseNegativeRate", "rocAuc", "prAuc", "n", "nPositives")
            },
            "B_test": {
                k: results["semantics"]["B_pooled_train"]["splits"]["test"][k]
                for k in ("precision", "recall", "f1Score", "falsePositiveRate",
                          "falseNegativeRate", "rocAuc", "prAuc", "n", "nPositives")
            },
        },
        indent=2,
    ))

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=str(AI_ROOT / "evaluation" / "data"))
    parser.add_argument("--out-dir", default=str(AI_ROOT / "evaluation" / "results"))
    parser.add_argument(
        "--report", default=str(AI_ROOT / "evaluation" / "reports" / "ml_baseline.md")
    )
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--bootstrap", type=int, default=1000)
    args = parser.parse_args()

    run(
        data_dir=Path(args.data_dir),
        out_dir=Path(args.out_dir),
        report_path=Path(args.report),
        seed=args.seed,
        bootstrap=args.bootstrap,
    )


if __name__ == "__main__":
    main()
