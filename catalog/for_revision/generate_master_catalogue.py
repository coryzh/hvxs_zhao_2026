import logging
import pandas as pd
import config
import data_schema as ds
from utils.calc_flux import calculate_optical_flux
from log.log_config import configure_logging
from pathlib import Path
from typing import Literal

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
    logger.info("Applying zero-point correction to photometry...")

    phot_g_mean_mag = df_copy['phot_g_mean_mag']
    bp_rp = df_copy['bp_rp']

    zp_correction = 0.026 * (bp_rp - 0.4) ** 2 - 0.004
    phot_g_mean_mag_corrected = phot_g_mean_mag - zp_correction

    df_copy['phot_g_mean_mag'] = phot_g_mean_mag_corrected

    logger.info("Zero-point correction applied.")

    return df_copy


def _load_df(
        option: Literal[
            'astrometry', 'photometry', 'aen', 'gspphot', "nway"
        ] = 'astrometry'
) -> pd.DataFrame:
    file_root = config.RESULTS_CATALOGUES_FOR_REVISION

    if option in ['astrometry', 'photometry', 'aen', 'gspphot']:
        file_path = file_root / "gaia" / f"{option}_stars_only.csv"
    elif option == "nway":
        file_path = (
            file_root / "nway_matched_results"
            / "xray_catalogue_concatenated_deduplicated.csv"
        )
    else:
        raise ValueError(f"Unknown option: {option}")

    df = pd.read_csv(file_path)
    logger.info(f"Loaded {option} catalogue: {df.shape[0]} rows")
    return df


def _add_f_g_col(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    phot_g_mean_mag = df_copy['phot_g_mean_mag']

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
