import pandas as pd
import config
import logging
import numpy as np
import time
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


def check_overlap(df: pd.DataFrame) -> None:
    logger.info(f"Input DataFrame has {df.shape[0]} rows")
    n_tot = df.shape[0]

    df_sep = pd.DataFrame(
        columns=["id_x_1", "id_x_2", "sep", "pos_x_err_1", "pos_x_err_2"]
    )

    logger.info("Checking for overlapping sources...")
    for i in range(n_tot):
        for j in range(i + 1, n_tot):
            ra_x1 = df.loc[i, "ra_x"]
            dec_x1 = df.loc[i, "dec_x"]
            ra_x2 = df.loc[j, "ra_x"]
            dec_x2 = df.loc[j, "dec_x"]
            pos_x_err_1 = df.loc[i, "pos_x_err"]
            pos_x_err_2 = df.loc[j, "pos_x_err"]
            id_x_1 = df.loc[i, "ID_x"]
            id_x_2 = df.loc[j, "ID_x"]
            sep = np.sqrt(
                (ra_x1 - ra_x2) ** 2 +
                (dec_x1 - dec_x2) ** 2
            )

            err_sum = df.loc[i, "pos_x_err"] + df.loc[j, "pos_x_err"]
            if sep < err_sum:
                row = pd.Series(
                    {
                        "id_x_1": id_x_1,
                        "id_x_2": id_x_2,
                        "sep": sep,
                        "pos_x_err_1": pos_x_err_1,
                        "pos_x_err_2": pos_x_err_2
                    }
                )

                df_sep = pd.concat(
                    [df_sep, row.to_frame().T], ignore_index=True
                )

    n_overlap = df_sep.shape[0]
    print(df_sep)
    logger.info(
        f"Found {n_overlap} overlapping sources.",
    )


if __name__ == "__main__":
    logger = logging.getLogger(Path(__file__).stem)
    configure_logging(level=logging.INFO, app_name=Path(__file__).stem)

    df_all = _concatenate_catalogues()

    start_time = time.perf_counter()
    df_test = df_all.sample(n=1000, random_state=42).reset_index(drop=True)
    check_overlap(df_test)
    elapsed = time.perf_counter() - start_time

    expected_hours = (elapsed / df_test.shape[0]) * df_all.shape[0] / 3600
    logger.info(
        f"Checking on {df_test.shape[0]} rows completed in {elapsed:.2f} "
        f"seconds. For the full catalogue with {df_all.shape[0]} rows, "
        f"it may take up to {expected_hours:.2f} hours."
    )
