import numpy as np

import config
import matplotlib.pyplot as plt
import pandas as pd
from typing import Tuple
from plot.plot_settings import DIST_INFERENCE_COLOR_DICT


def set_up_figure() -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))
    ax.set_xlabel(r"$d$ (kpc)")
    ax.set_ylabel("Counts")

    ax.set_yscale("log")

    ax.set_yticks([1, 10, 100])
    ax.set_yticklabels(["1", "10", "100"])

    return fig, ax


def add_hvxs(df: pd.DataFrame, ax: plt.Axes, fig: plt.Figure) -> None:
    bins = np.linspace(0, 15, 80)
    bin_centers = 0.5 * (bins[1:] + bins[:-1])
    # _ = ax.hist(df["dist_med"], bins=bins, ec="k", lw=2., histtype="step")
    for key, val in DIST_INFERENCE_COLOR_DICT.items():
        df_sub = df[df["distance_inference"] == key]
        dist = df_sub["dist_med"]

        hist = ax.hist(dist, bins=bins, histtype="step", ec=val, lw=1.5)

        ax.step(bin_centers, hist[0], color=val, where="mid", label=key)

        plt.legend(loc="best")


def make_figure() -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_lolim_gt_150_unique_stage_9.csv")
    fig, ax = set_up_figure()
    add_hvxs(df, ax, fig)

    plt.savefig(config.RESULTS_FIGURES_DIR / "dist_histogram" / "test.pdf")


if __name__ == "__main__":
    make_figure()
