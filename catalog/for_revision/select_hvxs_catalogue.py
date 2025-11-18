import pandas as pd
import config
import data_schema as ds
import logging
import numpy as np
from log.log_config import configure_logging
from pathlib import Path
from typing import Literal

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


def _filter_by_vpec_min_lim(
        df: pd.DataFrame, vpec_min_lim: float,
        vpec_min_lim_opt: Literal['lo', 'med']
) -> pd.DataFrame:
    df_copy = df.copy()

    if vpec_min_lim_opt == 'lo':
        vpec_col = (
            df_copy[ds.CombinedCatalogueSchema.vpec_min_med]
            - df_copy[ds.CombinedCatalogueSchema.e_vpec_min]
        )
    elif vpec_min_lim_opt == 'med':
        vpec_col = df_copy[ds.CombinedCatalogueSchema.vpec_min_med]

    else:
        raise ValueError(f"Unknown vpec_min_lim_opt: {vpec_min_lim_opt}")

    initial_len = df_copy.shape[0]

    df_filtered = df_copy[
        vpec_col >= vpec_min_lim
    ].reset_index(drop=True)

    final_len = df_filtered.shape[0]

    logger.info(
        f"Filtered by Vpec_min limit ({vpec_min_lim_opt}): "
        f"from {initial_len} to {final_len}."
    )

    return df_filtered


def _filter_by_fx_fg(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()
    logger.info(f"{df_copy.shape[0]} rows before FX/FG filtering.")
    fx_fg = df_copy[ds.CombinedCatalogueSchema.fx_fg]
    fx_fg_err = df_copy[ds.CombinedCatalogueSchema.fx_fg_err]
    bp_rp = df_copy[ds.CombinedCatalogueSchema.bp_rp]

    logger.info("Filtering by FX/FG ratio lower limit...")

    _filter = (
        fx_fg.notna() & fx_fg_err.notna() & bp_rp.notna()
        & (fx_fg - fx_fg_err >= np.power(10, bp_rp - 3.5))
    )

    n_rows_removed = df_copy.shape[0] - _filter.sum()
    df_filtered = df_copy[_filter].reset_index(drop=True)

    logger.info(
        f"{n_rows_removed} rows removed after FX/FG filtering, "
        f"keeping {df_filtered.shape[0]} rows."
    )

    return df_filtered


def _save_to_file(df: pd.DataFrame, file_path: Path) -> None:
    df.to_csv(file_path, index=False)
    logger.info(f"Saved DataFrame to {file_path}")


def make_catalogue(
        vpec_min_lim: float, vpec_min_lim_opt: Literal['lo', 'med']
) -> pd.DataFrame:
    df = _load_master_catalogue()
    df = _filter_by_vpec_min_lim(
        df, vpec_min_lim=vpec_min_lim,
        vpec_min_lim_opt=vpec_min_lim_opt
    )
    df = _filter_by_fx_fg(df)

    output_path = (
        config.RESULTS_CATALOGUES_FOR_REVISION / "hvxs" / "hvxs.csv"
    )
    _save_to_file(df, output_path)

    return df


if __name__ == "__main__":
    make_catalogue(vpec_min_lim=200, vpec_min_lim_opt='lo')
