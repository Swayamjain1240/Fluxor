import lightkurve as lk
import numpy as np

MISSION_MAP={
    "TESS":"TESS",
    "KEPLER":"Kepler",
    "K2":"K2",
}

def fetch_light_curve(object_id: str, source:str="TESS"):
    mission = MISSION_MAP.get(source.upper())
    if not mission:
        raise ValueError(
            f"Unsupported photometric source:{source}"
        )

    search_result = lk.search_lightcurve(object_id,mission=mission)
    if len(search_result) == 0:
        raise ValueError(
            f"No {mission} light curve found for {object_id}"
        )

    collection = search_result.download_all()
    if collection is None or len(collection) == 0:
        raise ValueError(
            f"Unable to download light curve for {object_id}"
        )

    light_curve = collection.stitch()
    light_curve = light_curve.remove_nans()

    time = np.asarray(
        light_curve.time.value,
        dtype=float
    )

    flux = np.asarray(
        light_curve.flux.value,
        dtype=float
    )

    return {
        "objectId": object_id,
        "mission": mission,
        "time": time,
        "flux": flux,
        "metadata": {
            "mission": mission,
            "points": len(time),
            "targetId": str(
                light_curve.meta.get(
                    "TARGETID",
                    object_id
                )
            )
        }
    }