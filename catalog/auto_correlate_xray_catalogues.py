import pandas as pd
import config
import logging
from log.log_config import configure_logging
from pathlib import Path


def _concatenate_catalogues() -> pd.DataFrame:
    """Concatenate multiple X-ray catalogues into a single DataFrame.
    This DataFrame will then be used for auto-correlation to identify
    duplicate sources across different catalogues.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the concatenated X-ray catalogues.
    """
    col_remapping_dict = {
        "csc": {
            "name": "ID_x", "ra_deg": "ra_x", "dec_deg": "dec_x",
        },
        "xmm": {
            "iauname": "ID_x", "sc_ra": "ra_x", "sc_dec": "dec_x",
        },
        "swift": {
            "IAUName": "ID_x", "RA": "ra_x", "Decl": "dec_x",
        },
        "erass": {
            "IAUNAME": "ID_x", "RA": "ra_x", "DEC": "dec_x"
        }
    }

    cols_to_keep = ["ID_x", "ra_x", "dec_x", "pos_x_err"]
    for survey in config.SURVEY_NAMES_SHORT:
        file_path = (
            config.ROOT_DIR / "results" / survey
            / "catalogues" / "nway_match" /
            f"{survey}_confident_point_sources_poserr_rescaled.csv"
        )
        df = pd.read_csv(file_path)
        logger.info(
            f"Confident point sources for {survey.upper()} loaded "
            f"from {file_path}, "
            f"including {df.shape[0]} rows"
        )

        logger.info(
            f"Renaming columns for {survey.upper()} ..."
            f"Mapping: {col_remapping_dict[survey]}"
        )
        df = df.rename(
            columns=col_remapping_dict[survey]
        )
        n_duplicates = df["ID_x"].duplicated().sum()
        if n_duplicates > 0:
            logger.warning(
                f"{n_duplicates} Duplicate IDs found in {survey.upper()} "
                "catalogue! This should not happen if the catalogue is raw. "
                "Please check."
            )

        logger.info(
            f"Concatenating {survey.upper()} catalogue into a master list..."
        )
        if survey == config.SURVEY_NAMES_SHORT[0]:
            df_all = df[cols_to_keep]
        else:
            df_all = pd.concat([df_all, df[cols_to_keep]], ignore_index=True)

    logger.info(
        f"All catalogues concatenated, total rows: {df_all.shape[0]}"
    )
    return df_all


if __name__ == "__main__":
    logger = logging.getLogger(Path(__file__).stem)
    configure_logging(level=logging.INFO, app_name=Path(__file__).stem)

    _ = _concatenate_catalogues()
