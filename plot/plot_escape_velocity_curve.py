import numpy as np
import pandas as pd

import config
from potential import MW
from galpy.potential import vesc
from typing import Tuple
from astropy.units import Quantity, Unit
import plot.plot_settings as ps
import matplotlib.pyplot as plt


def make_figure() -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    ax.set_xlim(0, 30)
    ax.set_ylim(200, 4000)
    ax.set_yscale("log")
    # ax.set_xscale("log")

    ax.set_xlabel(r"$R\,\mathrm{(kpc)}$")
    ax.set_ylabel(r"$v_\mathrm{space, min, lo}\,\mathrm{(km~s^{-1})}$")

    ax.set_yticks([1000])
    ax.set_yticklabels(["1000"])

    return fig, ax


def add_esc_curve(ax: plt.Axes) -> None:
    step_size = 0.01
    _, r_max = ax.get_xlim()
    r_grid: Quantity = np.arange(step_size, r_max, step_size) * Unit("kpc")
    v_escape = vesc(MW, r_grid)

    ax.plot(
        r_grid.value, v_escape.value, ls="-", lw=2.0, color="r",
        zorder=-1
    )


def add_hvxs(df: pd.DataFrame, ax: plt.Axes) -> None:
    vspace_lolim = (df["vspace_min_med"] - df["e_vspace_min"]).values
    r = df["r_gc"].values

    ax.scatter(
        r, vspace_lolim, marker="o", s=20, fc=ps.cblind_palette[0], ec="k",
        rasterized=True, zorder=1, label="HVXS", alpha=0.8
    )


def add_runaway(df: pd.DataFrame, ax: plt.Axes) -> None:
    vspace_lolim = (df["vspace_min_med"] - df["e_vspace_min"]).values
    r = df["r_gc"].values

    ax.scatter(
        r, vspace_lolim, marker="*", s=100, fc=ps.cblind_palette[1],
        ec="k", rasterized=True, zorder=2, label="Runaway"
    )


def plot() -> None:
    df_hvxs = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources"
                          / "combined_vpec_lolim_gt_200_unique_stage_9.csv")
    df_runaway = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR / "runaway_sources"
        / "combined_vpec_lolim_gt_200_unique_stage_9_runaway.csv"
    )

    fig, ax = make_figure()
    add_hvxs(df_hvxs, ax)
    add_runaway(df_runaway, ax)
    add_esc_curve(ax)

    ax.legend(loc="upper right", fontsize=20)

    plt.savefig(
        config.RESULTS_FIGURES_DIR / "escape_velocity_curve"
        / "escape_velocity_curve.pdf"
    )


if __name__ == "__main__":
    plot()
