import pandas as pd
from utils.distances import FromLiterature
from astropy.coordinates import SkyCoord
import astropy.units as u
from pathlib import Path
from constants import gal_cen
from utils.utility_functions import get_errors
import logging
from log.log_config import configure_logging

configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


def transform_distance_columns(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"Got catalogue shape: {df.shape}")

    logger.info("Adding distance error columns...")
    dist_lo_err = df["r_med_photogeo"] - df["r_lo_photogeo"]
    dist_hi_err = df["r_hi_photogeo"] - df["r_med_photogeo"]

    column_mapping = {
        "r_med_photogeo": "dist_med",
        "ra": "ra_gaia",
        "dec": "dec_gaia",
    }

    columns_to_drop = [
            "r_lo_photogeo", "r_hi_photogeo",
            "r_med_geo", "r_lo_geo", "r_hi_geo"
    ]

    df["e_dist"] = dist_lo_err
    df["E_dist"] = dist_hi_err

    logger.info(f"Renaming distance columns: {column_mapping} ...")
    df = df.rename(columns=column_mapping)

    logger.info(
        f"Dropping unnecessary distance columns: {columns_to_drop} ..."
    )

    df = df.drop(
        columns=columns_to_drop
    )

    logger.info(f"Final catalogue shape: {df.shape}")

    return df


def add_cartesian_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    logger.info(f"Got catalogue, shape: {df_copy.shape}.")
    duplicated_cols_to_check = ["x", "y", "z", "r_gc"]
    duplicated_cols = [
        col for col in duplicated_cols_to_check if col in df_copy.columns
    ]
    df_copy = df_copy.drop(columns=duplicated_cols)

    def get_coords(row: pd.Series):
        dist = FromLiterature(
            row['dist_med'],
            x_lo=row['dist_med'] - row['e_dist'],
            x_hi=row['dist_med'] + row['E_dist']
        )
        d_gamma = dist.fit_gamma()["distribution"]
        d_rand = d_gamma.rvs(1000)
        coords = SkyCoord(
            row['ra_gaia'] * u.deg, row['dec_gaia'] * u.deg,
            distance=d_rand * u.kpc,
            frame="icrs"
        )

        coords_galcen = coords.transform_to(gal_cen)

        x, y, z = (
            coords_galcen.x.value,
            coords_galcen.y.value,
            coords_galcen.z.value
        )

        coords_galcen.representation_type = "cylindrical"
        r_gc = coords_galcen.rho.value

        row_values = []
        for item in [x, y, z, r_gc]:
            med, uperr, loerr = get_errors(item)
            row_values.extend([med, uperr, loerr])
        return row_values

    coord_cols = [
        "x_med", "e_x", "E_x",
        "y_med", "e_y", "E_y",
        "z_med", "e_z", "E_z",
        "r_gc", "e_r_gc", "E_r_gc"
    ]

    coord_df = df_copy.apply(get_coords, axis=1, result_type='expand')
    coord_df.columns = coord_cols
    df_concat = pd.concat([df_copy, coord_df], axis=1)

    return df_concat


def add_quality_bitmask(df: pd.DataFrame) -> pd.DataFrame:
    logger.info(f"Got catalogue, shape: {df.shape}")
    cond_1 = (df["sep_x_g"] / df["pos_x_err"] <= 1)
    cond_2 = (df["parallax_corr"] / df["parallax_error"] >= 5)
    cond_3 = (
        (abs(1 / df["parallax_corr"] - df["dist_med"])
         / df["dist_med"] <= 0.2) & df["parallax_corr"] > 0
    )

    logger.info("Adding quality bitmask column ...")
    df["quality"] = (
        cond_1.astype(int) * (1 << 2) +
        cond_2.astype(int) * (1 << 1) +
        cond_3.astype(int) * (1 << 0)
    )

    return df
