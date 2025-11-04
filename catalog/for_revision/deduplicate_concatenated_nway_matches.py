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
        f"Saved dropped duplicated pairs to {output_file_dropped}."
    )


def _sanity_check(
        df: pd.DataFrame, df_cleaned: pd.DataFrame, df_dropped: pd.DataFrame
) -> None:
    # Get all duplicated source IDs
    dup_source_ids = df[
        df.duplicated(subset=ds.CombinedCatalogueSchema.source_id, keep=False)
    ][ds.CombinedCatalogueSchema.source_id]

    # Count occurrences of each duplicated source ID
    dup_counts = dup_source_ids.value_counts()
    tot_duplicates = dup_counts.sum()
    tot_duplicates_via_keep_false = dup_source_ids.shape[0]

    # Number of unique duplicated source IDs
    n_unique = df[
        df.duplicated(subset=ds.CombinedCatalogueSchema.source_id, keep=False)
    ][ds.CombinedCatalogueSchema.source_id].nunique()

    n_unique_via_dropped = tot_duplicates - df_dropped.shape[0]

    if tot_duplicates != tot_duplicates_via_keep_false:
        logger.warning(
            f"Sanity check failed: The total of duplicates via tallying "
            f"({tot_duplicates}) does not match the total via keep=False "
            f"({tot_duplicates_via_keep_false})."
        )
    else:
        logger.info(
            f"Sanity check passed: The total of duplicates via tallying "
            f"({tot_duplicates}) matches the total via keep=False "
            f"({tot_duplicates_via_keep_false})."
        )

    if n_unique != n_unique_via_dropped:
        logger.warning(
            f"Sanity check failed: The number of unique duplicated source IDs "
            f"({n_unique}) obtained from .nunique() on the original DataFrame "
            "does not match the expected number obtained by taking off "
            f"the number of dropped rows from the original total: "
            f"({n_unique_via_dropped})."
        )
    else:
        logger.info(
            f"Sanity check passed: The number of unique duplicated source IDs "
            f"({n_unique}) obtained from .nunique() on the original DataFrame "
            f"matches the expected number obtained by taking off "
            f"the number of dropped rows from the original total: "
            f"({n_unique_via_dropped})."
        )


if __name__ == "__main__":
    df = _load_catalogue()

    df_deduplicated, df_dropped = deduplicate_concatenated_nway_matches(df)

    output_dir = (
        config.RESULTS_CATALOGUE_DIR / "nway_matched_results"
    )

    _save_to_files(out_root=output_dir)
    _sanity_check(
        df=df,
        df_cleaned=df_deduplicated,
        df_dropped=df_dropped
    )
