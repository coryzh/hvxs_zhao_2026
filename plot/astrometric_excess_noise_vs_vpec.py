import config
import pandas as pd
import matplotlib.pyplot as plt
import data_schema as ds
import numpy as np
import astropy.units as u
from typing import Tuple
from matplotlib.ticker import ScalarFormatter
from matplotlib.colors import LogNorm
from plot_settings import CMAP


def set_up_figure(**kwargs_subplots) -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, **kwargs_subplots)

    return fig, ax


def axis_settings(ax: plt.Axes) -> None:
    ax.set_xlabel(
        r"Semi-major axis estimate, "
        r"$\sqrt{2}\epsilon d\,(\mathrm{AU})$"
    )
    ax.set_ylabel(r"$v_\mathrm{pec, min, lo}\,(\mathrm{km~s^{-1}})$")

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.get_yaxis().set_major_formatter(ScalarFormatter())
    ax.set_yticks([100, 200, 300, 400, 500, 600, 1000])
    ax.set_yticklabels(["100", "200", "300", "400", "500", "600", "1000"])
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    ax.set_xticks([0.1, 1, 10])
    ax.set_xticklabels(["0.1", "1", "10"])

    ax.set_xlim(0.02, None)
    ax.set_ylim(80.0, 1050)


def add_control(ax: plt.Axes) -> None:
    df_all = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "control_sample" / "control_sample_stage_9.csv"
    )
    df_all.dropna(
        subset=[
            "astrometric_excess_noise", "dist_med", "vpec_min_med",
            "e_vpec_min"
        ], inplace=True
    )
    df_all = df_all[df_all["distance_inference"] != "fixed_at_1"]

    aen = df_all["astrometric_excess_noise"].values
    x = (
        np.sqrt(2) * (aen * u.mas).to(u.rad).value
        * df_all["dist_med"].values * u.kpc
    )

    x = x.to(u.AU).value
    y = df_all["vpec_min_med"] - df_all["e_vpec_min"]

    _ = ax.scatter(
        x, y, s=0.1, marker=".", zorder=0.5, color="k",
        rasterized=True
    )

    # ax.scatter(bp_rp, g_abs, marker="o", s=0.1, color="k", alpha=0.4,
    # rasterized=True, zorder=0)


def add_hvxs(df: pd.DataFrame, ax: plt.Axes, fig: plt.Figure) -> None:
    _epsilon_filter = df[ds.Gaia.astrometric_excess_noise] > 0
    df_filtered = df[_epsilon_filter]

    df_filtered = df_filtered.sort_values("dist_med", ascending=False)

    aen = df_filtered[ds.Gaia.astrometric_excess_noise].values
    x = (
        np.sqrt(2) * (aen * u.mas).to(u.rad).value
        * df_filtered["dist_med"].values * u.kpc
    )
    x = x.to(u.AU).value
    y = df_filtered["vpec_min_med"] - df_filtered["e_vpec_min"]
    dist = df_filtered["dist_med"]

    ax.axhline(y=150.0, ls="--", color="k")

    color_min = 0.1
    color_max = 20.0
    color_norm = LogNorm(vmin=color_min, vmax=color_max)
    scatter = ax.scatter(
        x, y, s=20, marker="o", c=dist, cmap=CMAP, ec="k",
        norm=color_norm, alpha=0.8
    )

    # Get the positions of the top and bottom subplots to calculate the
    # colorbar's height
    box = ax.get_position()  # Get the position of the top-right subplot

    # Calculate the position and dimensions for the colorbar
    left = box.x1 + 0.005  # Slightly to the right of the rightmost subplot
    bottom = box.y0  # Bottom edge aligned with the bottom subplot
    height = box.y1 - box.y0  # Covering the height of both rows
    width = 0.03  # Fixed width for the colorbar

    _cbar_ax = fig.add_axes([left, bottom, width, height])
    _cbar = fig.colorbar(scatter, cax=_cbar_ax, orientation="vertical")
    _cbar.ax.set_yticks([0.1, 1.0, 10.0, 20.0])
    _cbar.ax.set_yticklabels(["0.1", "1", "10", "20"])
    _cbar.set_label(r"$d\,\mathrm{(kpc)}$")


def make_plot() -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources"
                     / "combined_vpec_lolim_gt_150_unique_stage_5.csv")

    fig, ax = set_up_figure(figsize=(12, 10))
    add_hvxs(df, ax, fig)
    add_control(ax)
    axis_settings(ax)

    plt.savefig(
        config.RESULTS_FIGURES_DIR
        / "excess_noise" / "aen_vs_vpec_vpec_lolim_gt_150.pdf"
    )


if __name__ == "__main__":
    make_plot()
