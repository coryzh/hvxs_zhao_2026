import logging
import pandas as pd
import config
from pathlib import Path
from log.log_config import configure_logging

configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


def _load_fidelity_catalogue() -> pd.DataFrame:
    in_file = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "rybizki_fidelity"
        / "fidelity_all.csv"
    )
    df = pd.read_csv(in_file)
    logger.info(f"Rybizki fidelity catalogue loaded: {df.shape[0]} rows.\n")
    return df


def _merge_fidelity_to_main_df(
        df: pd.DataFrame, df_fidelity: pd.DataFrame
) -> pd.DataFrame:
    logger.info("Merging fidelity catalogue to main dataframe ...")

    df_merged = pd.merge(
        df, df_fidelity, on="source_id", how="left"
    )

    logger.info(f"Merged dataframe shape: {df_merged.shape}")
    return df_merged


def _clean_df_simbad_type(
        df: pd.DataFrame, fidelity_thresh: float = 0.5
) -> pd.DataFrame:
    _filter = df["fidelity_v2"] >= fidelity_thresh

    df_filtered = df[_filter]
    logger.info(
        f"{df.shape[0] - df_filtered.shape[0]} rows removed based on fidelity "
        f"threshold {fidelity_thresh}."
    )

    return df_filtered


def _cleanup(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["fidelity_v2"])
    logger.info(
        "Clean-up: fidelity columns ('fidelity_v2') have been"
        " dropped."
    )

    return df


def clean(df: pd.DataFrame, out_file: Path = None) -> pd.DataFrame:
    df_fidelity = _load_fidelity_catalogue()
    df = _merge_fidelity_to_main_df(df, df_fidelity)
    df = _clean_df_simbad_type(df, fidelity_thresh=0.5)
    df = _cleanup(df)

    if out_file:
        df.to_csv(out_file, index=False)
        logger.info(f"Cleaned dataframe saved to {out_file}.")

    return df
