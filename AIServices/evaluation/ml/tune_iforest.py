"""Threshold calibration for Fluxor's Isolation Forest (Part 2 completion).

The baseline showed that under a pooled training fit the model ranks anomalies
well (ROC-AUC 0.927) but flags almost none of them at the default decision cut,
because `contamination="auto"` sets a fixed threshold (offset_ = -0.5) instead of
a target quantile.

This script tests whether the decision threshold is the bottleneck:

  A0  per-curve fit, fixed offset (deployed baseline, no calibration)
  A1  per-curve fit, flag the top-q fraction of each curve (q selected on val)
  B0  pooled train fit, fixed offset (no calibration)
  B1  pooled train fit, global decision threshold (q/threshold selected on val)

Every selection uses the VALIDATION split only. The TEST split is scored once with
frozen parameters and is not used to choose anything.

Run:
    python evaluation/ml/tune_iforest.py
"""

from __future__ import annotations

import argparse
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
from evaluation.ml.run_ml_eval import (  # noqa: E402
    fit_predict_full,
    group_windows,
    latency_summary,
    load_benchmark,
    score_pooled,
)
from ml.anomalyDetector import AnomalyDetector  # noqa: E402

SPLITS = ("train", "val", "test")

# Candidate flag fractions. Applied as a quantile of the validation decision
# distribution for the pooled strategy, and as a per-curve top-q for the
# transductive strategy.
Q_GRID = np.round(np.arange(0.01, 0.301, 0.01), 4)

TEST_TOUCHES_THIS_SCRIPT = 1


# ---------------------------------------------------------------------------
# Calibrated prediction rules
# ---------------------------------------------------------------------------


def apply_global_threshold(decision: np.ndarray, threshold: float) -> np.ndarray:
    """Flag windows whose decision score falls below a fixed threshold."""
    return (decision < threshold).astype(int)


def apply_per_curve_quantile(decision: np.ndarray, q: float) -> np.ndarray:
    """Flag the lowest-scoring `q` fraction of windows within one light curve."""
    n = len(decision)
    k = int(np.ceil(q * n))
    flags = np.zeros(n, dtype=int)
    if k <= 0:
        return flags
    order = np.argsort(decision, kind="stable")[:k]
    flags[order] = 1
    return flags


def collect_for(
    objects: list[str],
    grouped: dict[str, dict],
    predictions: dict[str, tuple[np.ndarray, np.ndarray]],
    rule: str,
    param: float,
) -> dict:
    """Pool window-level truth and rule-applied predictions for `objects`."""
    y_true: list[int] = []
    y_pred: list[int] = []
    scores: list[float] = []
    per_class: dict[str, list[int]] = {}

    for obj in objects:
        bucket = grouped[obj]

        _labels, decision = predictions[obj]

        if rule == "fixed_offset":
            flagged = (decision < 0.0).astype(int)
        elif rule == "quantile":
            flagged = apply_per_curve_quantile(decision, param)
        elif rule == "threshold":
            flagged = apply_global_threshold(decision, param)
        else:
            raise ValueError(f"unknown rule {rule}")

        for index, evaluable in enumerate(bucket["evaluable"]):
            if not evaluable:
                continue
            y_true.append(int(bucket["labels"][index]))
            y_pred.append(int(flagged[index]))
            scores.append(float(-decision[index]))

            cls = bucket["injectionClass"][index]
            if bucket["labels"][index] == 1 and cls:
                per_class.setdefault(cls, [0, 0])
                per_class[cls][1] += 1
                if flagged[index] == 1:
                    per_class[cls][0] += 1

    return {
        "yTrue": y_true,
        "yPred": y_pred,
        "scores": scores,
        "perClass": {k: {"detected": v[0], "total": v[1]} for k, v in per_class.items()},
    }


def collect_for_split(
    grouped: dict[str, dict],
    predictions: dict[str, tuple[np.ndarray, np.ndarray]],
    split: str,
    rule: str,
    param: float,
) -> dict:
    objects = [o for o in sorted(grouped) if grouped[o]["split"] == split]
    return collect_for(objects, grouped, predictions, rule, param)


def metrics_for(
    grouped: dict[str, dict],
    predictions: dict[str, tuple[np.ndarray, np.ndarray]],
    rule: str,
    param: float,
) -> dict:
    out = {}
    for split in SPLITS:
        collected = collect_for_split(grouped, predictions, split, rule, param)
        result = evaluateMl(collected["yTrue"], collected["yPred"], scores=collected["scores"])
        result["perClass"] = collected["perClass"]
        out[split] = result
    return out


# ---------------------------------------------------------------------------
# Selection on validation
# ---------------------------------------------------------------------------


def select_quantile(grouped, predictions, rule: str) -> dict:
    """Choose the flag fraction that maximises validation F1."""
    candidates = []

    for q in Q_GRID:
        collected = collect_for_split(grouped, predictions, "val", rule, float(q))
        if len(set(collected["yTrue"])) < 2:
            continue
        metrics = evaluateMl(collected["yTrue"], collected["yPred"])
        candidates.append(
            {
                "q": float(q),
                "valPrecision": metrics["precision"],
                "valRecall": metrics["recall"],
                "valF1": metrics["f1Score"],
                "valFlagRate": metrics["predictedPositiveRate"],
            }
        )

    if not candidates:
        raise RuntimeError("validation selection produced no candidates")

    # Highest F1; ties broken by precision, then by the smaller flag fraction.
    best = sorted(
        candidates,
        key=lambda c: (-c["valF1"], -c["valPrecision"], c["q"]),
    )[0]

    f1_values = [c["valF1"] for c in candidates]
    return {
        "objective": "validation F1",
        "selected": best,
        "grid": {"min": float(min(Q_GRID)), "max": float(max(Q_GRID)), "points": int(len(Q_GRID))},
        "top5": sorted(candidates, key=lambda c: (-c["valF1"], c["q"]))[:5],
        "f1AcrossGrid": {
            "min": round(float(min(f1_values)), 4),
            "max": round(float(max(f1_values)), 4),
            "median": round(float(np.median(f1_values)), 4),
            "spread": round(float(max(f1_values) - min(f1_values)), 4),
        },
    }


def select_threshold(grouped, predictions) -> dict:
    """Choose a global decision threshold from validation decision values."""
    val_decisions = np.concatenate(
        [
            predictions[obj][1]
            for obj in sorted(grouped)
            if grouped[obj]["split"] == "val"
        ]
    )

    selection = select_quantile(grouped, predictions, "threshold")
    q = selection["selected"]["q"]
    tau = float(np.quantile(val_decisions, q))
    selection["derivedThreshold"] = round(tau, 6)
    selection["thresholdDerivation"] = (
        f"q={q} quantile of the {len(val_decisions)} validation decision scores"
    )
    return selection


def calibrated_bootstrap(
    grouped: dict[str, dict],
    predictions: dict[str, tuple[np.ndarray, np.ndarray]],
    split: str,
    rule: str,
    param: float,
    seed: int,
    iterations: int,
) -> dict:
    """Cluster bootstrap that applies the calibrated rule, not the fixed offset.

    Resampling the imported fixed-offset bootstrap here would report intervals for
    the wrong decision rule, so the rule is passed through explicitly.
    """
    objects = [o for o in sorted(grouped) if grouped[o]["split"] == split]
    if len(objects) < 2 or iterations <= 0:
        return {"note": "insufficient objects or zero iterations"}

    pooled = collect_for(objects, grouped, predictions, rule, param)
    point_metrics = evaluateMl(pooled["yTrue"], pooled["yPred"], scores=pooled["scores"])

    rng = np.random.default_rng(seed)
    stats: dict[str, list[float]] = {"precision": [], "recall": [], "f1Score": []}
    skipped = 0

    for _ in range(iterations):
        sample = list(rng.choice(objects, size=len(objects), replace=True))
        collected = collect_for(sample, grouped, predictions, rule, param)
        if len(set(collected["yTrue"])) < 2:
            skipped += 1
            continue
        metrics = evaluateMl(collected["yTrue"], collected["yPred"])
        for key in stats:
            stats[key].append(float(metrics[key]))

    out = {
        "iterations": iterations,
        "used": iterations - skipped,
        "unit": "object",
        "rule": rule,
        "param": param,
        "point": {
            key: point_metrics[key] for key in ("precision", "recall", "f1Score")
        },
    }
    for key, values in stats.items():
        out[key] = (
            None
            if not values
            else {
                "low": round(float(np.percentile(values, 2.5)), 4),
                "high": round(float(np.percentile(values, 97.5)), 4),
            }
        )
    return out


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def run(data_dir: Path, out_dir: Path, report_path: Path, seed: int, bootstrap: int) -> dict:
    started = time.time()

    records, manifest = load_benchmark(data_dir)
    grouped = group_windows(records)

    # --- Transductive predictions: per-curve refit (deployed behaviour) ---
    predictions_a: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    latency_a = []
    for obj in sorted(grouped):
        detector = AnomalyDetector(contamination="auto", random_state=seed)
        t0 = time.perf_counter()
        labels, decision = fit_predict_full(detector, grouped[obj]["X"])
        latency_a.append((time.perf_counter() - t0) * 1000.0)
        predictions_a[obj] = (labels, decision)

    # --- Pooled predictions: fit once on training objects ---
    train_objects = sorted(o for o, b in grouped.items() if b["split"] == "train")
    X_train = np.vstack([grouped[o]["X"] for o in train_objects])

    predictions_b: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    latency_b = []
    for obj in sorted(grouped):
        labels, decision, elapsed = score_pooled(X_train, grouped[obj]["X"], seed)
        latency_b.append(elapsed)
        predictions_b[obj] = (labels, decision)

    # --- Selection: validation only ---
    selection_a = select_quantile(grouped, predictions_a, "quantile")
    selection_b = select_threshold(grouped, predictions_b)

    q_a = selection_a["selected"]["q"]
    tau_b = selection_b["derivedThreshold"]

    # --- Final scoring: test with frozen parameters ---
    strategies = {}

    strategies["A0_per_curve_fixed_offset"] = {
        "description": "Deployed baseline: per-curve refit, flag when decision score < 0.",
        "parameters": "offset_=-0.5 (sklearn default)",
        "calibrated": False,
        "metrics": metrics_for(grouped, predictions_a, "fixed_offset", 0.0),
        "validationSelection": None,
    }

    strategies["A1_per_curve_quantile"] = {
        "description": (
            "Per-curve refit, flag the top-q fraction of windows in each curve; "
            "q chosen on validation."
        ),
        "parameters": f"q={q_a}",
        "calibrated": True,
        "metrics": metrics_for(grouped, predictions_a, "quantile", q_a),
        "validationSelection": selection_a,
    }

    strategies["B0_pooled_fixed_offset"] = {
        "description": "Pooled training fit, flag when decision score < 0.",
        "parameters": "offset_=-0.5 (sklearn default)",
        "calibrated": False,
        "metrics": metrics_for(grouped, predictions_b, "fixed_offset", 0.0),
        "validationSelection": None,
    }

    strategies["B1_pooled_threshold"] = {
        "description": (
            "Pooled training fit, global decision threshold; threshold and its "
            "quantile chosen on validation."
        ),
        "parameters": f"q={selection_b['selected']['q']}, threshold={tau_b}",
        "calibrated": True,
        "metrics": metrics_for(grouped, predictions_b, "threshold", tau_b),
        "validationSelection": selection_b,
    }

    # Bootstrap intervals for the calibrated test results.
    bootstraps = {
        "A0_per_curve_fixed_offset": calibrated_bootstrap(
            grouped, predictions_a, "test", "fixed_offset", 0.0, seed, bootstrap
        ),
        "A1_per_curve_quantile": calibrated_bootstrap(
            grouped, predictions_a, "test", "quantile", q_a, seed, bootstrap
        ),
        "B0_pooled_fixed_offset": calibrated_bootstrap(
            grouped, predictions_b, "test", "fixed_offset", 0.0, seed, bootstrap
        ),
        "B1_pooled_threshold": calibrated_bootstrap(
            grouped, predictions_b, "test", "threshold", tau_b, seed, bootstrap
        ),
    }

    test_a0 = strategies["A0_per_curve_fixed_offset"]["metrics"]["test"]
    test_a1 = strategies["A1_per_curve_quantile"]["metrics"]["test"]
    test_b0 = strategies["B0_pooled_fixed_offset"]["metrics"]["test"]
    test_b1 = strategies["B1_pooled_threshold"]["metrics"]["test"]

    deltas = {
        "A_recallGain": round(test_a1["recall"] - test_a0["recall"], 4),
        "A_precisionChange": round(test_a1["precision"] - test_a0["precision"], 4),
        "A_f1Gain": round(test_a1["f1Score"] - test_a0["f1Score"], 4),
        "B_recallGain": round(test_b1["recall"] - test_b0["recall"], 4),
        "B_precisionChange": round(test_b1["precision"] - test_b0["precision"], 4),
        "B_f1Gain": round(test_b1["f1Score"] - test_b0["f1Score"], 4),
        "B_flagRateFrom": test_b0["predictedPositiveRate"],
        "B_flagRateTo": test_b1["predictedPositiveRate"],
    }

    results = {
        "track": "track1_controlled_injection",
        "purpose": "threshold calibration; model hyperparameters unchanged",
        "model": "sklearn.ensemble.IsolationForest(n_estimators=200, "
        "contamination='auto', max_features=1.0, random_state=42, n_jobs=-1)",
        "benchmark": {
            "sha256": manifest["artifacts"]["jsonlSha256"],
            "seed": manifest["seed"],
            "windowCounts": manifest["windowCounts"],
            "splits": {k: len(v) for k, v in manifest["splits"].items()},
        },
        "protocol": {
            "selectionSplit": "val",
            "selectionObjective": "F1",
            "testSplitUsedForSelection": False,
            "testEvaluationsInThisScript": TEST_TOUCHES_THIS_SCRIPT,
            "priorTestEvaluationsInBaseline": 1,
            "note": (
                "The test split was scored once in the baseline and once here, both with "
                "parameters frozen on validation. Reusing test for reporting twice is "
                "disclosed rather than hidden; no test-based decision was made."
            ),
        },
        "strategies": strategies,
        "bootstrapTest": bootstraps,
        "deltas": deltas,
        "latency": {
            "fitPlusScorePerObject_transductive": latency_summary(latency_a),
            "scoreOnlyPerObject_pooled": latency_summary(latency_b),
        },
        "versions": {
            "python": platform.python_version(),
            "numpy": np.__version__,
            "scikit-learn": __import__("sklearn").__version__,
        },
        "runtimeSeconds": round(time.time() - started, 2),
        "limitations": [
            "Ground truth is synthetic injection, not confirmed astronomical anomalies.",
            "Selection used 8 validation objects (171 positives); the chosen operating "
            "point is therefore itself uncertain, which is why validation F1 across the "
            "whole grid is reported.",
            "A per-curve flag fraction forces a constant number of flags per light curve, "
            "which is a strong assumption when real anomaly rates vary between objects.",
            "The pooled threshold is a single global cut; it ignores per-object score "
            "distributions, which is exactly what the per-curve strategy exploits.",
            "Metrics remain conditional on the injected morphologies (flare, dip, "
            "sinusoid, rectangular offset) and one TESS sector per object.",
        ],
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    result_path = out_dir / f"ml_calibration_{stamp}.json"
    result_path.write_text(json.dumps(results, indent=2), encoding="utf-8")

    write_markdown(report_path, results)

    print(json.dumps(
        {
            "result": str(result_path),
            "report": str(report_path),
            "selected": {
                "A1_q": q_a,
                "B1_q": selection_b["selected"]["q"],
                "B1_threshold": tau_b,
            },
            "test": {
                name: {
                    k: strategies[name]["metrics"]["test"][k]
                    for k in ("precision", "recall", "f1Score", "falsePositiveRate",
                              "predictedPositiveRate")
                }
                for name in strategies
            },
            "deltas": deltas,
        },
        indent=2,
    ))

    return results


def write_markdown(path: Path, results: dict) -> None:
    lines: list[str] = []
    bench = results["benchmark"]
    strategies = results["strategies"]

    lines.append("# Fluxor — ML Threshold Calibration (Part 2 completion)\n")
    lines.append(
        "Generated by `evaluation/ml/tune_iforest.py`. Every number is read from the "
        "machine-readable result file.\n"
    )
    lines.append("## Ground truth\n")
    lines.append(
        "**Synthetic by construction.** Labels reflect seeded injections into real TESS "
        "light curves, not confirmed astronomical anomalies. See `evaluation/AUDIT.md` "
        "section 6.5.\n"
    )

    lines.append("## Protocol\n")
    lines.append("| Item | Value |")
    lines.append("|---|---|")
    lines.append(f"| Benchmark SHA-256 | `{bench['sha256']}` |")
    lines.append(f"| Seed | {bench['seed']} |")
    lines.append(
        f"| Objects (train/val/test) | {bench['splits']['train']} / "
        f"{bench['splits']['val']} / {bench['splits']['test']} |"
    )
    lines.append(f"| Selection split | {results['protocol']['selectionSplit']} only |")
    lines.append(f"| Selection objective | {results['protocol']['selectionObjective']} |")
    lines.append(
        f"| Test evaluations (baseline + this) | "
        f"{results['protocol']['priorTestEvaluationsInBaseline']} + "
        f"{results['protocol']['testEvaluationsInThisScript']} |"
    )
    lines.append(f"| Model hyperparameters | unchanged (`{results['model']}`) |")
    lines.append("")

    sel_a = strategies["A1_per_curve_quantile"]["validationSelection"]
    sel_b = strategies["B1_pooled_threshold"]["validationSelection"]

    lines.append("## Selection on validation\n")
    lines.append("| Strategy | Chosen | Val precision | Val recall | Val F1 | Val flag rate |")
    lines.append("|---|---|---|---|---|---|")
    for name, sel in (("A1 per-curve quantile", sel_a), ("B1 pooled threshold", sel_b)):
        chosen = sel["selected"]
        label = f"q={chosen['q']}"
        if name.startswith("B1"):
            label += f", threshold={sel['derivedThreshold']}"
        lines.append(
            f"| {name} | {label} | {chosen['valPrecision']} | {chosen['valRecall']} | "
            f"{chosen['valF1']} | {chosen['valFlagRate']} |"
        )
    lines.append("")
    lines.append(
        f"Validation F1 across the whole q grid: min {sel_a['f1AcrossGrid']['min']}, "
        f"median {sel_a['f1AcrossGrid']['median']}, max {sel_a['f1AcrossGrid']['max']} "
        f"(A1); min {sel_b['f1AcrossGrid']['min']}, median "
        f"{sel_b['f1AcrossGrid']['median']}, max {sel_b['f1AcrossGrid']['max']} (B1). "
        "A flat curve would mean the chosen operating point is arbitrary.\n"
    )

    lines.append("## Test results (parameters frozen from validation)\n")
    lines.append(
        "| Strategy | Calibrated | Precision | Recall | F1 | FPR | Flag rate | ROC-AUC | PR-AUC |"
    )
    lines.append("|---|---|---|---|---|---|---|---|---|")
    for name, strategy in strategies.items():
        test = strategy["metrics"]["test"]
        lines.append(
            f"| {name} | {'yes' if strategy['calibrated'] else 'no'} | {test['precision']} | "
            f"{test['recall']} | {test['f1Score']} | {test['falsePositiveRate']} | "
            f"{test['predictedPositiveRate']} | {test['rocAuc']} | {test['prAuc']} |"
        )
    lines.append("")

    deltas = results["deltas"]
    lines.append("### Effect of calibration on the test split\n")
    lines.append("| Change | Value |")
    lines.append("|---|---|")
    lines.append(f"| A recall gain (A0 → A1) | {deltas['A_recallGain']:+} |")
    lines.append(f"| A precision change | {deltas['A_precisionChange']:+} |")
    lines.append(f"| A F1 gain | {deltas['A_f1Gain']:+} |")
    lines.append(f"| B recall gain (B0 → B1) | {deltas['B_recallGain']:+} |")
    lines.append(f"| B precision change | {deltas['B_precisionChange']:+} |")
    lines.append(f"| B F1 gain | {deltas['B_f1Gain']:+} |")
    lines.append(
        f"| B flag rate | {deltas['B_flagRateFrom']} → {deltas['B_flagRateTo']} |"
    )
    lines.append("")

    lines.append("## Confusion matrices (test split)\n")
    for name, strategy in strategies.items():
        cm = strategy["metrics"]["test"]["confusionMatrix"]
        lines.append(f"**{name}** — tn {cm['tn']}, fp {cm['fp']}, fn {cm['fn']}, tp {cm['tp']}\n")

    lines.append("## Per-injection-class recall (test split)\n")
    classes = sorted({c for s in strategies.values() for c in s["metrics"]["test"]["perClass"]})
    header = "| Class | " + " | ".join(strategies) + " |"
    lines.append(header)
    lines.append("|---" * (len(strategies) + 1) + "|")
    for cls in classes:
        cells = []
        for strategy in strategies.values():
            entry = strategy["metrics"]["test"]["perClass"].get(cls)
            if not entry or not entry["total"]:
                cells.append("n/a")
            else:
                cells.append(f"{round(entry['detected'] / entry['total'], 4)}")
        lines.append(f"| {cls} | " + " | ".join(cells) + " |")
    lines.append("")

    lines.append("## Bootstrap 95% CI (test, resampling objects)\n")
    for name, boot in results["bootstrapTest"].items():
        if boot.get("precision"):
            lines.append(
                f"- **{name}**: precision [{boot['precision']['low']}, "
                f"{boot['precision']['high']}], recall [{boot['recall']['low']}, "
                f"{boot['recall']['high']}], F1 [{boot['f1Score']['low']}, "
                f"{boot['f1Score']['high']}] ({boot['used']}/{boot['iterations']} resamples)"
            )
    lines.append("")

    lines.append("## Latency\n")
    lines.append("| Stage | n | p50 ms | p95 ms | max ms |")
    lines.append("|---|---|---|---|---|")
    for stage, summary in results["latency"].items():
        lines.append(
            f"| {stage} | {summary['n']} | {summary['p50Ms']} | {summary['p95Ms']} | "
            f"{summary['maxMs']} |"
        )
    lines.append("")

    lines.append("## Limitations\n")
    for item in results["limitations"]:
        lines.append(f"- {item}")
    lines.append("")

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data-dir", default=str(AI_ROOT / "evaluation" / "data"))
    parser.add_argument("--out-dir", default=str(AI_ROOT / "evaluation" / "results"))
    parser.add_argument(
        "--report", default=str(AI_ROOT / "evaluation" / "reports" / "ml_calibration.md")
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
