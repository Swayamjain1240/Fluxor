from astroquery.vizier import Vizier

from astropy.coordinates import SkyCoord
import astropy.units as u


def _safe_value(value):

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


def _row_to_dict(table, row):

    result = {}

    for column in table.colnames:

        try:

            result[column] = _safe_value(
                row[column]
            )

        except Exception:

            result[column] = None

    return result


def query_vizier(
    ra: float,
    dec: float,
    radius_arcsec: float = 10,
    max_catalogs: int = 5,
    max_rows_per_catalog: int = 5
):

    try:

        coordinate = SkyCoord(
            ra=ra * u.degree,
            dec=dec * u.degree,
            frame="icrs"
        )


        vizier = Vizier(
            columns=["**"],
            row_limit=max_rows_per_catalog
        )


        result = vizier.query_region(
            coordinate,
            radius=radius_arcsec * u.arcsec
        )


        if result is None or len(result) == 0:

            return {
                "found": False,
                "source": "VizieR",
                "catalogs": []
            }


        catalogs = []


        for table_index, table in enumerate(
            result[:max_catalogs]
        ):

            rows = []


            for row in table[
                :max_rows_per_catalog
            ]:

                rows.append(
                    _row_to_dict(
                        table,
                        row
                    )
                )


            catalogs.append({

                "catalog":
                    str(
                        table.meta.get(
                            "name",
                            f"catalog_{table_index}"
                        )
                    ),

                "description":
                    str(
                        table.meta.get(
                            "description",
                            ""
                        )
                    ),

                "rows":
                    rows
            })


        return {
            "found": True,
            "source": "VizieR",
            "catalogCount":
                len(catalogs),
            "catalogs":
                catalogs
        }


    except Exception as error:

        return {
            "found": False,
            "source": "VizieR",
            "error": str(error),
            "catalogs": []
        }