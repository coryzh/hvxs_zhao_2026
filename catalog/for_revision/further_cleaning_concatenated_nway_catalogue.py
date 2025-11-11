import pandas as pd
import logging
import config
from log.log_config import configure_logging
from pathlib import Path
from catalog.for_revision import (
    decrowding_concatenated_nway_catalogue,
    remove_poorly_localised_xray_sources
)

configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


def run_cleaning_pipeline() -> None:
    in_file = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "nway_matched_results"
        / "xray_catalogue_concatenated_deduplicated.csv"
    )

    df = pd.read_csv(in_file)
    logger.info(
        f"Initial catalogue loaded: {df.shape[0]} sources."
    )

    # Step 1: Remove poorly localized X-ray sources
    df = remove_poorly_localised_xray_sources.clean(
        df=df,
        pos_x_err_thresh=10.0,
        out_file=None
    )

    # Step 2: Decrowd the concatenated NWAY catalogue
    df = decrowding_concatenated_nway_catalogue.clean(
        df=df,
        radius=3.0,
        n_neighbours_thresh=1,
        out_file=None
    )

    logger.info(f"Final cleaned catalogue: {df.shape[0]} sources.")

    out_file = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "nway_matched_results"
        / "xray_catalogue_concatenated_further_cleaned.csv"
    )

    df.to_csv(out_file, index=False)
    logger.info(f"Further cleaned catalogue saved: {out_file}")


if __name__ == "__main__":
    run_cleaning_pipeline()
