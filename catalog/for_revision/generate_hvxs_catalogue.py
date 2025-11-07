import pandas as pd
import config
import data_schema as ds
import logging
from log.log_config import configure_logging
from catalog.for_revision.auto_correlate_xray_catalogues import (
    _concatenate_catalogues
)
from pathlib import Path

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

    df_xray = df[xray_columns].copy()

    return df_xray


def test() -> None:
    df_master = _concatenate_catalogues()
    logger.info(f"Concatenated catalogue shape: {df_master.shape}")


if __name__ == "__main__":
    test()
