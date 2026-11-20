"""Track 2: weak catalogue proxy labels for the frozen Fluxor TESS targets.

TRACK 2 IS SEPARATE FROM TRACK 1 AND ITS LABELS ARE NOT GROUND TRUTH.

Track 1 labels windows using seeded synthetic injections. Track 2 labels whole
objects using an external catalogue: whether Gaia DR3's variability
classification processed the source (`in_vari_classification_result` in
`gaiadr3.vari_summary`), with the specific class flags recorded alongside where
Gaia assigned them. This is a proxy for "Gaia treats this star as a variability
candidate", nothing more:

  * it is a literature classification of the star, not of the specific window
    or epoch the detector scored;
  * absence from the Gaia variability tables is common for real variables
    (faint, crowded, long-period, or simply not processed), so a 0 is "not in
    the catalogue", not "not variable";
  * the sources were never inspected by a human for this task.

Any metric computed on these labels is reported as a weak-label metric.

Output: evaluation/track2/labels.json (cache; delete or pass --refresh to refetch)

Run:
    python evaluation/track2/build_labels.py
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

AI_ROOT = Path(__file__).resolve().parents[2]
if str(AI_ROOT) not in sys.path:
    sys.path.insert(0, str(AI_ROOT))

DATA_DIR = AI_ROOT / "evaluation" / "data"
OUT_PATH = AI_ROOT / "evaluation" / "track2" / "labels.json"

GAIA_CLASS_FLAGS = (
    "in_vari_rrlyrae",
    "in_vari_cepheid",
    "in_vari_planetary_transit",
    "in_vari_short_timescale",
    "in_vari_long_period_variable",
    "in_vari_eclipsing_binary",
    "in_vari_rotation_modulation",
    "in_vari_ms_oscillator",
    "in_vari_agn",
    "in_vari_microlensing",
    "in_vari_compact_companion",
)


def loadTargets() -> list[str]:
    manifest = json.loads(
        (DATA_DIR / "benchmark_manifest.json").read_text(encoding="utf-8")
    )
    return sorted(manifest["targets"])


def fetchTic(objectIds: list[str]) -> dict[str, dict]:
    """TIC rows (position, brightness, objType, Gaia source id) per target."""

    from astroquery.mast import Catalogs

    rows: dict[str, dict] = {}

    for objectId in objectIds:

        ticId = objectId.replace("TIC ", "").strip()
        entry: dict = {"objectId": objectId, "ticId": ticId, "tic": None, "error": None}

        try:
            table = Catalogs.query_criteria(catalog="TIC", ID=ticId)

            if table is None or len(table) == 0:
                entry["error"] = "no TIC row"
            else:
                row = table[0]
                entry["tic"] = {
                    "ra": float(row["ra"]),
                    "dec": float(row["dec"]),
                    "Tmag": float(row["Tmag"]) if row["Tmag"] is not None else None,
                    "objType": str(row["objType"]),
                    "typeSrc": str(row["typeSrc"]),
                    "gaiaSourceId": (
                        str(int(row["GAIA"])) if row["GAIA"] is not None else None
                    ),
                    "contratio": (
                        float(row["contratio"]) if "contratio" in table.colnames else None
                    ),
                }
        except Exception as error:  # recorded, never silently dropped
            entry["error"] = f"{type(error).__name__}: {error}"

        rows[objectId] = entry
        time.sleep(0.2)

    return rows


def fetchGaiaVariability(sourceIds: list[str]) -> dict[str, dict]:
    """One TAP query for every Gaia source id; missing ids are simply absent."""

    if not sourceIds:
        return {}

    from astroquery.gaia import Gaia

    columns = ["source_id", "in_vari_classification_result"] + list(GAIA_CLASS_FLAGS)

    query = (
        f"SELECT {', '.join(columns)} FROM gaiadr3.vari_summary "
        f"WHERE source_id IN ({', '.join(sourceIds)})"
    )

    job = Gaia.launch_job(query)
    table = job.get_results()

    out: dict[str, dict] = {}

    for row in table:
        record = {"inVariClassificationResult": int(row["in_vari_classification_result"])}
        classes = [flag.replace("in_vari_", "") for flag in GAIA_CLASS_FLAGS if int(row[flag]) == 1]
        record["gaiaClasses"] = classes
        out[str(int(row["source_id"]))] = record

    return out


def labelFromGaia(gaiaRecord: dict | None) -> int:
    """Weak binary label from Gaia DR3's own variability flag.

    1 when the source appears in `gaiadr3.vari_summary` with
    `in_vari_classification_result == 1`, i.e. Gaia passed it through the
    variability classifier. A specific class (`in_vari_*`) is recorded when
    Gaia assigned one, but is not required: most classified sources carry none.
    0 means "not in the catalogue", never "not variable".
    """

    if not gaiaRecord:
        return 0

    if gaiaRecord.get("gaiaClasses"):
        return 1

    return 1 if gaiaRecord.get("inVariClassificationResult") == 1 else 0


def build(refresh: bool = False) -> dict:

    if OUT_PATH.exists() and not refresh:
        return json.loads(OUT_PATH.read_text(encoding="utf-8"))

    targets = loadTargets()
    tic = fetchTic(targets)

    sourceIds = sorted(
        {
            entry["tic"]["gaiaSourceId"]
            for entry in tic.values()
            if entry.get("tic") and entry["tic"].get("gaiaSourceId")
        }
    )

    gaia = fetchGaiaVariability(sourceIds)

    objects: dict[str, dict] = {}

    for objectId in targets:
        entry = tic[objectId]
        gaiaId = (entry.get("tic") or {}).get("gaiaSourceId")
        gaiaRecord = gaia.get(gaiaId) if gaiaId else None

        objects[objectId] = {
            **entry,
            "gaiaSourceId": gaiaId,
            "gaia": gaiaRecord,
            "weakLabel": labelFromGaia(gaiaRecord),
        }

    payload = {
        "track": "track2_catalogue_proxy",
        "groundTruth": "weak_proxy_not_ground_truth",
        "warning": (
            "Labels are an external catalogue classification of the object, not "
            "confirmation that any scored window is an anomaly. See "
            "evaluation/reports/track2_catalog_proxy.md."
        ),
        "labelDefinition": (
            "weakLabel = 1 if the source is present in gaiadr3.vari_summary with "
            "in_vari_classification_result = 1 (Gaia ran it through variability "
            "classification), else 0. Specific in_vari_* classes are recorded "
            "when Gaia assigned one but are not required. A 0 means 'not in the "
            "catalogue', not 'not variable'."
        ),
        "sources": {
            "tic": "MAST TIC (astroquery.mast.Catalogs.query_criteria, catalog=TIC)",
            "gaia": "Gaia DR3 gaiadr3.vari_summary via Gaia TAP",
        },
        "fetchedAtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "counts": {
            "objects": len(objects),
            "withTic": sum(1 for e in objects.values() if e.get("tic")),
            "withGaiaId": sum(1 for e in objects.values() if e.get("gaiaSourceId")),
            "inGaiaVariabilityTable": sum(1 for e in objects.values() if e.get("gaia")),
            "positive": sum(e["weakLabel"] for e in objects.values()),
        },
        "objects": objects,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    return payload


def main() -> None:

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true")
    args = parser.parse_args()

    payload = build(refresh=args.refresh)
    print(json.dumps(payload["counts"], indent=2))
    print(f"wrote {OUT_PATH}")


if __name__ == "__main__":
    main()
