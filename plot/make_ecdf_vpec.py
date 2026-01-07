import matplotlib.pyplot as plt
import pandas as pd
import config
from utils.ecdf import plot_ecdf, get_ecdf
from log.loggers import VerboseLogger
from matplotlib.ticker import ScalarFormatter
from scipy.interpolate import interp1d
import seaborn as sns


colors = sns.color_palette("hls", 4)


def make_ecdf(verbose: bool = False, vpec_lo_lim: float = 200.0) -> None:
    source_types = {
        "as": "Active stars",
        "ab": "Active binaries",
        "yso": "YSOs",
        "cv": "CVs",
        "nicob": "NICOBs"
    }

    color_dict = {
        "as": colors[0], "ab": colors[1], "yso": colors[2],
        "cv": colors[3], "LMXB": colors[0], "PSR": colors[1],
        "HMXB": colors[2], "nicob": colors[3]
    }

    logger = VerboseLogger(verbose=verbose)

    logger.begin()

    logger.log("Plotting routine starts.\n")

    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(13, 10))

    for key, value in source_types.items():
        in_file = (
            config.RESULTS_CATALOGUE_DIR / "v_catalogs_contaminants"
            / f"{key}_vpec.csv"
        )
        df = pd.read_csv(in_file)

        logger.log(f"{df.shape[0]} {value} loaded.")

        vpec_med = df["vpec_med"].values
        # vpec_lo = vpec_med - df["e_vpec"].values
        # vpec_up = vpec_med + df["E_vpec"].values
        if key == "nicob":
            ls = '-'
        else:
            ls = '--'
        plot_ecdf(
            arr=vpec_med, ax=ax, color=color_dict[key],
            ls=ls, lw=2.0, normalised=True, label=value
        )
        x, ecdf = get_ecdf(vpec_med)
        f_ecdf = interp1d(x, ecdf, fill_value=(0, 1.0), bounds_error=False)
        logger.log(
            f"{f_ecdf(vpec_lo_lim) * 100:.2f}% of {value}"
            f" <= {vpec_lo_lim} km/s"
        )

    in_file_xrb = (
        config.RESULTS_CATALOGUE_DIR / "v_catalogs_contaminants"
        / "xrb_vpec.csv"
    )

    df_xrb = pd.read_csv(in_file_xrb)
    xrb_types = dict(LMXB="LMXBs", PSR="BPSRs", HMXB="HMXBs")
    for key, value in xrb_types.items():
        xrb_filter = df_xrb.Type.str.contains(key)
        df_xrb_sub = df_xrb[xrb_filter]
        vpec_med = df_xrb_sub["vpec_med"]
        plot_ecdf(
            vpec_med, ax=ax, color=color_dict[key], lw=2.0,
            normalised=True, label=value
        )
        x, ecdf = get_ecdf(vpec_med)
        f_ecdf = interp1d(x, ecdf, fill_value=(0, 1.0), bounds_error=False)
        logger.log(
            f"{f_ecdf(vpec_lo_lim) * 100:.2f}% of {value}"
            f" <= {vpec_lo_lim} km/s"
        )

    ax.axvline(vpec_lo_lim, dashes=(7, 10), color="k")

    ax.set_xlabel(r"$v_\mathrm{pec}\,(\mathrm{km~s^{-1}})$")
    ax.set_ylabel(r"$f(\leq v_\mathrm{pec})$")

    ax.set_xscale("log")

    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    ax.set_xticks([10.0, 100, 1000])

    ax.set_xlim(5, 600)
    ax.set_ylim(0, 1)

    plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.15), ncol=4)
    out_file = config.RESULTS_FIGURES_DIR / "ecdfs" / "ecdf_vpec_new.pdf"
    plt.savefig(out_file)

    logger.log(f"Figure saved to {out_file}.")
    logger.end()


def main() -> None:
    make_ecdf(verbose=True, vpec_lo_lim=200)


if __name__ == "__main__":
    main()
