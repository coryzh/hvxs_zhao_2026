import pandas as pd
import config
import logging
import data_schema as ds
from pathlib import Path
from log.log_config import configure_logging

configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


def _load_gaia_neighbours() -> pd.DataFrame:
    in_file = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "gaia_neighbours"
        / "gaia_neighbours_20arcsec.csv"
    )

    df = pd.read_csv(in_file)
    logger.info(f"{df.shape[0]} Gaia neighbours loaded.")

    return df


def _count_neighbours(
        df_neighbours: pd.DataFrame, radius: float
) -> pd.DataFrame:

    logger.info(
        f"Counting number of sources within {radius} times positional error..."
    )
    df_count = df_neighbours.query(
        f"angDist/pos_x_err<={radius}"
    ).value_counts(ds.CombinedCatalogueSchema.ID_x).reset_index(name="counts")

    # Exclude the counterpart itself
    df_count["n_neighbours"] = df_count["counts"] - 1
    df_count = df_count.drop(columns=["counts"])

    return df_count


def _merge_to_main_df(
        df: pd.DataFrame, df_count: pd.DataFrame
) -> pd.DataFrame:
    logger.info(
        f"Merging neighbour counts to main dataframe: {df.shape[0]} sources..."
    )
    df_merged = pd.merge(
        df, df_count, how="left", on=ds.CombinedCatalogueSchema.ID_x
    )

    return df_merged


def _clean_by_n_neighbours(
        df: pd.DataFrame, n_neighbours_thresh: int
) -> pd.DataFrame:
    logger.info(
        f"Removing sources with >= {n_neighbours_thresh} neighbours..."
    )

    _filter = df["n_neighbours"] < n_neighbours_thresh

    df_cleaned = df[_filter]

    logger.info(
        f"Decrowding removed {df.shape[0] - df_cleaned.shape[0]} sources. "
        f"Reduced to {df_cleaned.shape[0]} sources."
    )

    return df_cleaned


def _sanity_check_neighbour_counts(
        df_cleaned: pd.DataFrame, n_neighbours_thresh: int
) -> None:
    assert df_cleaned["n_neighbours"].max() < n_neighbours_thresh, (
        "Sanity check failed: There are still sources with "
        "neighbour counts >= 1."
    )

    logger.info(
        "Sanity check passed: All sources have neighbour counts < "
        f"{n_neighbours_thresh}."
    )


def cleanup(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["n_neighbours"])
    return df


def clean(
        df: pd.DataFrame, out_file: Path = None, radius: float = 2.,
        n_neighbours_thresh: int = 1
) -> pd.DataFrame:
    df_neighbours = _load_gaia_neighbours()

    df_count = _count_neighbours(df_neighbours, radius=radius)

    df = _merge_to_main_df(df, df_count)

    df = _clean_by_n_neighbours(
        df, n_neighbours_thresh=n_neighbours_thresh
    )
    _sanity_check_neighbour_counts(
        df, n_neighbours_thresh=n_neighbours_thresh
    )
    df = cleanup(df)

    if out_file is not None:
        df.to_csv(out_file, index=False)
        logger.info(f"Cleaned catalogue saved to {out_file}.")

    return df
