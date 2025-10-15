import numpy as np
import config
import pandas as pd
import matplotlib.pyplot as plt
from plot.plot_settings import SURVEY_COLOR_DICT_X, SURVEY_NAME_DICT_X
from typing import Tuple
from scipy.stats import gaussian_kde


def make_figure() -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    return fig, ax


def axes_settings(ax: plt.Axes) -> None:
    ax.set_xlabel(r"$\delta_\mathrm{x,g} / r_\mathrm{err, x}$")
    ax.set_ylabel(r"Probability density")
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)


def add_histogram(ax: plt.Axes, from_catalog: str) -> None:
    # for key, val in SURVEY_COLOR_DICT.items():
    in_file = (
        config.RESULTS_CATALOGUE_DIR / "high-v_sources_old"
        / "combined_vpec_med_gt_0_all.csv"
    )

    df = pd.read_csv(in_file)
    # sep_sigma_all = df["sep_x_g"] / df["pos_x_err"]
    # bins = np.linspace(sep_sigma_all.min(), sep_sigma_all.max(), 100)
    df_filtered = df[df["from"] == from_catalog]
    sep = df_filtered["sep_x_g"] / df_filtered["pos_x_err"]

    kde = gaussian_kde(sep)
    sep_range = np.arange(0, max(sep), 0.01)

    ax.plot(
        sep_range, kde(sep_range), lw=2.0,
        color=SURVEY_COLOR_DICT_X[from_catalog],
        label=SURVEY_NAME_DICT_X[from_catalog]
    )
    # _ = ax.hist(sep, bins=bins, density=True, histtype="step",
    # ec=SURVEY_COLOR_DICT[from_catalog],
    #             label=SURVEY_NAME_DICT[from_catalog], lw=1.5)


def make_histogram() -> None:
    fig, ax = make_figure()

    for key in SURVEY_NAME_DICT_X.keys():
        print(f"Done for {key}.")
        add_histogram(ax, from_catalog=key)

    axes_settings(ax)
    plt.legend(loc="upper right")
    plt.savefig(config.RESULTS_FIGURES_DIR / "sep_x_g_histogram.pdf")


def main() -> None:
    make_histogram()


if __name__ == "__main__":
    main()
