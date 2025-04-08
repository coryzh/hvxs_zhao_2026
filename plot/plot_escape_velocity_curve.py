import numpy as np
import pandas as pd

import config
from potential import MW
from galpy.potential import vesc
from typing import Tuple
from astropy.units import Quantity, Unit
import matplotlib.pyplot as plt


def make_figure() -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(12, 8))

    ax.set_xlabel(r"$R\,\mathrm{(kpc)}$")
    ax.set_ylabel(r"$v_\mathrm{space}\,\mathrm{(km~s^{-1})}$")

    ax.set_yscale("log")
    # ax.set_xscale("log")

    return fig, ax


def add_esc_curve(ax: plt.Axes) -> None:
    step_size = 0.01
    r_grid: Quantity = np.arange(step_size, 20, step_size) * Unit("kpc")
    v_escape = vesc(MW, r_grid)

    ax.plot(r_grid.value, v_escape.value, ls="--", lw=2.0, color="r")


def add_hvxs(df: pd.DataFrame, ax: plt.Axes) -> None:
    vspace_lolim = (df["vspace_min_med"] - df["e_vspace_min"]).values
    r = df["r_gc"].values

    ax.scatter(
        r, vspace_lolim, marker="o", s=1, fc="r", ec="k", rasterized=True
    )


def plot() -> None:
    df_hvxs = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources"
                          / "combined_vpec_lolim_gt_150_unique_stage_9.csv")
    fig, ax = make_figure()
    add_esc_curve(ax)
    add_hvxs(df_hvxs, ax)

    plt.savefig(config.RESULTS_FIGURES_DIR / "escape_velocity_curve.pdf")


if __name__ == "__main__":
    plot()
