import pandas as pd
import logging
import config
import data_schema as ds
from log.log_config import configure_logging
from pathlib import Path
from typing import Tuple


logger = logging.getLogger(Path(__file__).stem)
configure_logging(level=logging.INFO, app_name=Path(__file__).stem)


def _load_catalogue() -> pd.DataFrame:
    file_path = (
        config.RESULTS_CATALOGUE_DIR
        / "nway_matched_results"
        / "xray_catalogue_concatenated.csv"
    )
    df = pd.read_csv(file_path)
    logger.info(
        f"Loading concatenated NWAY-matched X-ray catalogue ...\n"
        f"{df.shape[0]} sources loaded."
    )

    return df


def deduplicate_concatenated_nway_matches(
        df: pd.DataFrame
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Remove Gaia sources that have multiple X-ray matches, keeping only the
    nearest match. N.B. None of the X-ray sources have multi

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame containing the matches to deduplicate.

    Returns
    -------
    TUPLE[pd.DataFrame, pd.DataFrame]
        - Deduplicated DataFrame.
        - DataFrame containing the dropped duplicates.
    """

    df_copy = df.copy()

    df_copy[ds.CombinedCatalogueSchema.sep_x_g_sigma] = df_copy.eval(
        "sep_x_g / pos_x_err"
    )
    df_copy = df_copy.sort_values(
        by=ds.CombinedCatalogueSchema.sep_x_g_sigma, ascending=True
    )

    df_dropped = df_copy[
        df_copy.duplicated(
            subset=ds.CombinedCatalogueSchema.source_id, keep="first"
        )
    ].reset_index(drop=True)

    df_cleaned = df_copy.drop_duplicates(
        subset=ds.CombinedCatalogueSchema.source_id,
        keep="first"
    ).reset_index(drop=True)

    logger.info(f"{df_cleaned.shape[0]} total matches after deduplication.")
    logger.info(
        f"Removed {df_dropped.shape[0]} duplicated matches "
        f"based on the {ds.CombinedCatalogueSchema.source_id} column."
    )

    return df_cleaned, df_dropped


def _save_to_files(out_root: Path) -> None:
    out_root.mkdir(parents=True, exist_ok=True)

    output_file_deduplicated = (
        out_root / "xray_catalogue_concatenated_deduplicated.csv"
    )
    output_file_dropped = (
        out_root / "dropped_duplicated_matches.csv"
    )
    df_deduplicated.to_csv(output_file_deduplicated, index=False)
    df_dropped.to_csv(output_file_dropped, index=False)

    logger.info(
        "Saved deduplicated NWAY-matched X-ray catalogue to "
        f"{output_file_deduplicated}."
    )

    logger.info(
        f"Saved dropped duplicated matches to {output_file_dropped}."
    )


if __name__ == "__main__":
    df = _load_catalogue()

    df_deduplicated, df_dropped = deduplicate_concatenated_nway_matches(df)

    output_dir = (
        config.RESULTS_CATALOGUE_DIR / "nway_matched_results"
    )

    _save_to_files(out_root=output_dir)
