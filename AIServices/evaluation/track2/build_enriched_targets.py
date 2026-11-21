"""Track 2 (enriched): build an object list sampled on Gaia variability class.

The first Track 2 list was the 40 frozen Track 1 targets, taken as they came.
Only 5 landed in Gaia's variability tables and just one carried a specific
class, so the ranking rested on a single eclipsing binary.

This builds the list the other way round: start from Gaia DR3 sources carrying a
specific variability class inside the TESS Sector 1 field, keep those that have
TESS two-minute photometry, and pair each with a magnitude-matched control that
has no Gaia variability classification. Positives and negatives are balanced by
design; AUC is prevalence-invariant, but the base rate is a sampling choice and
the report says so.

Access notes, measured on this machine (2026-11-20), because they shape the code:

  * a bulk `Observations.query_criteria` for the whole Sector 1 target list
    either returns nothing or hangs for minutes, so it is not used;
  * `lightkurve.search_lightcurve` on sky coordinates takes ~35 s per object;
  * resolving the TIC id by position takes 0.5-3 s and searching by TIC takes
    9-13 s, so ids are resolved first and the search is done per TIC;
  * most classed Gaia sources in the field have no TESS two-minute data at all,
    so a "no curve" outcome is expected and recorded, not an error.

Labels remain weak: a Gaia class describes the star, not any scored window.

Outputs (all under evaluation/track2/enriched/):
    labels.json          objects with class, magnitude, weakLabel and curve provenance
    cache/TIC_<id>.npz   one TESS light curve per object (sector recorded)

Run:
    python evaluation/track2/build_enriched_targets.py --per-class 4
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
import warnings
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

import numpy as np  # noqa: E402

OUT_DIR = AI_ROOT / "evaluation" / "track2" / "enriched"
CACHE_DIR = OUT_DIR / "cache"
LABELS = OUT_DIR / "labels.json"

FIELD_CENTRE = (90.0, -66.56)  # south ecliptic pole, inside TESS Sector 1
FIELD_RADIUS_DEG = 15.0
MAG_RANGE = (8.0, 13.0)
MAG_MATCH_TOLERANCE = 0.35
TIC_MATCH_ARCSEC = 3.0

CLASS_PRIORITY = (
    "in_vari_eclipsing_binary",
    "in_vari_rrlyrae",
    "in_vari_cepheid",
    "in_vari_rotation_modulation",
    "in_vari_long_period_variable",
    "in_vari_short_timescale",
)

# Fetched with +1 so a full page is detectable as truncation rather than silent.
POOL_LIMIT = 6000

GAIA_FIELDS = ", ".join("v." + name for name in CLASS_PRIORITY)


def launchWithRetry(Gaia, query: str, attempts: int = 3):
    """Gaia TAP returns 408/500/ValueError under load; retry before giving up."""

    lastError = None
    for attempt in range(1, attempts + 1):
        try:
            return Gaia.launch_job(query).get_results()
        except Exception as error:
            lastError = error
            print(
                f"    gaia query attempt {attempt}/{attempts} failed: "
                f"{type(error).__name__}: {str(error)[:120]}",
                flush=True,
            )
            if attempt < attempts:
                time.sleep(20 * attempt)

    raise RuntimeError(
        f"Gaia query failed after {attempts} attempts: "
        f"{type(lastError).__name__}: {lastError}"
    ) from lastError


# ---------------------------------------------------------------------------
# Gaia pools
# ---------------------------------------------------------------------------

def fetchVariabilityPool() -> dict:
    """Gaia sources in the field with per-class flags (may carry none).

    Returns the rows plus a `truncated` flag. Truncation matters here more than
    anywhere else in the build: these ids are subtracted from the control pool,
    so a partial pool would let variability-classified stars into the negatives.
    The caller refuses to continue when it happens.
    """

    from astroquery.gaia import Gaia

    query = f"""
SELECT TOP {POOL_LIMIT + 1} v.source_id, g.ra, g.dec, g.phot_g_mean_mag, {GAIA_FIELDS}
FROM gaiadr3.vari_summary AS v
JOIN gaiadr3.gaia_source AS g ON v.source_id = g.source_id
WHERE 1=CONTAINS(POINT('ICRS', g.ra, g.dec),
  CIRCLE('ICRS', {FIELD_CENTRE[0]}, {FIELD_CENTRE[1]}, {FIELD_RADIUS_DEG}))
  AND g.phot_g_mean_mag BETWEEN {MAG_RANGE[0]} AND {MAG_RANGE[1]}
"""

    table = launchWithRetry(Gaia, query)

    rows = []
    malformed = 0

    for row in table[:POOL_LIMIT]:
        try:
            classes = [
                name.replace("in_vari_", "")
                for name in CLASS_PRIORITY
                if bool(row[name])
            ]
            rows.append(
                {
                    "sourceId": str(int(row["source_id"])),
                    "ra": float(row["ra"]),
                    "dec": float(row["dec"]),
                    "gMag": float(row["phot_g_mean_mag"]),
                    "classes": classes,
                }
            )
        except (TypeError, ValueError):
            malformed += 1

    return {
        "rows": rows,
        "truncated": len(table) > POOL_LIMIT,
        "limit": POOL_LIMIT,
        "malformedRows": malformed,
    }


def magnitudeBands(bands: int) -> list[tuple[float, float]]:
    """Split MAG_RANGE into disjoint, contiguous bands."""

    step = (MAG_RANGE[1] - MAG_RANGE[0]) / bands
    edges = [MAG_RANGE[0] + step * index for index in range(bands)] + [MAG_RANGE[1]]
    return [(edges[index], edges[index + 1]) for index in range(bands)]


def fetchControlPool(
    knownIds: set[str], bands: int, pageSize: int
) -> dict:
    """Gaia sources in the field absent from vari_summary, by magnitude bands.

    Pagination is by disjoint magnitude band rather than a `source_id` cursor.
    Both were tried against the live service: the cone + magnitude query with
    `ORDER BY source_id` completes in about a minute for 2000 rows, but adding
    any extra non-indexed predicate -- `MOD(source_id, 50) = 0`, or even
    `source_id > <cursor>` -- flips the planner to a scan and returns TAP 408.
    Disjoint bands keep every query in the shape that works, cannot overlap, and
    still dedupe by id because a source at a band edge is queried once.

    Controls are separated from positives client-side: ids in the variability
    pool are dropped here and the caller asserts disjointness.
    """

    from astroquery.gaia import Gaia

    rows: list[dict] = []
    seen: set[str] = set()
    duplicates = 0
    overlapped = 0
    malformed = 0
    truncatedBands: list[list[float]] = []
    failedBands: list[dict] = []
    bandRanges = magnitudeBands(bands)

    for low, high in bandRanges:

        # Fetch one extra row so a full page is recognisable as truncation.
        query = f"""
SELECT TOP {pageSize + 1} source_id, ra, dec, phot_g_mean_mag
FROM gaiadr3.gaia_source
WHERE 1=CONTAINS(POINT('ICRS', ra, dec),
  CIRCLE('ICRS', {FIELD_CENTRE[0]}, {FIELD_CENTRE[1]}, {FIELD_RADIUS_DEG}))
  AND phot_g_mean_mag BETWEEN {low} AND {high}
ORDER BY source_id
"""

        try:
            table = launchWithRetry(Gaia, query)
        except RuntimeError as error:
            # A band that never answers is recorded and skipped: the controls
            # are a convenience sample, and a partial pool is still valid as
            # long as it is reported rather than silently thinner.
            failedBands.append({"band": [low, high], "error": str(error)[:200]})
            print(f"    band {low}-{high} failed; continuing without it", flush=True)
            continue

        if table is None or len(table) == 0:
            continue

        if len(table) > pageSize:
            truncatedBands.append([round(low, 3), round(high, 3)])
            table = table[:pageSize]

        for row in table:
            try:
                sourceId = str(int(row["source_id"]))
                entry = {
                    "sourceId": sourceId,
                    "ra": float(row["ra"]),
                    "dec": float(row["dec"]),
                    "gMag": float(row["phot_g_mean_mag"]),
                    "classes": [],
                }
            except (TypeError, ValueError):
                malformed += 1
                continue

            if sourceId in seen:
                duplicates += 1
                continue
            seen.add(sourceId)
            if sourceId in knownIds:
                overlapped += 1
                continue
            rows.append(entry)

    return {
        "rows": rows,
        "bands": bandRanges,
        "pagesFetched": len(bandRanges) - len(failedBands),
        "duplicatesDropped": duplicates,
        "overlappedWithVariabilityPool": overlapped,
        "malformedRows": malformed,
        "truncatedBands": truncatedBands,
        "failedBands": failedBands,
    }


# ---------------------------------------------------------------------------
# TESS light curves
# ---------------------------------------------------------------------------

def cachePath(ticId: str) -> Path:
    return CACHE_DIR / f"TIC_{ticId}.npz"


def resolveTic(ra: float, dec: float) -> str | None:
    """Nearest TIC id within TIC_MATCH_ARCSEC of the Gaia position.

    The cone can return several TIC entries, so the first row is not
    necessarily the counterpart; the nearest on-sky match is used instead and
    the separation is returned with the id for the record.
    """

    from astroquery.mast import Catalogs
    from astropy.coordinates import SkyCoord
    import astropy.units as u

    coordinate = SkyCoord(ra=ra * u.deg, dec=dec * u.deg)
    table = Catalogs.query_region(
        coordinate, radius=TIC_MATCH_ARCSEC * u.arcsec, catalog="TIC"
    )

    if table is None or len(table) == 0:
        return None

    separations = []
    for row in table:
        candidate = SkyCoord(ra=float(row["ra"]) * u.deg, dec=float(row["dec"]) * u.deg)
        separations.append((coordinate.separation(candidate).arcsec, str(int(row["ID"]))))

    separation, ticId = min(separations)

    if separation > TIC_MATCH_ARCSEC:
        return None

    return ticId


def fetchCurve(ticId: str) -> dict | None:
    """One two-minute TESS curve for a TIC id, cached as npz."""

    import lightkurve as lk

    path = cachePath(ticId)
    if path.exists():
        try:
            with np.load(path) as data:
                return {
                    "cached": True,
                    "sector": int(data["sector"]),
                    "points": int(len(data["flux"])),
                }
        except Exception:
            # A truncated file from an interrupted run must not poison the
            # cache: drop it and download again.
            path.unlink(missing_ok=True)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        search = lk.search_lightcurve(f"TIC {ticId}", mission="TESS", exptime=120)

    if search is None or len(search) == 0:
        return None

    curve = search[0].download()
    if curve is None:
        return None

    timeArr = np.asarray(curve.time.value, dtype=float)
    fluxArr = np.asarray(curve.flux.value, dtype=float)
    valid = np.isfinite(timeArr) & np.isfinite(fluxArr)

    if valid.sum() < 500:
        return None

    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Write beside the target and rename, so an interrupted save cannot leave a
    # half-written npz at the path a later run trusts.
    temporary = path.with_suffix(".tmp.npz")
    np.savez_compressed(
        temporary,
        time=timeArr[valid],
        flux=fluxArr[valid],
        sector=np.int32(curve.meta.get("SECTOR", -1)),
    )
    os.replace(temporary, path)

    return {"cached": False, "sector": int(curve.meta.get("SECTOR", -1)), "points": int(valid.sum())}


# ---------------------------------------------------------------------------
# Sampling
# ---------------------------------------------------------------------------

def takePositives(pool: list[dict], perClass: int) -> list[dict]:
    """Brightest-first, quota per class, no source used twice."""

    chosen: list[dict] = []
    used: set[str] = set()

    for className in ("eclipsing_binary", "rotation_modulation",
                      "long_period_variable", "short_timescale",
                      "rrlyrae", "cepheid"):
        ofClass = sorted(
            (row for row in pool if row["classes"] and row["classes"][0] == className),
            key=lambda row: row["gMag"],
        )
        for row in ofClass[:perClass]:
            if row["sourceId"] in used:
                continue
            used.add(row["sourceId"])
            chosen.append({**row, "label": 1, "primaryClass": className})

    return chosen


def matchNegatives(positives: list[dict], controls: list[dict]) -> list[dict]:
    """One control per positive, nearest in magnitude, each used once."""

    chosen: list[dict] = []
    used: set[str] = set()
    ordered = sorted(controls, key=lambda row: row["gMag"])

    for positive in sorted(positives, key=lambda row: row["gMag"]):
        best = None
        bestDelta = None
        for control in ordered:
            if control["sourceId"] in used:
                continue
            delta = abs(control["gMag"] - positive["gMag"])
            if delta > MAG_MATCH_TOLERANCE:
                continue
            if bestDelta is None or delta < bestDelta:
                best, bestDelta = control, delta
        if best is not None:
            used.add(best["sourceId"])
            chosen.append({**best, "label": 0, "primaryClass": None})

    return chosen


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def writeLabels(
    objects: dict, failures: list[dict], args, extra: dict | None = None
) -> None:

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
                "track": "track2_enriched",
                "groundTruth": "weak_proxy_not_ground_truth",
                "labelDefinition": (
                    "weakLabel = 1 when Gaia DR3 assigns a specific variability class "
                    "(in_vari_*); 0 for a magnitude-matched field source absent from "
                    "gaiadr3.vari_summary."
                ),
                "sampling": {
                    "fieldCentre": FIELD_CENTRE,
                    "fieldRadiusDeg": FIELD_RADIUS_DEG,
                    "magRange": MAG_RANGE,
                    "perClassCap": args.per_class,
                    "magMatchTolerance": MAG_MATCH_TOLERANCE,
                    "balancedByDesign": True,
                    "cadence": "TESS 2-minute, first available sector (recorded per object)",
                },
                "sources": {
                    "gaia": "Gaia DR3 gaiadr3.vari_summary + gaiadr3.gaia_source via TAP",
                    "tic": "MAST TIC via astroquery.mast.Catalogs.query_region",
                    "tess": "lightkurve search_lightcurve by TIC id, exptime=120",
                },
                "counts": {
                    "objects": len(objects),
                    "positive": sum(o["weakLabel"] for o in objects.values()),
                    "negative": sum(1 - o["weakLabel"] for o in objects.values()),
                },
                "failures": failures,
                "objects": objects,
    }

    if extra:
        payload.update(extra)

    # Atomic replace: an interrupted build must not leave unparsable metadata,
    # and every intermediate write is marked complete=false.
    temporary = LABELS.with_suffix(".tmp.json")
    temporary.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, LABELS)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-class", type=int, default=4)
    parser.add_argument("--control-bands", type=int, default=3)
    parser.add_argument("--control-page-size", type=int, default=2000)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="query and match only: validate counts and separation, download nothing",
    )
    args = parser.parse_args()

    if args.per_class < 1 or args.control_bands < 1 or args.control_page_size < 2:
        parser.error("--per-class and --control-bands must be >= 1, --control-page-size >= 2")

    warnings.filterwarnings("ignore")

    print("querying Gaia variability pool ...", flush=True)
    poolResult = fetchVariabilityPool()
    pool = poolResult["rows"]
    classed = [row for row in pool if row["classes"]]
    print(
        f"  field rows: {len(pool)}, with a class: {len(classed)}"
        f" ({poolResult['malformedRows']} malformed rows skipped)",
        flush=True,
    )

    if poolResult["truncated"]:
        raise SystemExit(
            f"variability pool hit TOP {poolResult['limit']}: the control pool cannot "
            "be cleaned of variability sources. Narrow MAG_RANGE or add pagination "
            "before building labels."
        )

    positives = takePositives(pool, args.per_class)
    print(f"  positive candidates: {len(positives)}", flush=True)

    # The full control pool, not a brightness slice: truncating it before the
    # magnitude match starved positives fainter than the slice edge.
    knownIds = {row["sourceId"] for row in pool}
    controls = fetchControlPool(
        knownIds, args.control_bands, args.control_page_size
    )
    negatives = matchNegatives(positives, controls["rows"])

    print(
        f"  control sample: {len(controls['rows'])} rows from "
        f"{controls['pagesFetched']} of {len(controls['bands'])} magnitude band(s), "
        f"{controls['duplicatesDropped']} duplicates dropped, "
        f"{controls['overlappedWithVariabilityPool']} dropped as variability-pool members, "
        f"{controls['malformedRows']} malformed rows skipped",
        flush=True,
    )

    # Reported, never silent: a capped or failed band means the control pool is
    # thinner or brighter-than-thought, which the dataset must record.
    if controls["truncatedBands"]:
        print(
            f"  WARNING: bands reached TOP {args.control_page_size} and were capped: "
            f"{controls['truncatedBands']}",
            flush=True,
        )
    if controls["failedBands"]:
        print(
            f"  WARNING: {len(controls['failedBands'])} band(s) failed after retries: "
            f"{[round(b['band'][0], 2) for b in controls['failedBands']]}",
            flush=True,
        )

    if not controls["rows"]:
        raise SystemExit("no control sources returned; refusing to build a one-class dataset")

    samplingMeta = {
        "controlBands": [[round(low, 3), round(high, 3)] for low, high in controls["bands"]],
        "controlPageSize": args.control_page_size,
        "controlRows": len(controls["rows"]),
        "controlTruncatedBands": controls["truncatedBands"],
        "controlFailedBands": controls["failedBands"],
        "positiveCandidates": len(positives),
        "variabilityPoolRows": len(pool),
    }

    # Separation invariant: a source is a positive or a control, never both.
    overlap = {row["sourceId"] for row in positives} & {
        row["sourceId"] for row in negatives
    }
    if overlap:
        raise SystemExit(f"positive/control overlap on {len(overlap)} sources")

    if len(negatives) < len(positives):
        print(
            f"  WARNING: {len(positives) - len(negatives)} positive(s) left without a "
            f"magnitude-matched control; balance is {len(positives)}:{len(negatives)}",
            flush=True,
        )

    print(
        f"  magnitude-matched controls: {len(negatives)} "
        f"(overlap with positives: {len(overlap)})",
        flush=True,
    )

    if args.dry_run:

        perClass: dict[str, int] = {}
        for row in positives:
            perClass[row["primaryClass"]] = perClass.get(row["primaryClass"], 0) + 1

        print("  dry run: no TIC resolution, no downloads", flush=True)
        print(f"  positives by class: {perClass}", flush=True)
        if positives and negatives:
            print(
                f"  positive magnitudes: {min(r['gMag'] for r in positives):.2f}-"
                f"{max(r['gMag'] for r in positives):.2f}; controls: "
                f"{min(r['gMag'] for r in negatives):.2f}-"
                f"{max(r['gMag'] for r in negatives):.2f}",
                flush=True,
            )
        print(
            f"  bands fetched: {controls['pagesFetched']} of {args.control_bands}, "
            f"truncated: {controls['truncatedBands'] or 'none'}",
            flush=True,
        )
        print("  NOT a validated dataset: no TIC resolved, no curves downloaded", flush=True)
        return

    objects: dict[str, dict] = {}
    failures: list[dict] = []

    for candidate in positives + negatives:

        label = candidate["label"]

        try:
            ticId = resolveTic(candidate["ra"], candidate["dec"])
        except Exception as error:
            failures.append(
                {"gaiaSourceId": candidate["sourceId"], "label": label,
                 "error": f"TIC: {type(error).__name__}: {error}"}
            )
            continue

        if ticId is None:
            failures.append(
                {"gaiaSourceId": candidate["sourceId"], "label": label, "error": "no TIC match"}
            )
            continue

        objectId = f"TIC {ticId}"

        # Two Gaia sources can resolve to the same TIC id; keep the first so an
        # object is never counted twice with contradictory labels.
        if objectId in objects:
            failures.append(
                {"objectId": objectId, "label": label,
                 "error": "duplicate TIC id already used by another source"}
            )
            continue

        try:
            curve = fetchCurve(ticId)
        except Exception as error:
            failures.append(
                {"objectId": objectId, "label": label,
                 "error": f"curve: {type(error).__name__}: {error}"}
            )
            continue

        if curve is None:
            failures.append(
                {"objectId": objectId, "label": label, "error": "no TESS 2-minute curve"}
            )
            continue

        objects[objectId] = {
            "objectId": objectId,
            "gaiaSourceId": candidate["sourceId"],
            "weakLabel": label,
            "gaiaClasses": candidate["classes"],
            "primaryClass": candidate["primaryClass"],
            "tic": {
                "ra": candidate["ra"],
                "dec": candidate["dec"],
                "Tmag": round(candidate["gMag"], 3),
                "objType": candidate["primaryClass"] or "unclassified",
                "typeSrc": "Gaia DR3",
                "gaiaSourceId": candidate["sourceId"],
            },
            "gaia": {"gaiaClasses": candidate["classes"]},
            "curve": {
                "file": cachePath(ticId).name,
                "sector": curve["sector"],
                "points": curve["points"],
            },
        }

        writeLabels(objects, failures, args, {"complete": False, **samplingMeta})

        print(
            f"  [{len(objects):3d}] {objectId} label={label} "
            f"class={candidate['primaryClass']} mag={candidate['gMag']:.2f} "
            f"sector={curve['sector']} points={curve['points']}",
            flush=True,
        )

    writeLabels(objects, failures, args, {"complete": True, **samplingMeta})

    built = sum(o["weakLabel"] for o in objects.values())
    print(
        f"\nbuilt {len(objects)} objects: {built} positive, "
        f"{len(objects) - built} negative, {len(failures)} skipped",
        flush=True,
    )
    print(f"wrote {LABELS} (complete=true)", flush=True)


if __name__ == "__main__":
    main()
