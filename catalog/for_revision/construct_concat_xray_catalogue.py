import pandas as pd
import logging
import config
import data_schema as ds
from log.log_config import configure_logging
from pathlib import Path


logger = logging.getLogger(Path(__file__).stem)
configure_logging(level=logging.INFO, app_name=Path(__file__).stem)


def _load_catalogue(survey_name: str) -> pd.DataFrame:
    if survey_name not in config.SURVEY_NAMES_SHORT:
        raise ValueError(
            f"Survey name '{survey_name}' not recognized. "
            f"Must be one of: {config.SURVEY_NAMES_SHORT}"
        )

    file_path = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "nway_matched_results"
        / f"{survey_name}_gaia_nway_match_clean.csv"
    )
    df = pd.read_csv(file_path)
    logger.info(
        f"Loading NWAY-matched catalogue for survey '{survey_name}' ...\n"
        f"{df.shape[0]} sources loaded."
    )

    return df


def construct_concat_xray_catalogue() -> pd.DataFrame:
    df_concat = pd.DataFrame()
    essential_cols = [
        ds.CombinedCatalogueSchema.ID_x, ds.CombinedCatalogueSchema.source_id,
        ds.CombinedCatalogueSchema.ra_x, ds.CombinedCatalogueSchema.dec_x,
        ds.CombinedCatalogueSchema.ra_gaia,
        ds.CombinedCatalogueSchema.dec_gaia,
        ds.CombinedCatalogueSchema.pos_x_err,
        ds.CombinedCatalogueSchema.sep_x_g,
        ds.NWAYSchema.p_any, ds.NWAYSchema.p_single,
        ds.NWAYSchema.match_flag, ds.NWAYSchema.p_i
    ]
    summed_rows = 0
    for survey_name in config.SURVEY_NAMES_SHORT:
        df = _load_catalogue(survey_name)
        df = df[essential_cols]
        df_concat = pd.concat([df_concat, df], ignore_index=True)
        summed_rows += df.shape[0]

    if summed_rows != df_concat.shape[0]:
        logger.warning(
            "The total number of rows from individual survey catalogues "
            "does not match the number of rows in the concatenated catalogue. "
            f"Summed rows: {summed_rows}, "
            f"Concatenated rows: {df_concat.shape[0]}"
        )

    logger.info(
        "Constructed concatenated X-ray catalogue from "
        f"{len(config.SURVEY_NAMES_SHORT)} surveys, "
        f"totaling {df_concat.shape[0]} sources."
    )

    return df_concat


def save_concat_catalogue(df: pd.DataFrame, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / "xray_catalogue_concatenated.csv"

    df.to_csv(output_file, index=False)

    logger.info(
        f"Saved concatenated X-ray catalogue to {output_file}."
    )


if __name__ == "__main__":
    df_concat = construct_concat_xray_catalogue()
    save_concat_catalogue(
        df_concat,
        output_dir=config.RESULTS_CATALOGUES_FOR_REVISION
        / "nway_matched_results"
    )
