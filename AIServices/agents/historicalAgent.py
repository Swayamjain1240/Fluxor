import numpy as np

from graph.state import FluxorState

from tools.mastTool import (
    fetch_light_curve
)


def historicalAgent(
    state: FluxorState
):

    objectId = state.get(
        "objectId"
    )

    metadata = state.get(
        "metadata",
        {}
    )


    mission = metadata.get(
        "mission",
        "TESS"
    )


    try:

        historical = fetch_light_curve(
            object_id=objectId,
            source=mission
        )


        time = np.asarray(
            historical["time"],
            dtype=float
        )

        flux = np.asarray(
            historical["flux"],
            dtype=float
        )


        valid = (
            np.isfinite(time)
            &
            np.isfinite(flux)
        )

        time = time[valid]
        flux = flux[valid]


        if len(flux) == 0:

            raise ValueError(
                "No valid historical light curve points"
            )


        medianFlux = float(
            np.median(flux)
        )

        stdFlux = float(
            np.std(flux)
        )

        amplitude = float(
            np.max(flux)
            -
            np.min(flux)
        )


        if stdFlux > 0:

            extremeMask = (
                np.abs(
                    flux - medianFlux
                )
                >
                3 * stdFlux
            )

            extremeEvents = int(
                np.sum(extremeMask)
            )

        else:

            extremeEvents = 0


        duration = 0.0

        if len(time) > 1:

            duration = float(
                np.max(time)
                -
                np.min(time)
            )


        historicalData = {

            "mission":
                mission,

            "totalPoints":
                len(flux),

            "observationDurationDays":
                duration,

            "medianFlux":
                medianFlux,

            "standardDeviation":
                stdFlux,

            "amplitude":
                amplitude,

            "extremePointCount":
                extremeEvents
        }


    except Exception as error:

        historicalData = {

            "mission":
                mission,

            "available":
                False,

            "error":
                str(error)
        }


    return {

        "historicalData":
            historicalData,

        "status":
            "historical_complete"
    }