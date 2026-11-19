"""Build the Track 1 controlled-injection benchmark for Fluxor ML evaluation.

Downloads real TESS 2-minute light curves (cached after the first run), applies
seeded synthetic injections to create window-level ground truth, and freezes the
result into a JSONL benchmark plus a manifest.

GROUND TRUTH IS SYNTHETIC BY CONSTRUCTION.
This is not real anomaly annotation. See evaluation/AUDIT.md section 6.

Run:
    python evaluation/data/build_ml_benchmark.py
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import sys
import time
import warnings
from pathlib import Path

import numpy as np

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

from ml.features import FEATURE_NAMES, extract_window_features  # noqa: E402
from ml.preprocessing import preprocess_light_curve  # noqa: E402

# ---------------------------------------------------------------------------
# Frozen experiment configuration
# ---------------------------------------------------------------------------

MASTER_SEED = 42

WINDOW_SIZE = 200
STEP_SIZE = 100
MIN_POINTS = 80

# Injected span sits in the centre of a chosen window. Chosen window starts are
# multiples of 2*STEP_SIZE, so their spans are sample-disjoint. No other window
# can fully contain the injected span, which makes labelling unambiguous.
INJECTION_WIDTH = 100
DISJOINT_STRIDE = 2 * STEP_SIZE

TARGETS_TOTAL = 40
SPLIT_SIZES = {"train": 24, "val": 8, "test": 8}

TARGET_POSITIVE_RATE = 0.10

INJECTION_CLASSES = ("T1_flare", "T2_dip", "T3_sinusoid", "T4_offset")

# Amplitude is drawn as a target SNR against the curve's own robust noise, then
# clipped to the amplitude bounds documented in AUDIT.md section 6.2.
SNR_RANGE = (3.0, 20.0)
AMPLITUDE_CLIP = (0.001, 0.10)


# ---------------------------------------------------------------------------
# Injection primitives (pure functions: deterministic given rng)
# ---------------------------------------------------------------------------


def robust_sigma(flux: np.ndarray) -> float:
    """Median-absolute-deviation scatter of a normalized light curve."""
    med = float(np.median(flux))
    mad = float(np.median(np.abs(flux - med)))
    return 1.4826 * mad


def make_flare(n: int, amp: float, rng: np.random.Generator) -> np.ndarray:
    """T1: fast rise (1 sample), exponential decay.

    The peak equals `amp` exactly at index 1 so that the recorded amplitude is
    the actual injected peak, not an extrapolated one.
    """
    tau = float(rng.uniform(10.0, 60.0))
    t = np.arange(n, dtype=float)
    sig = amp * np.exp(-np.maximum(t - 1.0, 0.0) / tau)
    sig[0] = 0.0
    return sig


def make_dip(n: int, amp: float, rng: np.random.Generator) -> np.ndarray:
    """T2: trapezoidal eclipse/transit dip."""
    duration = int(rng.integers(20, 80))
    ingress = int(rng.integers(2, 6))
    start = int(rng.integers(0, max(1, n - duration)))
    sig = np.zeros(n, dtype=float)
    for i in range(duration):
        idx = start + i
        if idx >= n:
            break
        edge = min(i, duration - 1 - i)
        frac = 1.0 if edge >= ingress else (edge + 1) / (ingress + 1)
        sig[idx] = -amp * frac
    return sig


def make_sinusoid(n: int, amp: float, rng: np.random.Generator) -> np.ndarray:
    """T3: sinusoidal variability, Hann-tapered to the injected span."""
    period = float(rng.uniform(40.0, 100.0))
    phase = float(rng.uniform(0.0, 2.0 * np.pi))
    t = np.arange(n, dtype=float)
    taper = np.hanning(n)
    return amp * np.sin(2.0 * np.pi * t / period + phase) * taper


def make_offset(n: int, amp: float, rng: np.random.Generator) -> np.ndarray:
    """T4: abrupt rectangular level offset (instrumental-glitch morphology)."""
    start = int(rng.integers(0, max(1, n // 2)))
    sign = 1.0 if rng.random() < 0.5 else -1.0
    sig = np.zeros(n, dtype=float)
    sig[start:] = sign * amp
    return sig


INJECTORS = {
    "T1_flare": make_flare,
    "T2_dip": make_dip,
    "T3_sinusoid": make_sinusoid,
    "T4_offset": make_offset,
}


def inject(
    flux: np.ndarray,
    window_start: int,
    cls: str,
    rng: np.random.Generator,
) -> tuple[np.ndarray, dict]:
    """Inject one anomaly of `cls` into the centre of the window at `window_start`."""
    n_curve = len(flux)
    span_start = window_start + (WINDOW_SIZE - INJECTION_WIDTH) // 2
    span_end = span_start + INJECTION_WIDTH
    if span_end > n_curve:
        raise ValueError("injection span exceeds curve length")

    segment = flux[span_start:span_end]
    sigma = robust_sigma(segment)
    if sigma <= 0:
        sigma = robust_sigma(flux)
    if sigma <= 0:
        raise ValueError("could not estimate noise level for injection")

    snr_target = float(np.exp(rng.uniform(np.log(SNR_RANGE[0]), np.log(SNR_RANGE[1]))))
    amp_raw = snr_target * sigma
    amp = float(np.clip(amp_raw, AMPLITUDE_CLIP[0], AMPLITUDE_CLIP[1]))

    signal = INJECTORS[cls](INJECTION_WIDTH, amp, rng)

    out = flux.copy()
    out[span_start:span_end] += signal

    params = {
        "class": cls,
        "spanStartIndex": int(span_start),
        "spanEndIndex": int(span_end),
        "amplitudeRel": round(amp, 6),
        "targetSnr": round(snr_target, 3),
        "realizedSnr": round(amp / sigma, 3),
        "amplitudeClipped": bool(abs(amp - amp_raw) > 1e-12),
        "noiseSigma": round(sigma, 8),
    }
    return out, params


# ---------------------------------------------------------------------------
# Data acquisition
# ---------------------------------------------------------------------------


def discover_targets() -> list[str]:
    """TESS 2-minute targets from a single archival MAST query, sorted."""
    from astroquery.mast import Observations

    obs = Observations.query_criteria(
        obs_collection="TESS",
        dataproduct_type="timeseries",
        t_exptime=120,
        sequence_number=1,
    )
    names = sorted({str(n) for n in obs["target_name"]})
    return [f"TIC {n}" for n in names]


def fetch_curve(target: str, cache_dir: Path) -> dict | None:
    """One sector of TESS 2-minute photometry, cached as .npz."""
    cache_dir.mkdir(parents=True, exist_ok=True)
    path = cache_dir / (target.replace(" ", "_") + ".npz")

    if path.exists():
        with np.load(path) as d:
            return {
                "objectId": target,
                "time": np.asarray(d["time"], dtype=float),
                "flux": np.asarray(d["flux"], dtype=float),
                "sector": int(d["sector"]),
                "cached": True,
            }

    import lightkurve as lk

    search = lk.search_lightcurve(target, mission="TESS", exptime=120)
    if len(search) == 0:
        return None

    lc = search[0].download()
    if lc is None:
        return None

    time = np.asarray(lc.time.value, dtype=float)
    flux = np.asarray(lc.flux.value, dtype=float)
    sector = int(lc.meta.get("SECTOR", -1))

    np.savez_compressed(path, time=time, flux=flux, sector=sector)

    return {
        "objectId": target,
        "time": time,
        "flux": flux,
        "sector": sector,
        "cached": False,
    }


# ---------------------------------------------------------------------------
# Benchmark construction
# ---------------------------------------------------------------------------


def assign_splits(object_ids: list[str], noise: list[float], seed: int) -> dict[str, str]:
    """Split by object, balanced across noise level.

    Labels are shuffled over the noise-sorted object list so each split spans the
    quiet-to-noisy range. Objects, never windows, are the unit of splitting, which
    is what prevents the 50% window overlap from leaking (AUDIT.md H1).
    """
    labels: list[str] = []
    for split, size in SPLIT_SIZES.items():
        labels.extend([split] * size)
    if len(labels) < len(object_ids):
        raise ValueError("split sizes do not cover all objects")

    rng = random.Random(seed)
    rng.shuffle(labels)

    order = sorted(range(len(object_ids)), key=lambda i: noise[i])
    return {object_ids[i]: labels[rank] for rank, i in enumerate(order)}


def build(
    out_dir: Path,
    cache_dir: Path,
    n_targets: int,
    seed: int,
    target_positive_rate: float,
) -> dict:
    started = time.time()
    warnings.filterwarnings("ignore")

    if n_targets != sum(SPLIT_SIZES.values()):
        raise ValueError("n_targets must equal the frozen split total")

    # Frozen target list: reuse the manifest if present so reruns are identical
    # even if the MAST target inventory changes.
    manifest_path = out_dir / "benchmark_manifest.json"
    frozen_targets = None
    if manifest_path.exists():
        try:
            prev = json.loads(manifest_path.read_text(encoding="utf-8"))
            frozen_targets = prev.get("targets")
        except Exception:
            frozen_targets = None

    if frozen_targets:
        candidates = frozen_targets
        print(f"reusing frozen target list ({len(candidates)} targets)")
    else:
        print("querying MAST for TESS 2-minute targets ...")
        pool = discover_targets()
        print(f"  pool size: {len(pool)}")
        order = list(range(len(pool)))
        random.Random(seed).shuffle(order)
        candidates = [pool[i] for i in order]

    # Collect light curves until n_targets are usable.
    curves: dict[str, dict] = {}
    failures: list[dict] = []

    for target in candidates:
        if len(curves) >= n_targets:
            break
        try:
            data = fetch_curve(target, cache_dir)
        except Exception as error:  # network/parse failures are recorded, not hidden
            failures.append({"target": target, "error": f"{type(error).__name__}: {error}"})
            print(f"  skip {target}: {type(error).__name__}")
            continue

        if data is None:
            failures.append({"target": target, "error": "no TESS 2-minute light curve"})
            continue

        try:
            time_clean, flux_clean = preprocess_light_curve(data["time"], data["flux"])
        except Exception as error:
            failures.append({"target": target, "error": f"preprocess: {error}"})
            continue

        if len(flux_clean) < WINDOW_SIZE:
            failures.append({"target": target, "error": "curve shorter than one window"})
            continue

        try:
            _, windows = extract_window_features(
                time_clean, flux_clean, WINDOW_SIZE, STEP_SIZE, MIN_POINTS
            )
        except Exception as error:
            failures.append({"target": target, "error": f"windowing: {error}"})
            continue

        curves[target] = {
            "time": time_clean,
            "flux": flux_clean,
            "windows": windows,
            "sector": data["sector"],
            "cached": data["cached"],
        }
        print(f"  [{len(curves):2d}/{n_targets}] {target} sector={data['sector']} windows={len(windows)}")

    if len(curves) < n_targets:
        raise RuntimeError(
            f"only {len(curves)} usable light curves, need {n_targets}. "
            "Refusing to fabricate substitute data."
        )

    object_ids = sorted(curves)
    noise = [
        float(np.std(curves[o]["flux"]) / abs(np.median(curves[o]["flux"]))) for o in object_ids
    ]
    splits = assign_splits(object_ids, noise, seed)

    # Per-object extraction latency, measured on the clean curve.
    extraction_ms: dict[str, float] = {}
    for o in object_ids:
        t0 = time.perf_counter()
        extract_window_features(
            curves[o]["time"], curves[o]["flux"], WINDOW_SIZE, STEP_SIZE, MIN_POINTS
        )
        extraction_ms[o] = (time.perf_counter() - t0) * 1000.0

    records: list[dict] = []
    per_object: dict[str, dict] = {}

    for split_rank, object_id in enumerate(object_ids):
        curve = curves[object_id]
        split = splits[object_id]
        windows = curve["windows"]
        flux = curve["flux"]
        time_arr = curve["time"]

        # Only windows starting at multiples of DISJOINT_STRIDE are eligible, so
        # injected spans never overlap each other.
        eligible = [
            i for i, w in enumerate(windows) if w["startIndex"] % DISJOINT_STRIDE == 0
        ]

        n_inject = int(round(target_positive_rate * len(windows)))
        n_inject = max(5, min(n_inject, len(eligible)))

        # Independent RNG stream per (split, object): test parameters cannot be
        # reached or inferred from validation runs.
        rng = np.random.default_rng(
            np.random.SeedSequence(entropy=seed, spawn_key=(split_rank, len(object_id)))
        )

        chosen = sorted(rng.choice(np.array(eligible), size=n_inject, replace=False).tolist())

        injected_flux = flux.copy()
        injections: list[dict] = []

        for k, window_index in enumerate(chosen):
            cls = INJECTION_CLASSES[k % len(INJECTION_CLASSES)]
            window_start = windows[window_index]["startIndex"]
            injected_flux, params = inject(injected_flux, window_start, cls, rng)
            params["windowIndex"] = int(window_index)
            injections.append(params)

        # Injected sample indices per class, for coverage labelling.
        covered = np.zeros(len(flux), dtype=np.int32)
        class_per_sample: dict[int, str] = {}
        for params in injections:
            s, e = params["spanStartIndex"], params["spanEndIndex"]
            covered[s:e] += 1
            for idx in range(s, e):
                class_per_sample[idx] = params["class"]

        features, _ = extract_window_features(
            time_arr, injected_flux, WINDOW_SIZE, STEP_SIZE, MIN_POINTS
        )

        if len(features) != len(windows):
            raise RuntimeError(
                f"window count changed after injection for {object_id}: "
                f"{len(windows)} -> {len(features)}"
            )

        n_pos = n_neg = n_excl = 0
        for i, window in enumerate(windows):
            start, end = window["startIndex"], window["endIndex"]
            inside = int(covered[start:end].sum())

            injection_class = None
            if inside > 0:
                sample_indices = []
                for params in injections:
                    s, e = params["spanStartIndex"], params["spanEndIndex"]
                    lo, hi = max(s, start), min(e, end)
                    if hi > lo:
                        sample_indices.append(params["class"])
                injection_class = sample_indices[0] if sample_indices else None

            if inside == 0:
                label = 0
                n_neg += 1
            elif inside == INJECTION_WIDTH:
                label = 1
                n_pos += 1
            else:
                # Partially covered window: genuine label ambiguity, dropped.
                label = -1
                n_excl += 1

            records.append(
                {
                    "objectId": object_id,
                    "split": split,
                    "noise": round(noise[object_ids.index(object_id)], 8),
                    "windowIndex": i,
                    "startIndex": start,
                    "endIndex": end,
                    "startTime": window["startTime"],
                    "endTime": window["endTime"],
                    "label": label,
                    "injectionClass": injection_class if label == 1 else None,
                    "features": [float(v) for v in features[i]],
                }
            )

        per_object[object_id] = {
            "split": split,
            "sector": curve["sector"],
            "points": int(len(flux)),
            "windows": int(len(windows)),
            "positives": n_pos,
            "negatives": n_neg,
            "excluded": n_excl,
            "injections": len(injections),
            "injectionClasses": {
                cls: sum(1 for p in injections if p["class"] == cls) for cls in INJECTION_CLASSES
            },
            "medianClippedAmplitude": bool(
                np.median([p["amplitudeClipped"] for p in injections]) > 0.5
            ) if injections else None,
            "extractionMs": round(extraction_ms[object_id], 3),
            "seriesChecksum": hashlib.sha256(np.ascontiguousarray(flux).tobytes()).hexdigest()[:16],
        }

    # ------------------------------------------------------------------
    # Write artifacts
    # ------------------------------------------------------------------

    out_dir.mkdir(parents=True, exist_ok=True)
    jsonl_path = out_dir / "ml_benchmark.jsonl"

    with jsonl_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    jsonl_sha = hashlib.sha256(jsonl_path.read_bytes()).hexdigest()

    counts = {"train": 0, "val": 0, "test": 0}
    for record in records:
        if record["label"] == 1:
            counts[record["split"]] += 1

    split_objects = {s: sorted(o for o in object_ids if splits[o] == s) for s in SPLIT_SIZES}

    versions = {"python": platform.python_version(), "numpy": np.__version__}
    try:
        import sklearn

        versions["scikit-learn"] = sklearn.__version__
    except Exception:
        pass
    try:
        import lightkurve

        versions["lightkurve"] = lightkurve.__version__
    except Exception:
        pass

    manifest = {
        "track": "track1_controlled_injection",
        "groundTruth": "synthetic_by_construction",
        "warning": (
            "Window labels reflect injected signals, not confirmed astronomical anomalies. "
            "See evaluation/AUDIT.md section 6.5."
        ),
        "seed": seed,
        "config": {
            "windowSize": WINDOW_SIZE,
            "stepSize": STEP_SIZE,
            "minPoints": MIN_POINTS,
            "injectionWidth": INJECTION_WIDTH,
            "disjointStride": DISJOINT_STRIDE,
            "targetPositiveRate": target_positive_rate,
            "snrRange": list(SNR_RANGE),
            "amplitudeClip": list(AMPLITUDE_CLIP),
            "injectionClasses": list(INJECTION_CLASSES),
            "splitSizes": SPLIT_SIZES,
            "splitUnit": "object",
        },
        "featureNames": list(FEATURE_NAMES),
        "targets": object_ids,
        "splits": split_objects,
        "objects": per_object,
        "windowCounts": {
            "total": len(records),
            "positive": sum(1 for r in records if r["label"] == 1),
            "negative": sum(1 for r in records if r["label"] == 0),
            "excluded": sum(1 for r in records if r["label"] == -1),
            "positiveBySplit": counts,
        },
        "failures": failures,
        "artifacts": {"jsonl": jsonl_path.name, "jsonlSha256": jsonl_sha},
        "versions": versions,
        "builtAtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "buildSeconds": round(time.time() - started, 1),
    }

    manifest_path.write_text(json.dumps(manifest, indent=2), encoding="utf-8")

    print("\nbenchmark written")
    print(f"  windows total={len(records)} pos={manifest['windowCounts']['positive']} "
          f"neg={manifest['windowCounts']['negative']} excluded={manifest['windowCounts']['excluded']}")
    print(f"  splits: train={len(split_objects['train'])}o/{counts['train']}pos "
          f"val={len(split_objects['val'])}o/{counts['val']}pos "
          f"test={len(split_objects['test'])}o/{counts['test']}pos")
    print(f"  sha256={jsonl_sha[:16]}...  build={manifest['buildSeconds']}s")
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default=str(AI_ROOT / "evaluation" / "data"))
    parser.add_argument("--cache-dir", default=str(AI_ROOT / "evaluation" / "data" / "cache"))
    parser.add_argument("--targets", type=int, default=TARGETS_TOTAL)
    parser.add_argument("--seed", type=int, default=MASTER_SEED)
    parser.add_argument("--positive-rate", type=float, default=TARGET_POSITIVE_RATE)
    args = parser.parse_args()

    build(
        out_dir=Path(args.out_dir),
        cache_dir=Path(args.cache_dir),
        n_targets=args.targets,
        seed=args.seed,
        target_positive_rate=args.positive_rate,
    )


if __name__ == "__main__":
    main()
