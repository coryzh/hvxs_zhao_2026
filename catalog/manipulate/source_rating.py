import numpy as np

import config
import pandas as pd
from log.loggers import VerboseLogger
from pathlib import Path


def weighted_rating(in_file: Path, verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)

    df = pd.read_csv(in_file)
    logger.begin()
    logger.log(f"{df.shape[0]} rows loaded.\n")

    # Adding the lower limit columns
    logger.log("Adding the lower limit columns ... \n")
    df["vpec_lolim"] = df["vpec_min_med"] - df["e_vpec_min"]
    df["fx_fg_lolim"] = df["fx_fg"] - df["fx_fg_err"]

    # Min-max normalisation
    cols_of_interest = [
        "vpec_lolim", "fx_fg_lolim", "mh_gspphot", "astrometric_excess_noise"
    ]
    logger.log(f"Normalising {cols_of_interest} ...")
    df_temp = pd.DataFrame()
    df_temp["ID_x"] = df["ID_x"]

    for cols in cols_of_interest:
        min_val = df[cols].min()
        max_val = df[cols].max()
        df_temp[f"{cols}_normalised"] = (
            (df[cols] - min_val)
            / (max_val - min_val)
        )

    # missing_weight = 0.3
    weights = {
        "vpec_lolim_normalised": 1.5,
        "fx_fg_lolim_normalised": 1.0,
        "astrometric_excess_noise_normalised": 0.5,
        "mh_gspphot_normalised": 0.5
    }

    df_temp["mh_gspphot_normalised"].fillna(0, inplace=True)

    score = pd.Series(np.zeros(df_temp.shape[0]))

    for key, val in weights.items():
        print(df_temp[key])
        score += df_temp[key] * val

    df_temp["weighted_score"] = score
    df_out = pd.merge(
        df, df_temp[["ID_x", "weighted_score"]], on="ID_x", how="left"
    )
    df_out.sort_values(by="weighted_score", ascending=False, inplace=True)

    out_file = in_file.parent / f"{in_file.stem}_ranked.csv"
    df_out.to_csv(out_file)


def main() -> None:
    in_file = (config.RESULTS_CATALOGUE_DIR
               / "high-v_sources"
               / "combined_vpec_lolim_gt_150_unique_stage_6.csv")

    weighted_rating(in_file, verbose=True)


if __name__ == "__main__":
    main()
