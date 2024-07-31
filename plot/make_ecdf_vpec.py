import matplotlib.pyplot as plt
import pandas as pd
import config
from utils.ecdf import plot_ecdf
from log.loggers import VerboseLogger


def make_ecdf(verbose: bool = False) -> None:
    source_types = dict(cv="CVs", asab="Active Stars", yso="YSOs")
    logger = VerboseLogger(verbose=verbose)

    logger.begin()
    logger.log(f"Plotting routine starts.\n")
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    for key, value in source_types.items():
        df = pd.read_csv(config.ROOT_DIR / "results" / key / "catalogues" / f"{key}_gaia_w_vpec_min.csv")
        logger.log(f"{df.shape[0]} {value} loaded.")
        vpec_med_min = df["vpec_min_med"].values

        plot_ecdf(arr=vpec_med_min, ax=ax, normalised=True, label=value)

    ax.set_xlabel(r"$v_\mathrm{pec, min}\,(\mathrm{km~s^{-1}})$")
    ax.set_ylabel(r"$f(\leq v_\mathrm{pec, min})$")

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
