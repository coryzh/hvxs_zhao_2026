# import config
import pandas as pd

import config
from log.loggers import VerboseLogger
from pathlib import Path


def clean_for_fxfg_vs_bprp(df: pd.DataFrame, verbose: bool = False, out_file: Path = None) -> pd.DataFrame:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    logger.log(f"Loading catalogue ...")
    logger.log(f"{df.shape[0]} rows loaded.\n")

    logger.log(f"Dropping rows that have NA X-ray fluxes or NA X-ray/optical ratios.")
    df_cleaned = df.dropna(subset=["f_x", "f_x_err", "fx_fg"])
    logger.log(f"{df.shape[0] - df_cleaned.shape[0]} rows dropped.\n")

    logger.log(f"Dropping rows that have 0 X-ray fluxes ...")
    _filter_zero_flux = (df["f_x"] > 0) & (df["f_x_err"] > 0)
    n_rows = df_cleaned.shape[0]
    df_cleaned = df_cleaned[_filter_zero_flux]
    logger.log(f"{n_rows - df_cleaned.shape[0]} rows dropped.\n")

    logger.log(f"Dropping rows that have unavailable Gaia BP and RP magnitudes ...")
    n_rows = df_cleaned.shape[0]
    df_cleaned = df_cleaned.dropna(subset=["phot_bp_mean_mag", "phot_rp_mean_mag"])
    logger.log(f"{n_rows - df_cleaned.shape[0]} rows dropped.\n")

    if not out_file:
        logger.log(f"Saving the cleaned catalog to {out_file}....")
        df_cleaned.to_csv(out_file, index=False)
        logger.log(f"Catalog saved to {out_file}.")

    return df_cleaned


def main() -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_lolim_gt_200.0_unique.csv")
    df_cleaned = clean_for_fxfg_vs_bprp(df, verbose=True)


if __name__ == "__main__":
    main()
