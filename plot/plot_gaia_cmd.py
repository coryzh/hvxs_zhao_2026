import pandas as pd
from gaia_cmd_plotter.gaia_cmd_axis import GaiaCMDAxis
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Tuple
from matplotlib import colors
from plot.plot_settings import SCATTER_DICT_CMD
import config


def make_figure(use_nearby_star_cmd: bool = False) -> Tuple[plt.Figure, plt.Axes]:
    """
    Make a matplotlib figure and axis object
    """
    plt.style.use("mycustomised")
    if use_nearby_star_cmd:
        fig = plt.figure(figsize=(10, 10))
        ax = GaiaCMDAxis(fig)

    else:
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    return fig, ax


def axes_settings(ax: plt.Axes) -> None:
    ax.set_xlim(-1, 5.5)
    ax.set_ylim(15, -2.5)

    ax.set_xlabel("Bp$-$Rp")
    ax.set_ylabel(r"$M_\mathrm{G}$")


def add_sample(in_file: Path, ax: plt.Axes) -> None:
    df = pd.read_csv(in_file)
    bp_rp = df["phot_bp_mean_mag"] - df["phot_rp_mean_mag"]
    dist = df["dist_med"]
    g_abs = df["phot_g_mean_mag"] - 5.0 * np.log10(dist) - 10.0

    ax.scatter(bp_rp, g_abs, **SCATTER_DICT_CMD)


def add_background(ax: plt.Axes) -> None:
    df_all = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "control_sample" / "control_sample_stage_9.csv")
    df_all.dropna(subset=["bp_rp", "dist_med", "phot_g_mean_mag"], inplace=True)
    df_all = df_all[df_all["distance_inference"] != "fixed_at_1"]
    bp_rp = df_all["bp_rp"]
    dist = df_all["dist_med"]
    g_abs = df_all["phot_g_mean_mag"] - 5.0 * np.log10(dist) - 10.0
    # print(min(bp_rp), max(bp_rp))
    # print(min(g_abs), max(g_abs))
    _ = ax.hist2d(bp_rp, g_abs, bins=200, cmin=0.1, norm=colors.PowerNorm(0.5), zorder=0.5, cmap="Greens")
    # ax.scatter(bp_rp, g_abs, marker="o", s=0.1, color="k", alpha=0.4, rasterized=True, zorder=0)


def make_cmd(in_file: Path) -> None:
    fig, ax = make_figure(use_nearby_star_cmd=False)
    add_background(ax)
    add_sample(in_file, ax)
    axes_settings(ax)

    out_file = config.RESULTS_FIGURES_DIR / "high-v_sources" / f"{in_file.stem}_gaia_cmd.pdf"
    plt.savefig(out_file)


def main() -> None:
    in_file = config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_lolim_gt_150_unique_stage_9.csv"
    make_cmd(in_file)


if __name__ == "__main__":
    main()
