import pandas as pd
import config
import data_schema as ds
import logging
from log.log_config import configure_logging
from pathlib import Path


configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


def _load_master_catalogue() -> pd.DataFrame:
    file_path = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "master_catalogue.csv"
    )
    df = pd.read_csv(file_path)
    logger.info(f"Master catalogue loaded: {df.shape[0]} rows.")
    return df


def _load_hvxs_catalogue() -> pd.DataFrame:
    file_path = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / 'hvxs' / "hvxs.csv"
    )
    df = pd.read_csv(file_path)
    logger.info(f"HVXS catalogue loaded: {df.shape[0]} rows.")
    return df


def _select_complement(
        df_master: pd.DataFrame, df_hvxs: pd.DataFrame
) -> pd.DataFrame:
    logger.info(
        "Selecting complement of HVXS catalogue in master catalogue."
    )

    hvxs_source_ids = df_hvxs[ds.CombinedCatalogueSchema.source_id]
    _filter = ~df_master[ds.CombinedCatalogueSchema.source_id].isin(
        hvxs_source_ids
    )
    df_complement = df_master[_filter].reset_index(drop=True)
    logger.info(
        f"Complement selection complete: {df_complement.shape[0]} rows."
    )

    return df_complement


def _save_to_file(
        df: pd.DataFrame
) -> None:
    out_file = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "control" / "control.csv"
    )

    out_file.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_file, index=False)
    logger.info(f"DataFrame saved to file: {out_file}")


def entry_point() -> None:
    df_master = _load_master_catalogue()
    df_hvxs = _load_hvxs_catalogue()
    df_control = _select_complement(df_master, df_hvxs)
    _save_to_file(df_control)


if __name__ == "__main__":
    entry_point()
