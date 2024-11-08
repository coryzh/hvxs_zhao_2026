import numpy as np
import pandas as pd
import config
from pathlib import Path
from log.loggers import VerboseLogger


def select_high_fx_fg_ratio_sources(in_file_csv: Path, out_file: bool = False, verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    df = pd.read_csv(in_file_csv)
    logger.log(f"{df.shape[0]} rows loaded.\n")

    _filter = (df["fx_fg"] - df["fx_fg_err"] >= np.power(10, df["bp_rp"] - 3.5))
    df_filtered = df[_filter]

    logger.log(f"{df_filtered.shape[0]} sources selected.  \n")

    if out_file:
        logger.log(f"Saving the filtered catalogue ...")
        out_file = in_file_csv.parent / f"{in_file_csv.stem.replace('stage_1', 'stage_2')}.csv"
        df_filtered.to_csv(out_file, index=False)
        logger.log(f"Catalogue saved to {out_file}.\n")

    logger.end()


def select_prime_sample(in_file: Path, verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    df = pd.read_csv(in_file)

    _vpec_filter = df["vpec_min_med"] >= 1000
    _sep_filter = df["sep_x_g"] / df["pos_x_err"] <= 1.0

    df_prime = df[_vpec_filter & _sep_filter]
    df_prime = df_prime.sort_values(by=["from", "ra"], ascending=True)
    logger.log(f"{df_prime.shape[0]} prime sources selected.")

    out_file = in_file.parent / f"{in_file.stem}_prime.csv"
    df_prime.to_csv(out_file, index=False)
    logger.log(f"Selected sources saved to {out_file}.\n")
    logger.end()


def main() -> None:
    in_file = (config.RESULTS_CATALOGUE_DIR / "high-v_sources"
               / "combined_vpec_lolim_gt_150_unique_stage_6.csv")
    # select_high_fx_fg_ratio_sources(in_file_csv=in_file, out_file=True, verbose=True)
    select_prime_sample(in_file, verbose=True)


if __name__ == "__main__":
    main()
