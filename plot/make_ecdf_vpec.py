import matplotlib.pyplot as plt
import pandas as pd
import config
from utils.ecdf import plot_ecdf
from log.loggers import VerboseLogger
import seaborn as sns


colors = sns.color_palette("hls", 6)


def make_ecdf(verbose: bool = False) -> None:
    source_types = {"as": "Active stars", "ab": "Active binaries", "yso": "YSOs", "cv": "CVs"}
    color_dict = {"as": colors[0], "ab": colors[1], "yso": colors[2], "cv": colors[3], "LMXB": colors[4],
                  "PSR": colors[5]}
    logger = VerboseLogger(verbose=verbose)

    logger.begin()
    logger.log(f"Plotting routine starts.\n")
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(13, 10))

    for key, value in source_types.items():
        df = pd.read_csv(config.ROOT_DIR / "results" / key / "catalogues" / f"{key}_gaia_w_vpec.csv")
        logger.log(f"{df.shape[0]} {value} loaded.")
        vpec_med = df["vpec_med"].values
        # vpec_lo = vpec_med - df["e_vpec"].values
        # vpec_up = vpec_med + df["E_vpec"].values

        plot_ecdf(arr=vpec_med, ax=ax, color=color_dict[key], normalised=True, label=value)

    df_xrb = pd.read_csv(config.ROOT_DIR / "results" / "xrb" / "catalogues"/ "xrb_gaia_w_vpec.csv")
    xrb_types = dict(LMXB="LMXBs", PSR="PSRs")
    for key, value in xrb_types.items():
        xrb_filter = df_xrb.Type.str.contains(key)
        df_xrb_sub = df_xrb[xrb_filter]
        plot_ecdf(df_xrb_sub.vpec_med, ax=ax, color=color_dict[key], normalised=True, label=value)

    ax.set_xlabel(r"$v_\mathrm{pec}\,(\mathrm{km~s^{-1}})$")
    ax.set_ylabel(r"$f(\leq v_\mathrm{pec})$")

    ax.set_xticks([10, 100, 1000])
    ax.set_xticklabels(["10", "100", "1000"])

    ax.set_xlim(5, None)
    ax.set_ylim(0, 1)
    ax.set_xscale("log")

    plt.legend(loc="lower right")
    out_file = config.RESULTS_FIGURES_DIR / "ecdf_vpec_min.pdf"
    plt.savefig(out_file)

    logger.log(f"Figure saved to {out_file}.")
    logger.end()


def main() -> None:
    make_ecdf(verbose=True)


if __name__ == "__main__":
    main()
