import config
import pandas as pd
from pathlib import Path
from astropy.io import fits
from astropy.table import Table
import logging
from log.log_config import configure_logging

configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


def _rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    col_mapping = {
            "GaiaDR3": "source_id", "Name": "cluster_name",
            "Prob": "cl_member_prob"
    }

    df = df.rename(
        columns=col_mapping, inplace=True
    )

    logger.info(
        f"Columns renamed for cluster catalogue. Using mapping"
        f" {col_mapping}.\n"
    )
    return df


def load_cluster_catalogue() -> pd.DataFrame:
    logger.info("Loading the cluster catalogue (Hunt+23) ...")
    in_file = config.DATA_DIR_MISC / "hunt+23_members_of_clusters.fits"
    hdul = fits.open(in_file)
    data = Table(hdul[1].data)
    df = data.to_pandas()

    logger.info(
        f"Cluster catalogue loaded: {df.shape[0]} "
        "rows loaded.\n"
    )

    return df


def cross_match_ids(df: pd.DataFrame, df_members: pd.DataFrame) -> None:
    """
    Cross-matching based on Gaia DR3 source_ids.
    """
    n_duplicates = df_members.source_id.duplicated().sum()

    if n_duplicates > 0:
        logger.warning(
            f"There are {n_duplicates} duplicated IDs in the "
            "cluster members catalogue (IDs matched to multiple clusters)."
            " Dropping duplicates ... Keeping the highest probability members."
        )
        df_members = (
            df_members.sort_values(by="cl_member_prob", ascending=False)
            .drop_duplicates(subset="source_id", keep="first")
        )

    df_merged = pd.merge(
        df, df_members[["cluster_name", "source_id", "cl_member_prob"]],
        on="source_id", how="left"
    )

    n_likely_members = df_merged['cluster_name'].notna().sum()
    logger.log(
        f"{n_likely_members} sources are likely cluster members.\n"
    )

    df_merged_clean = df_merged[df_merged.cluster_name.isna()]

    return df_merged_clean


def _save_to_file(df: pd.DataFrame, file_path: Path) -> None:
    df.to_csv(file_path, index=False)

    logger.log(
        f"Catalogue with cluster membership information saved to "
        f"{file_path}."
    )

    logger.end()


def clean(df: pd.DataFrame, out_file: Path) -> pd.DataFrame:
    df_members = load_cluster_catalogue()
    df_members = _rename_columns(df_members)

    df_cleaned = cross_match_ids(df, df_members)

    if out_file is not None:
        _save_to_file(df_cleaned, out_file)

    return df_cleaned


def main() -> None:
    in_file = (config.RESULTS_CATALOGUE_DIR / "high-v_sources"
               / "combined_vpec_lolim_gt_200_unique_stage_3.csv")

    # cross_match_astrometry(in_file_csv=in_file, verbose=True,
    # radius_type="r50")
    cross_match_ids(in_file, verbose=True)


if __name__ == "__main__":
    main()
