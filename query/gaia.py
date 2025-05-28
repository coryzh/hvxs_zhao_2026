from astroquery.gaia import Gaia
from typing import List
from astropy.table import Table
from astropy.coordinates import SkyCoord
from astropy.units import Quantity
from tqdm import tqdm
import pandas as pd
import numpy as np


Gaia.MAIN_GAIA_TABLE = "gaiadr3.gaia_source"
default_columns = [
    "designation", "source_id", "ra", "ra_error", "dec", "dec_error",
    "parallax", "parallax_error", "pmra", "pmra_error", "pmdec", "pmdec_error",
    "phot_g_mean_mag", "phot_bp_mean_mag", "phot_rp_mean_mag",
    "nu_eff_used_in_astrometry", "pseudocolour", "ecl_lat",
    "astrometric_params_solved", "ag_gspphot", "ebpminrp_gspphot",
    "azero_gspphot"
]


def gaia_single_source_id_search(source_id: int,
                                 columns: List[str] = None) -> Table:
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


def check_neighbours(df: pd.DataFrame) -> pd.DataFrame:
    n_neighbours = np.zeros(df.shape[0])
    for i, row in df.iterrows():
        id_x = row["ID_x"]
        ra = row["ra_x"]
        dec = row["dec_x"]
        pos_x_err = row["pos_x_err"]
        coord = SkyCoord(ra, dec, frame="icrs", unit="deg")

        r_search = Quantity(2 * pos_x_err, "arcsec")

        print(f"Working on {id_x} ...")
        j = Gaia.cone_search_async(coord, radius=r_search)

        tab = j.get_results()
        n_neighbours[i] = len(tab) - 1

    df["n_neighbours"] = n_neighbours
    return df


def cone_search_closest_neighbour(df: pd.DataFrame, id_col: str = "ID",
                                  ra_col: str = "ra",
                                  dec_col: str = "dec") -> pd.DataFrame:

    closest_rows = []
    for i, row in tqdm(df.iterrows()):
        ra = row[ra_col]
        dec = row[dec_col]
        coord = SkyCoord(ra, dec, frame="icrs", unit="deg")
        j = Gaia.cone_search_async(coord, radius=Quantity(1, "arcmin"))

        tab = j.get_results()
        if len(tab) > 0:
            df_gaia = tab.to_pandas()
            df_gaia["dist"] = df_gaia["dist"] * 3600  # in arcsec
            df_gaia = df_gaia.sort_values(by="dist", ascending=True)
            closest = df_gaia.iloc[0].to_dict()
            closest[id_col] = row[id_col]
            closest_rows.append(closest)

        else:
            closest_rows.append(
                {id_col: row[id_col]}
            )
    df_closest = pd.DataFrame(closest_rows)
    df_results = pd.merge(df, df_closest, how="left", on=id_col)

    return df_results


def main() -> None:
    from pathlib import Path
    in_file_path = Path(
        "/Users/yuezhao/Desktop/local_repos"
        "/rubin_dp1_cdfs/data/catalogues/cdfs/source_catalogue.csv"
    )
    df = pd.read_csv(in_file_path)

    df_agn = df[df["OType"] == "AGN"]

    results = cone_search_closest_neighbour(
        df_agn, id_col="Seq", ra_col="RAJ2000", dec_col="DEJ2000"
    )

    results.to_csv(
        in_file_path.parent / "source_catalogue_agn_w_gaia.csv", index=False
    )


if __name__ == "__main__":
    main()
