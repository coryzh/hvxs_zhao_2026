import pandas as pd
import config
import logging
from typing import Dict
from log.log_config import configure_logging
from pathlib import Path
from astropy.io import fits
from astropy.table import Table

logger = logging.getLogger(Path(__file__).stem)
configure_logging(level=logging.INFO, app_name=Path(__file__).stem)


def load_catalogue(in_file: Path) -> pd.DataFrame:
    hdul = fits.open(in_file)
    tab = Table(hdul[1].data)
    df = tab.to_pandas()
    return df


def save_to_file(split_dfs: Dict[str, pd.DataFrame], out_dir: Path) -> None:
    for survey_name, df in split_dfs.items():
        out_file = out_dir / f"{survey_name}_gaia_neighbours.csv"
        split_dfs[survey_name].to_csv(
            out_file, index=False
        )

        logger.info(
            f"Saved the Gaia neighbours for {survey_name} to {out_file}."
        )


def split_catalogue(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Split the concatenated X-ray/Gaia catalogue into separate
    DataFrames based on survey identifiers.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the concatenated catalogue.
    """

    # Split the DataFrame into separate DataFrames based on survey identifiers
    split_dfs = {}
    survey_identifiers = config.SURVEY_ID_IDENTIFIERS

    kept_columns = ["source_id", "ra", "dec"]
    for identifier, survey_name in survey_identifiers.items():
        logger.info(f"Processing {survey_name} ...")
        mask = (
            df['ID_x'].dropna().astype(str)
            .str.strip()
            .str.startswith(identifier)
        )
        split_df = df[mask].copy()
        split_dfs[survey_name] = split_df[kept_columns]
        logger.info(
            f"'{survey_name}' has {len(split_df)} Gaia neighbours."
        )

    return split_dfs


if __name__ == "__main__":
    in_file = (
        config.RESULTS_CATALOGUES_FOR_REVISION / "x_ray_catalogue_for_nway"
        / "gaia_neighbours_20arcsec.fits"
    )

    df = load_catalogue(in_file)
    split_dfs = split_catalogue(df)
    save_to_file(
        split_dfs, out_dir=in_file.parent
    )
