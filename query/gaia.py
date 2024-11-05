from astroquery.gaia import Gaia
from typing import List
from astropy.table import Table


Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
default_columns = [
    "designation", "source_id", "ra", "ra_error", "dec", "dec_error", "parallax", "parallax_error",
    "pmra", "pmra_error", "pmdec", "pmdec_error", "phot_g_mean_mag", "phot_bp_mean_mag", "phot_rp_mean_mag",
    "nu_eff_used_in_astrometry", "pseudocolour", "ecl_lat", "astrometric_params_solved", "ag_gspphot",
    "ebpminrp_gspphot", "azero_gspphot"
]


def gaia_single_source_id_search(source_id: int, columns: List[str] = None) -> Table:
    if columns is None:
        columns = default_columns

    query = f"""
    SELECT {",".join(columns)}, gd.*
    FROM gaiadr3.gaia_source AS dr3
    JOIN external.gaiaedr3_distance AS gd USING (source_id)
    WHERE source_id='{source_id}'
    """

    job = Gaia.launch_job(query)

    results = job.get_results()

    return results
