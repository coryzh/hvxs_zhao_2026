import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import config
from typing import Tuple
from plot_settings import CMAP
from matplotlib import colors
import matplotlib.gridspec as gridspec


def make_figure() -> Tuple[plt.Figure, list[plt.Axes]]:
    plt.style.use("mycustomised")
    fig = plt.figure(figsize=(10, 10))
    gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.05, wspace=0.05)

    ax_main = fig.add_subplot(gs[1:4, 0:3])
    ax_xhist = fig.add_subplot(gs[0, 0:3], sharex=ax_main)
    ax_yhist = fig.add_subplot(gs[1:4, 3], sharey=ax_main)

    ax = [ax_main, ax_xhist, ax_yhist]
    return fig, ax


def axes_settings(ax: list[plt.Axes]) -> None:
    ax[0].set_xlabel(r"$d\,(\mathrm{kpc})$")
    ax[0].set_ylabel(r"$v_\mathrm{pec, min, lo}\,(\mathrm{km~s^{-1}})$")

    ax[0].set_xscale("log")
    ax[0].set_yscale("log")

    # ax[1].set_yscale("log")
    # ax[2].set_xscale("log")

    ax[0].set_xlim(0.01, 15)
    ax[0].set_ylim(2.5, 1400)

    # ax[0].set_xticks([0.01, 0.1, 1, 10])
    # ax[0].set_xticklabels(["0.01", "0.1", "1", "10"])
    ax[0].set_yticks([10, 100, 1000])
    ax[0].set_yticklabels(["10", "100", "1000"])

    ax[1].tick_params(labelleft=False, labelbottom=False)
    ax[2].tick_params(labelbottom=False, labelleft=False)


def add_control_and_hvxs(df_hvxs: pd.DataFrame, ax: list[plt.Axes]) -> None:
    df_control = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "control_sample" / "control_sample_stage_9.csv")
    _filter = df_control["distance_inference"] != "fixed_at_1"
    df_control = df_control[_filter]

    min_aen_val = 1e-3
    df_hvxs = df_hvxs.sort_values("astrometric_excess_noise", ascending=True)
    df_hvxs["astrometric_excess_noise"] = df_hvxs["astrometric_excess_noise"].replace(0, min_aen_val)

    log_y = np.log10(df_control["vpec_min_med"] - df_control["e_vpec_min"])
    y_bins = np.logspace(min(log_y), max(log_y), 100)
    log_x = np.log10(df_control["dist_med"])
    x_bins = np.logspace(min(log_x), max(log_x), 100)

    c_val = df_hvxs["astrometric_excess_noise"] + min_aen_val
    color_norm = colors.LogNorm(vmin=min_aen_val, vmax=max(c_val))
    hist_style = {
        "HVXS": {"ec": "r", "lw": 2.0},
        "Control": {"ec": "k", "lw": 2.0}
    }

    scatter_style = {
        "HVXS": {"s": 20, "ec": "k", "c": c_val, "rasterized": True, "cmap": CMAP, "norm": color_norm},
        "Control": {"s": 0.01, "c": "k", "alpha": 0.5, "rasterized": True}
    }

    df_dict = {
        "HVXS": df_hvxs,
        "Control": df_control
    }

    for key, df in df_dict.items():
        x = df["dist_med"]
        y = df["vpec_min_med"] - df["e_vpec_min"]
        if key == "HVXS":
            scatter = ax[0].scatter(x, y, **scatter_style[key])
        else:
            ax[0].scatter(x, y, **scatter_style[key])

        ax[1].hist(x, bins=x_bins, density=True, histtype="step", **hist_style[key])
        ax[2].hist(y, bins=y_bins, density=True, histtype="step", orientation="horizontal", **hist_style[key])

    ax[0].axhline(y=150, ls=":", color="k")

    cax = ax[0].inset_axes(bounds=(0.08, 0.8, 0.35, 0.05))
    _cbar = plt.colorbar(scatter, cax=cax, orientation="horizontal")
    _cbar.set_label(r"$\epsilon$", labelpad=10)  # Set the label text
    _cbar.ax.xaxis.set_label_position("top")
    _cbar.ax.set_xticks([0.001, 0.1, 10])
    _cbar.ax.set_xticklabels(["0.001", "0.1", "10"], fontsize=17)
# def add_hvxs(df: pd.DataFrame, ax: list[plt.Axes]) -> None:
#     x = df["dist_med"]
#     y = df["vpec_min_med"] - df["e_vpec_min"]
#     ax[0].scatter(x, y, s=40, marker="o", ec="k", fc="r")
#     ax[0].axhline(y=150, ls=":", color="k")


def make_plot() -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_lolim_gt_150_unique_stage_10.csv")

    fig, ax = make_figure()
    axes_settings(ax)
    add_control_and_hvxs(df_hvxs=df, ax=ax)
    # add_hvxs(df, ax[0])
    plt.savefig(config.RESULTS_FIGURES_DIR / "dist_vs_vpec" / "vpec_lolim_gt_150_vpec_vs_dist_stage_10.pdf")


def main() -> None:
    make_plot()


if __name__ == "__main__":
    main()
