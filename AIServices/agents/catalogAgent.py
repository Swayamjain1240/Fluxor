from graph.state import FluxorState

from tools.simbadTool import (
    get_simbad_object,
    get_simbad_by_coordinates
)

from tools.vizierTool import (
    query_vizier
)


def catalogAgent(
    state: FluxorState
):

    objectId = state.get(
        "objectId"
    )

    metadata = state.get(
        "metadata",
        {}
    )


    # -------------------------
    # SIMBAD
    # -------------------------

    simbadResult = (
        get_simbad_object(
            objectId
        )
    )


    ra = metadata.get("ra")
    dec = metadata.get("dec")


    # If object ID cannot be resolved,
    # try coordinate search.

    if (
        not simbadResult.get("found")
        and
        ra is not None
        and
        dec is not None
    ):

        simbadResult = (
            get_simbad_by_coordinates(
                float(ra),
                float(dec)
            )
        )


    # -------------------------
    # VizieR
    # -------------------------

    vizierResult = {
        "found": False,
        "catalogs": []
    }


    if (
        ra is not None
        and
        dec is not None
    ):

        vizierResult = query_vizier(
            float(ra),
            float(dec)
        )


    return {

        "catalogData": {

            "simbad":
                simbadResult,

            "vizier":
                vizierResult
        },

        "status":
            "catalog_complete"
    }