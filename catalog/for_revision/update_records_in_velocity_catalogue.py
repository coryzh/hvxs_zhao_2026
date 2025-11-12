import pandas as pd
import config
import logging
from log.log_config import configure_logging
from pathlib import Path
from typing import Dict
import argparse

configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


def _load_catalogues() -> Dict[str, pd.DataFrame]:
    old_path = (
        config.RESULTS_CATALOGUE_DIR / "ready_catalogues" / "hvxs.csv"
    )

    new_path = (
        config.RESULTS_CATALOGUES_FOR_REVISION / "velocity"
        / "space_velocities.csv"
    )

    return {
        "old": pd.read_csv(old_path),
        "new": pd.read_csv(new_path)
    }


def _get_comparision(
        source_id: int
) -> Dict[str, pd.Series]:
    logger.info(f"Locating source ID {source_id} in catalogues.")

    df_dict = _load_catalogues()

    records = {}
    cols_of_interest = [
        "vpec_min_med", "e_vpec_min", "E_vpec_min",
        "vpec_gamma_min_med", "e_vpec_gamma_min", "E_vpec_gamma_min",
    ]

    for key, df in df_dict.items():
        print(f"Searching in '{key}' catalogue ...")
        record = df[df.source_id == source_id]
        if record.empty:
            logger.warning(
                f"Source ID {source_id} not found in '{key}' catalogue."
            )
        else:
            records[key] = record.iloc[0]

    # Create DataFrame from records with dictionary keys as index
    df_comparison = pd.DataFrame.from_dict(records, orient='index')

    # Filter to only columns of interest if they exist in the data
    available_cols = [
        col for col in cols_of_interest if col in df_comparison.columns
    ]
    if available_cols:
        df_comparison = df_comparison[available_cols]

    return df_comparison


def check(source_id: int) -> None:
    print(f"Checking records for source_id: {source_id}")
    df = _get_comparision(source_id)

    print(df)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check and compare records for a given source_id "
                    "between old and new HVXS catalogues."
    )
    parser.add_argument(
        "source_id",
        type=int,
        help="The source_id to check in the catalogues."
    )

    args = parser.parse_args()
    check(args.source_id)
