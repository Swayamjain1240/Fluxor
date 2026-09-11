from astroquery.simbad import Simbad

from astropy.coordinates import SkyCoord
import astropy.units as u


def _safe_value(value):
    """
    Convert Astropy values into JSON-friendly values.
    """

    try:
        if value is None:
            return None

        if hasattr(value, "item"):
            value = value.item()

        if isinstance(value, bytes):
            return value.decode("utf-8")

        return value

    except Exception:
        return str(value)


def _table_row_to_dict(table, row_index=0):

    row = table[row_index]

    result = {}

    for column in table.colnames:

        try:
            result[column] = _safe_value(
                row[column]
            )

        except Exception:
            result[column] = None

    return result


def get_simbad_object(object_id: str):
    """
    Search SIMBAD using an astronomical object identifier.
    """

    try:

        simbad = Simbad()

        # Extra scientific information
        simbad.add_votable_fields(
            "otype",
            "sp_type"
        )

        result = simbad.query_object(
            object_id
        )


        if result is None or len(result) == 0:

            return {
                "found": False,
                "objectId": object_id,
                "source": "SIMBAD",
                "data": None
            }


        data = _table_row_to_dict(
            result
        )


        return {
            "found": True,
            "objectId": object_id,
            "source": "SIMBAD",
            "data": data
        }


    except Exception as error:

        return {
            "found": False,
            "objectId": object_id,
            "source": "SIMBAD",
            "error": str(error)
        }


def get_simbad_by_coordinates(
    ra: float,
    dec: float,
    radius_arcsec: float = 10
):
    """
    Search objects around coordinates.

    Useful when SIMBAD cannot resolve something
    such as a particular TIC identifier directly.
    """

    try:

        coordinate = SkyCoord(
            ra=ra * u.degree,
            dec=dec * u.degree,
            frame="icrs"
        )


        simbad = Simbad()

        simbad.add_votable_fields(
            "otype",
            "sp_type"
        )


        result = simbad.query_region(
            coordinate,
            radius=radius_arcsec * u.arcsec
        )


        if result is None or len(result) == 0:

            return {
                "found": False,
                "source": "SIMBAD",
                "data": []
            }


        objects = []

        for index in range(
            min(len(result), 10)
        ):

            objects.append(
                _table_row_to_dict(
                    result,
                    index
                )
            )


        return {
            "found": True,
            "source": "SIMBAD",
            "count": len(objects),
            "data": objects
        }


    except Exception as error:

        return {
            "found": False,
            "source": "SIMBAD",
            "error": str(error)
        }