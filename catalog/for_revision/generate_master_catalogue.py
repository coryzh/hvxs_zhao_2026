import logging
import pandas as pd
import config
import data_schema as ds
from utils.calc_flux import calculate_optical_flux
from catalog.manipulate.parallax_zeropoint_correction import correct_zp
from log.log_config import configure_logging
from pathlib import Path
from typing import Literal
from catalog.for_revision.auto_correlate_xray_catalogues import (
    _concatenate_catalogues
)

configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


def _get_xray_catalogue_path(survey_name: str = "csc") -> Path:
    logger.info(
        f"Getting X-ray catalogue path for survey '{survey_name}' ..."
    )
    file_path = (
        config.ROOT_DIR / "results"
        / survey_name / "catalogues" / "nway_match"
        / f"{survey_name}_confident_point_sources_poserr_rescaled.csv"
    )

    return file_path


def _load_xray_catalogue(survey_name: str = "csc") -> pd.DataFrame:

    file_path = _get_xray_catalogue_path(survey_name=survey_name)
    df = pd.read_csv(file_path)
    logger.info(
        f"X-ray catalogue for survey '{survey_name}' loaded: "
        f"{df.shape[0]} rows."
    )
    return df


def _get_survey_sub_df_from_concatenated_catalogue(
        df: pd.DataFrame, survey_name: str
) -> pd.DataFrame:
    """Get a subset of the DataFrame for a specific survey.

    Parameters
    ----------
    df : pd.DataFrame
        The concatenated catalogue DataFrame.
    survey_name : str
        The name of the survey to filter by.

    Returns
    -------
    pd.DataFrame
        A subset of the DataFrame for the specified survey.
    """
    df_copy = df.copy()
    survey_identifier = config.SURVEY_ID_IDENTIFIERS[survey_name]

    _filter = (
        df_copy[ds.CombinedCatalogueSchema.ID_x]
        .str.contains(survey_identifier)
    )
    n_rows = _filter.sum()
    logger.info(
        f"Number of rows for survey '{survey_name}': {n_rows}"
    )

    df_survey = df_copy[_filter].reset_index(drop=True)

    return df_survey


def _zp_correction(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()
    logger.info("Applying zero-point correction to parallax...")

    df_copy = correct_zp(df_copy, verbose=False)

    return df_copy


def _load_df(
        option: Literal[
            'astrometry', 'photometry', 'aen', 'gspphot', "nway", "velocity"
        ] = 'astrometry'
) -> pd.DataFrame:
    file_root = config.RESULTS_CATALOGUES_FOR_REVISION

    if option in ['astrometry', 'photometry', 'aen', 'gspphot']:
        file_path = file_root / "gaia" / f"{option}_stars_only.csv"
    elif option == "velocity":
        file_path = file_root / "velocity" / "space_velocities.csv"

    elif option == "nway":
        file_path = (
            file_root / "nway_matched_results"
            / "xray_catalogue_concatenated_further_cleaned.csv"
        )
    else:
        raise ValueError(f"Unknown option: {option}")

    df = pd.read_csv(file_path)
    logger.info(f"Loaded {option} catalogue: {df.shape[0]} rows")

    if option == 'velocity':
        df = df.drop(
            columns=["r_med_photogeo", "r_lo_photogeo", "r_hi_photogeo"],
        )
    elif option == "nway":
        cols_to_keep = [
            ds.CombinedCatalogueSchema.ID_x,
            ds.CombinedCatalogueSchema.source_id,
            ds.NWAYSchema.p_any,
            ds.NWAYSchema.p_single,
            ds.NWAYSchema.match_flag,
            ds.NWAYSchema.p_i,
            "sep_x_g",
            "sep_x_g_sigma"
        ]
        df = df[cols_to_keep]

    return df


def _add_f_g_col(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    phot_g_mean_mag = df_copy['phot_g_mean_mag'].values

    fg = calculate_optical_flux(phot_g_mean_mag)

    df_copy[ds.CombinedCatalogueSchema.f_g] = fg

    logger.info(
        f"Added F_G column. Total of "
        f"{df_copy[ds.CombinedCatalogueSchema.f_g].isna().sum()} NaN values."
    )

    return df_copy


def _add_fx_fg_col(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    fx = df_copy[ds.CombinedCatalogueSchema.f_x]
    fg = df_copy[ds.CombinedCatalogueSchema.f_g]
    fx_fg_err = df_copy[ds.CombinedCatalogueSchema.f_x_err] / fg

    df_copy[ds.CombinedCatalogueSchema.fx_fg] = fx / fg
    df_copy[ds.CombinedCatalogueSchema.fx_fg_err] = fx_fg_err

    logger.info("Added FX/FG ratio and the FX/FG error columns.")

    return df_copy


def _join_gaia_dfs(
    df_left, df_right, on: str = ds.CombinedCatalogueSchema.source_id,
    left_label: str = 'left', right_label: str = 'right'
) -> pd.DataFrame:
    cols_right = [
        col for col in df_right.columns if col != 'ID_x'
    ]

    df_joined = pd.merge(
        df_left, df_right[cols_right],
        on=on, how='left'
    )
    logger.info(
        f"Joined {right_label} to {left_label} DataFrames on '{on}'."
    )

    return df_joined


def _save_to_file(df: pd.DataFrame, file_path: Path) -> None:
    df.to_csv(file_path, index=False)
    logger.info(f"Saved DataFrame to {file_path}")


def make_catalogue() -> None:
    logger.info("Loading astrometry catalogue ...")
    df_base = _load_df(option='astrometry')

    logger.info("Loading photometry catalogue ...")
    df_photometry = _load_df(option='photometry')

    logger.info("Adding F_G column to photometry catalogue ...")
    df_photometry = _add_f_g_col(df_photometry)

    logger.info("Merging astrometry and photometry catalogues ...")
    df_base = _join_gaia_dfs(
        df_left=df_base, df_right=df_photometry,
        left_label='astrometry', right_label='photometry'
    )

    logger.info("Applying parallax zero-point correction ...")
    df_base = _zp_correction(df_base)

    logger.info(
        "Generating concatenated X-ray catalogue. This catalogue will be "
        "joined to get the x-ray columns ..."
    )

    df_xray = _concatenate_catalogues()
    logger.info(f"Concatenated catalogue shape: {df_xray.shape}")

    logger.info(
        "Joining with concatenated X-ray catalogue to get the X-ray columns..."
    )

    df_base = pd.merge(
        df_base, df_xray,
        on=ds.CombinedCatalogueSchema.ID_x,
        how='left'
    )

    logger.info("Adding FX/FG ratio and the FX/FG error columns ...")
    df_base = _add_fx_fg_col(df_base)

    logger.info("Joining additional catalogues ...")
    for label in ["aen", "gspphot", "velocity", "nway"]:
        df_to_join = _load_df(option=label)

        df_base = _join_gaia_dfs(
            df_left=df_base, df_right=df_to_join,
            left_label='base', right_label=label
        )

    logger.info(f"Finished. Final catalogue shape: {df_base.shape}")

    out_file_path = (
        config.RESULTS_CATALOGUES_FOR_REVISION / "master_catalogue.csv"
    )
    _save_to_file(df_base, file_path=out_file_path)


if __name__ == "__main__":
    make_catalogue()
