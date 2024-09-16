import pandas as pd
import config
from log.loggers import VerboseLogger


def select_targets(verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()

    logger.log(f"Loading the catalogue ...")
    in_file = config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_lolim_gt_150.0.csv"
    df = pd.read_csv(in_file)
    logger.log(f"Catalogue loaded; the input catalogue contains {df.shape[0]} entries.")

    _filter_gmag = df["phot_g_mean_mag"] <= 16
    _filter_fxfg = (df["fx_fg"] - df["fx_fg_err"] >= 10 ** (df["bp_rp"] - 3.5))
    _filter_combined = _filter_gmag & _filter_fxfg

    df_filtered = df[_filter_combined]
    out_file = in_file.parent / "vlt_p115" / "vlt_p115_targets.csv"
    df_filtered.to_csv(out_file, index=False)

    logger.log(f"{df_filtered.shape[0]} sources selected.")
    logger.log(f"Target catalogue saved to {out_file}.\n")
    logger.end()


if __name__ == "__main__":
    select_targets(verbose=True)
