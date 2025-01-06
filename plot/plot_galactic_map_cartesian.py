import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config
from plot.plot_settings import SCATTER_DICT_GALACTIC_MAP
from typing import Tuple
from matplotlib import colors


def setup_axes() -> Tuple[plt.Figure, np.ndarray[plt.Axes]]:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 2, figsize=(16, 8))

    plt.subplots_adjust(wspace=0.20)

    return fig, ax


def axes_settings(ax: np.ndarray[plt.Axes]) -> None:
    ax[0].set_xlabel(r"$x$ (kpc)")
    ax[0].set_ylabel(r"$y$ (kpc)")

    ax[0].axvline(x=0, ls=":", color="k")
    ax[0].axhline(y=0, ls=":", color="k")

    ax[1].set_xlabel(r"$R$ (kpc)")
    ax[1].set_ylabel(r"$|z|$ (kpc)")


def add_sources(df: pd.DataFrame, ax: np.ndarray[plt.Axes]) -> None:
    ax[0].scatter(-df["x"], df["y"], **SCATTER_DICT_GALACTIC_MAP)
    ax[1].scatter(df["r_gc"], np.abs(df["z"]), **SCATTER_DICT_GALACTIC_MAP)


def background_histogram(ax: np.ndarray[plt.Axes]) -> None:
    df_all = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_med_gt_0_unique_stage_8.csv")
    df_all = df_all[df_all["distance_inference"] != "fixed_at_1"]
    ax[0].hist2d(-df_all["x"], df_all["y"], bins=50,
                 cmin=0.1, norm=colors.LogNorm(), zorder=0.5, cmap="Greens")
    ax[1].hist2d(df_all["r_gc"], np.abs(df_all["z"]), bins=50,
                 cmin=0.1, norm=colors.LogNorm(), zorder=0.5, cmap="Greens")


def make_galactic_map() -> None:
    df_hvx = pd.read_csv(config.RESULTS_CATALOGUE_DIR /
                         "high-v_sources" / "combined_vpec_lolim_gt_150_unique_stage_8.csv")
    fig, ax = setup_axes()
    axes_settings(ax)
    background_histogram(ax)
    add_sources(df_hvx, ax)

    plt.savefig(config.RESULTS_FIGURES_DIR / "high-v_sources" / "galactic_map_cartesian.pdf")


def main() -> None:
    make_galactic_map()


if __name__ == "__main__":
    main()
