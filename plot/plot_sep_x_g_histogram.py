import config
import pandas as pd
import matplotlib.pyplot as plt
from plot.plot_settings import SURVEY_COLOR_DICT, SURVEY_NAME_DICT
from typing import Tuple


def make_figure() -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    return fig, ax


def axes_settings(ax: plt.Axes) -> None:
    ax.set_xlabel(r"Gaia-X-ray separation ($\sigma$)")
    ax.set_ylabel(r"Normalized counts")


def add_histogram(ax: plt.Axes, from_catalog: str) -> None:
    # for key, val in SURVEY_COLOR_DICT.items():
    in_file = (config.ROOT_DIR / "results" / from_catalog / "catalogues"
               / "nway_match" / f"{from_catalog}_gaia_nway_match.csv")

    df = pd.read_csv(in_file)
    sep = df["sep_x_g"] / df["pos_x_err"]

    _ = ax.hist(sep, bins="scott", density=True, histtype="step", ec=val, label=SURVEY_NAME_DICT[key])


def make_histogram() -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_med_gt_0.0_unique.csv")
    fig, ax = make_figure()
    axes_settings(ax)
    add_histogram(ax, df)

    plt.legend(loc="upper right")
    plt.savefig(config.RESULTS_FIGURES_DIR / "sep_x_g_histogram.pdf")


def main() -> None:
    make_histogram()


if __name__ == "__main__":
    main()
