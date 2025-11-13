import config
import pandas as pd
from pathlib import Path
from log.log_config import configure_logging
from typing import Dict
import logging

configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


catalogue_path_dict = {
    "confident_point_sources": (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "x_ray_catalogue_deduplication"
        / "xray_catalogue_all_for_autocorrelation.csv"
    ),

    "deduplicated_xray_catalogue": (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "x_ray_catalogue_deduplication"
        / "xray_catalogue_deduplicated.csv"
    ),

    "nway_matched": (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "nway_matched_results"
        / "xray_catalogue_concatenated.csv"
    ),

    "nway_matched_deduplicated": (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "nway_matched_results"
        / "xray_catalogue_concatenated_deduplicated.csv"
    ),

    "nway_matched_further_cleaned": (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "nway_matched_results"
        / "xray_catalogue_concatenated_further_cleaned.csv"
    ),

    "kinematic_worthy": (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "gaia"
        / "astrometry_stars_only.csv"
    ),

    "hvxs_raw": (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "hvxs" / "hvxs.csv"
    ),

    "hvxs_final": (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "ready_catalogues" / "hvxs.csv"
    )
}


def _count_rows_by_survey(
        df: pd.DataFrame, step_label: str,
) -> Dict[str, int]:
    n_total = df.shape[0]
    logger.info(
        f"Begin to count number of rows for each survey for {step_label}."
        f"Total row number: {n_total}"
    )

    count_dict = {}
    for identifier, survey_name in config.SURVEY_ID_IDENTIFIERS.items():
        _filter = df["ID_x"].str.startswith(identifier)
        count_dict[survey_name] = _filter.sum()

    return count_dict


def count_each_step() -> None:
    df_summary = pd.DataFrame(
        columns=list(config.SURVEY_ID_IDENTIFIERS.values()),
        index=list(catalogue_path_dict.keys())
    )

    for step_label, file_path in catalogue_path_dict.items():
        logger.info(
            f"Loading catalogue for step '{step_label}' ..."
        )
        df = pd.read_csv(file_path)
        count_dict = _count_rows_by_survey(df, step_label)
        df_summary.loc[step_label] = pd.Series(count_dict)

    df_summary["total"] = df_summary.sum(axis=1)

    df_summary.to_csv(
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "ready_catalogues"
        / "source_number_counts_by_survey_each_step.csv",
        index=True
    )


if __name__ == "__main__":
    count_each_step()
