import config
import pandas as pd
import matplotlib.pyplot as plt
import data_schema as ds
import numpy as np
import astropy.units as u
from typing import Tuple
from matplotlib.ticker import ScalarFormatter
from matplotlib.colors import LogNorm


def set_up_figure(**kwargs_subplots) -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, **kwargs_subplots)

    return fig, ax


def axis_settings(ax: plt.Axes) -> None:
    ax.set_xlabel(r"Astrometric excess noise, $\epsilon$ (mas)")
    ax.set_ylabel(r"Semi-major axis estimate (AU)")
    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.get_yaxis().set_major_formatter(ScalarFormatter())
    ax.set_yticks([0.1, 1, 10, 100])
    ax.set_yticklabels(["0.1", "1", "10", "100"])
    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    ax.set_xticks([0.01, 0.1, 1, 10])
    ax.set_xticklabels(["0.01", "0.1", "1", "10"])

    ax.set_xlim(0.008, None)
    ax.set_ylim(0.06, None)


def add_hvxs(df: pd.DataFrame, ax: plt.Axes, fig: plt.Figure) -> None:
    _epsilon_filter = df[ds.Gaia.astrometric_excess_noise] > 0
    df_filtered = df[_epsilon_filter]
    x = df_filtered[ds.Gaia.astrometric_excess_noise].values
    y = np.sqrt(2) * (x * u.mas).to(u.rad).value * df_filtered["dist_med"].values * u.kpc
    y = y.to(u.AU).value
    vpec_min_lo = df_filtered["vpec_min_med"] - df_filtered["e_vpec_min"]

    color_min = vpec_min_lo.min()
    color_max = vpec_min_lo.max()
    color_norm = LogNorm(vmin=color_min, vmax=color_max)
    scatter = ax.scatter(x, y, s=40, marker="o", c=vpec_min_lo, cmap="Greens", ec="k", norm=color_norm)

    # Get the positions of the top and bottom subplots to calculate the colorbar's height
    box = ax.get_position()  # Get the position of the top-right subplot

    # Calculate the position and dimensions for the colorbar
    left = box.x1 + 0.005  # Slightly to the right of the rightmost subplot
    bottom = box.y0  # Bottom edge aligned with the bottom subplot
    height = box.y1 - box.y0  # Covering the height of both rows
    width = 0.03  # Fixed width for the colorbar

    _cbar_ax = fig.add_axes([left, bottom, width, height])
    _cbar = fig.colorbar(scatter, cax=_cbar_ax, orientation="vertical")
    _cbar.ax.set_yticks([200, 300, 400, 600, 800])
    _cbar.ax.set_yticklabels(["200", "300", "400", "600", "800"])
    _cbar.set_label(r"$v_\mathrm{pec, min, lo}\,(\mathrm{km~s^{-1}})$")


def add_constant_distance_lines(ax: plt.Axes) -> None:
    d_list = [d * u.kpc for d in [0.5, 5.0, 30.0]]
    d_ls = [":", "--", "-."]
    epsilon_min, epsilon_max = ax.get_xlim()
    epsilon_range = np.logspace(np.log10(epsilon_min), np.log10(epsilon_max), 100) * u.mas

    for i, dist in enumerate(d_list):
        y = (dist * epsilon_range.to(u.rad).value).to(u.AU).value
        ax.plot(epsilon_range, y, lw=1.5, ls=d_ls[i], color="r", label=fr"$d={dist.value:.1f}$ kpc")

    ax.legend(loc="best")


def make_plot() -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources"
                     / "combined_vpec_lolim_gt_150_unique_w_simbad_high_ratio_simbad_cleaned_w_cl_info.csv")

    fig, ax = set_up_figure(figsize=(12, 10))
    add_hvxs(df, ax, fig)
    axis_settings(ax)
    add_constant_distance_lines(ax)

    plt.savefig(config.RESULTS_FIGURES_DIR / "excess_noise" / "aen_vs_semi_major_axis.pdf")


if __name__ == "__main__":
    make_plot()
