import config
import pandas as pd
import logging
import data_schema as ds
import argparse
from astropy.io import fits
from pathlib import Path
from astropy.table import Table
from log.log_config import configure_logging


logger = logging.getLogger(Path(__file__).stem)
configure_logging(level=logging.INFO, app_name=Path(__file__).stem)


def load_nway_fits_table(in_file: Path) -> pd.DataFrame:
    """Load a NWAY-prepared FITS table into a pandas DataFrame.

    Parameters
    ----------
    in_file : Path
        Path to the input FITS file.

    Returns
    -------
    pd.DataFrame
        The loaded catalogue as a pandas DataFrame.
    """
    logger.info(f"Loading NWAY-prepared FITS table from {in_file} ...")
    hdul = fits.open(in_file)
    tab = Table(hdul[1].data)
    df = tab.to_pandas()
    logger.info(
        f"Loaded {len(df)} entries from the FITS table."
    )
    return df


def _rename_columns(df: pd.DataFrame, survey_name: str) -> pd.DataFrame:
    """Rename columns to standard names for NWAY processing.

    Returns
    -------
    pd.DataFrame
        DataFrame with renamed columns.
    """

    if survey_name not in config.SURVEY_ID_IDENTIFIERS.values():
        raise ValueError(
            f"Survey name '{survey_name}' not recognized. "
            f"It must be one of {config.SURVEY_ID_IDENTIFIERS.values()}."
        )

    df_copy = df.copy()
    col_mapping = {
        f"{survey_name}_ID_x": ds.CombinedCatalogueSchema.ID_x,
        f"{survey_name}_ra_x": ds.CombinedCatalogueSchema.ra_x,
        f"{survey_name}_dec_x": ds.CombinedCatalogueSchema.dec_x,
        f"{survey_name}_pos_x_err": ds.CombinedCatalogueSchema.pos_x_err,
        f"Separation_Gaia_{survey_name}": ds.CombinedCatalogueSchema.sep_x_g,
        "Gaia_source_id": ds.CombinedCatalogueSchema.source_id,
        "Gaia_ra": ds.CombinedCatalogueSchema.ra_gaia,
        "Gaia_dec": ds.CombinedCatalogueSchema.dec_gaia,
    }
    logger.debug(
        f"Column mapping generated for {survey_name}\n: {col_mapping}"
    )
    df_copy = df_copy.rename(columns=col_mapping)

    logger.info(f"Renamed NWAY-generated columns for {survey_name}.")

    return df_copy


def clean_nway_catalogue(
        df: pd.DataFrame, p_single_lim: float = 0.90, p_any_lim: float = 0.90
) -> pd.DataFrame:
    """Clean the NWAY-matched catalogue for a specific survey.

    Parameters
    ----------
    df : pd.DataFrame
        The input NWAY-matched catalogue DataFrame.

    p_single_lim : float, optional
        The minimum threshold for 'p_single' to consider a match
        reliable, by default 0.90.

    p_any_lim : float, optional
        The minimum threshold for 'p_any' to consider a match
        reliable, by default 0.90.

    Returns
    -------
    pd.DataFrame
        The cleaned DataFrame with standardized column names.
    """
    df_copy = df.copy()
    n_row = df_copy.shape[0]
    logger.info(
        f"Cleaning the NWAY-matched catalogue ({n_row} rows) "
        f"with p_any >= {p_any_lim} and p_single >= {p_single_lim} ..."
    )
    confident_matches_filter = (
        (df_copy["p_any"] >= p_any_lim)
        & (df_copy["p_single"] >= p_single_lim)
        & (df_copy["match_flag"] == 1)  # 1 indicates confident match
    )

    logger.info(
        f"Found {confident_matches_filter.sum()} confident matches."
        f"This takes {confident_matches_filter.sum() / n_row * 100:.2f}"
        " percent of the total entries."
    )

    logger.info("Selecting necessary columns for the cleaned catalogue.")
    necessary_columns = [
        ds.CombinedCatalogueSchema.ID_x,
        ds.CombinedCatalogueSchema.ra_x,
        ds.CombinedCatalogueSchema.dec_x,
        ds.CombinedCatalogueSchema.pos_x_err,
        ds.CombinedCatalogueSchema.source_id,
        ds.CombinedCatalogueSchema.ra_gaia,
        ds.CombinedCatalogueSchema.dec_gaia,
        ds.CombinedCatalogueSchema.sep_x_g,
        ds.NWAYSchema.p_any,
        ds.NWAYSchema.p_single,
        ds.NWAYSchema.match_flag,
    ]

    df_cleaned = df_copy[confident_matches_filter][necessary_columns]
    return df_cleaned


def _save_to_file(
        df: pd.DataFrame, out_file: Path
) -> None:
    """Save the cleaned DataFrame to a CSV file.

    Parameters
    ----------
    df : pd.DataFrame
        The cleaned DataFrame to be saved.

    out_file : Path
        The output CSV file path.
    """
    df.to_csv(out_file, index=False)
    logger.info(f"Saved successfully to {out_file}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="clean_nway_catalogue",
        description=(
            "Clean the NWAY-matched catalogue by filtering "
            "based on match probabilities and renaming columns."
        )
    )

    parser.add_argument(
        "infile", help="Input NWAY-matched FITS file"
    )

    parser.add_argument(
        "survey_name", help="Name of the survey to clean the catalogue for"
    )

    parser.add_argument(
        "out_file", help="Output CSV file for the cleaned catalogue"
    )

    parser.add_argument(
        "--p_single_lim", required=False, type=float, default=0.90,
        help="Minimum p_single threshold for reliable matches"
    )

    parser.add_argument(
        "--p_any_lim", required=False, type=float, default=0.90,
        help="Minimum p_any threshold for reliable matches"
    )

    args = parser.parse_args()
    in_file_path = Path(args.infile)
    out_file_path = Path(args.out_file)

    df = load_nway_fits_table(in_file_path)

    df = _rename_columns(df, args.survey_name)
    print(f"Filtering for {args.p_single_lim=}, {args.p_any_lim=}")
    df = clean_nway_catalogue(
        df,
        p_single_lim=args.p_single_lim,
        p_any_lim=args.p_any_lim
    )

    _save_to_file(df, out_file_path)
