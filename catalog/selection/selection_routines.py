import numpy as np
import pandas as pd
import config
from pathlib import Path
from log.loggers import VerboseLogger


def select_high_fx_fg_ratio_sources(
        in_file_csv: Path, out_file: bool = False, verbose: bool = False
) -> None:

    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    df = pd.read_csv(in_file_csv)
    logger.log(f"{df.shape[0]} rows loaded.\n")

    # Applying the Rodriguez+24 empirical relation
    _filter = (
        df["fx_fg"] - df["fx_fg_err"] >= np.power(10, df["bp_rp"] - 3.5)
    )
    df_filtered = df[_filter]

    logger.log(f"{df_filtered.shape[0]} sources selected.  \n")

    if out_file:
        logger.log("Saving the filtered catalogue ...")
        out_file = (
            in_file_csv.parent
            / f"{in_file_csv.stem.replace('stage_1', 'stage_2')}.csv"
        )
        df_filtered.to_csv(out_file, index=False)
        logger.log(f"Catalogue saved to {out_file}.\n")

    logger.end()


def select_prime_sample(in_file: Path, verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    df = pd.read_csv(in_file)

    # _vpec_filter = df["vpec_min_med"] - df["e_vpec_min"] >= 500
    _sep_filter = df["sep_x_g"] / df["pos_x_err"] <= 1.0
    _parallax_filter = df["parallax_corr"] / df["parallax_error"] >= 5

    df_prime = df[_sep_filter & _parallax_filter]
    # df_prime = df_prime.sort_values(by=["from", "ra_x"], ascending=True)
    df_prime["fom"] = (
        np.log(df_prime["vpec_min_med"] - df_prime["e_vpec_min"])
        + np.log(df_prime["fx_fg"])
        + np.log(df_prime["parallax"] / df_prime["parallax_error"])
    )

    df_prime = df_prime.sort_values(by="fom", ascending=False)
    logger.log(f"{df_prime.shape[0]} prime sources selected.")

    out_file = in_file.parent / f"{in_file.stem}_prime.csv"
    df_prime.to_csv(out_file, index=False)
    logger.log(f"Selected sources saved to {out_file}.\n")
    logger.end()


def select_control_sample(in_file: Path, verbose: bool = False) -> None:
    """
    Used to build a control sample to the selected HVXS sample.

    Parameters
    ----------
    in_file : pathlib.Path
        The path to the input catalogue file. This catalogue is supposed to be
        the selected HVXS sample.

    verbose : bool
        Controls if extra information is printed out.

    Returns
    -------
    """

    logger = VerboseLogger(verbose=verbose)
    logger.begin()

    df = pd.read_csv(in_file)

    logger.log(f"{df.shape[0]} sources loaded.\n")

    df_all = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "control_sample"
        / "control_sample_stage_9.csv"
    )

    logger.log(f"The loaded parent sample has {df_all.shape[0]} sources.\n")

    in_hvxs = df_all["source_id"].isin(df["source_id"])
    df_control = df_all[~in_hvxs]

    logger.log(
        f"Identified {in_hvxs.sum()} HVXSs in the parent sample. "
        "Removing these sources ...\n"
    )
    logger.log(
        f"The updated control sample has {df_control.shape[0]} sources.\n"
    )

    df_control.to_csv(
        config.RESULTS_CATALOGUE_DIR
        / "control_sample"
        / "control_sample_stage_10.csv", index=False
    )


def select_prime_sample_by_fom(
        in_file: Path, top: int = 30, verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    df = pd.read_csv(in_file)
    logger.log(f"{df.shape[0]} sources loaded.\n")

    sep_x_g = df["sep_x_g"] / df["pos_x_err"]
    _filter = (sep_x_g <= 1) & (df.dist_med <= 10) & (df.parallax_corr > 0)
    df = df[_filter]

    vpec_min_lo = df["vpec_min_med"] - df["e_vpec_min"]
    fx_fg_lo = df["fx_fg"] - df["fx_fg_err"]
    aen_sig = df["astrometric_excess_noise_sig"]
    parallax_snr = df["parallax_corr"] / df["parallax_error"]
    # g_flux_snr = df["phot_g_mean_flux_over_error"]

    df["astrometric_excess_noise_sig"].fillna(1e-2, inplace=True)
    # Figure of merit
    logger.log("Adding a Figure of Merit (fom) column to the DataFrame ...\n")
    # df["fom"] = (vpec_min_lo ** 1.5 * parallax_snr) / (dist * sep_x_g)
    df["fom"] = (
        1.2 * np.log10(parallax_snr)
        + 1.0 * np.log10(aen_sig)
        + 1.0 * np.log10(fx_fg_lo)
        + 1.0 * np.log10(vpec_min_lo)
    )

    df = df.sort_values(by="fom", ascending=False)

    logger.log(f"Top {top} sources specified, and {df.shape[0]} sources "
               "selected\n")
    df_prime = df.head(top)
    out_file = (
        config.RESULTS_CATALOGUE_DIR
        / "prime_catalogs" / f"{in_file.stem}_prime_by_fom.csv"
    )
    df_prime.to_csv(out_file, index=False)
    logger.log(f"Prime catalogue saved to {out_file}.\n")
    logger.end()


def main() -> None:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources"
        / "hvxs_vpec_lo_gt_200.csv"
    )
    # select_high_fx_fg_ratio_sources(
    #     in_file_csv=in_file, out_file=True, verbose=True
    # )
    select_prime_sample(in_file, verbose=True)
    # select_prime_sample_by_fom(in_file, verbose=True, top=212)
    # select_control_sample(in_file, verbose=True)


if __name__ == "__main__":
    main()
