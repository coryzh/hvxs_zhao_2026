import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import config
from catalog.select.clean_for_plotting import clean_for_fxfg_vs_bprp
from matplotlib.ticker import ScalarFormatter, FormatStrFormatter
from matplotlib import colors
from pathlib import Path
from plot_settings import CMAP
from mpl_toolkits.axes_grid1 import make_axes_locatable

# colors = sns.color_palette("hls", 4)
#
# color_dict = {
#     "csc": colors[0], "xmm": colors[1], "erass": colors[2], "swift": colors[3]
# }
#
# label_dict = {
#     "csc": "CSC", "xmm": "4XMM", "erass": "eRASS", "swift": "2SXP"
# }


def add_control_sample(axs: np.ndarray[plt.Axes]) -> None:
    """Control sample plotted in the background"""

    df_all = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "control_sample"
                         / "control_sample_stage_9.csv")
    df_all = df_all[df_all.dist_med <= 1.5]
    for ax in axs.flatten():
        ax.scatter(df_all.bp_rp, df_all.fx_fg, s=0.01, color="k", marker="o", alpha=0.5,
                   zorder=-1, rasterized=True)


def add_hvx(in_file_csv: Path, fig: plt.Figure, axs: np.ndarray[plt.Axes]) -> None:
    df = pd.read_csv(in_file_csv)
    df = clean_for_fxfg_vs_bprp(df, verbose=False)
    df["vpec_min_lolim"] = df["vpec_min_med"] - df["e_vpec_min"]
    df = df.sort_values("vpec_min_lolim", ascending=True)
    color_val = df["vpec_min_lolim"]
    color_min = color_val.min()
    color_max = color_val.max()
    # color_norm = colors.LogNorm(vmin=color_min, vmax=color_max)

    # vpec_bins = np.linspace(color_val.min(), color_val.max(), 5)
    # print(vpec_bins)
    df_arr = np.array_split(df, len(axs.flatten()))
    vpec_bins = np.array([150.0, 180.0, 220.0, 300.0, 1500.0])

    for i, ax in enumerate(axs.flatten()):
        _filter = (color_val >= vpec_bins[i]) & (color_val <= vpec_bins[i+1])
        df_sub = df_arr[i]
        color_val_sub = df_sub["vpec_min_lolim"]
        scatter = ax.scatter(df_sub.bp_rp, df_sub.fx_fg, s=30, marker="o", ec="k", c=color_val_sub,
                             cmap=CMAP, zorder=1, rasterized=False)

        # ax.text(x=0.60, y=0.1, s=rf"$[{vpec_bins[i]:.0f}, {vpec_bins[i+1]:.0f}]$",
        #         transform=ax.transAxes, fontsize=40, ha="left", va="bottom")

        # Get the positions of the top and bottom subplots to calculate the colorbar's height
        # top_box = ax.get_position()  # Get the position of the top-right subplot
        # bottom_box = ax.get_position()  # Get the position of the bottom-right subplot

        # Calculate the position and dimensions for the colorbar
        # left = top_box.x0 + 0.6  # Slightly to the right of the rightmost subplot
        # bottom = top_box.y0  # Bottom edge aligned with the bottom subplot
        # height = 0.015  # Covering the height of both rows
        # width = (top_box.x1 - top_box.x0) * 0.5  # Fixed width for the colorbar
        cax = ax.inset_axes([0.55, 0.1, 0.4, 0.05])
        _cbar = fig.colorbar(scatter, cax=cax, orientation="horizontal")
        _cbar.set_label(r"$v_\mathrm{pec, min, lo}$", labelpad=10)  # Set the label text
        _cbar.ax.xaxis.set_label_position("top")
        # _cbar.ax.set_position([0.6, 0.01, 0.1, 0.015])
        # _cbar_ax = fig.add_axes([left, bottom, width, height])

        # _cbar.ax.set_yticks([200, 300, 400, 600, 1000])
        # _cbar.ax.set_yticklabels(["200", "300", "400", "600", "1000"])
        # _cbar.set_label(r"$v_\mathrm{pec, min, lo}\,(\mathrm{km~s^{-1}})$", fontsize=50)


def add_separatrix(axs: np.ndarray[plt.Axes]) -> None:
    for ax in axs.flatten():
        bp_rp_min, bp_rp_max = ax.get_xlim()
        bp_rp_line = np.linspace(bp_rp_min, bp_rp_max, 100)
        fxfg_line = 10 ** (bp_rp_line - 3.5)
        ax.plot(bp_rp_line, fxfg_line, lw=3.0, color="r")


def axes_settings(fig: plt.Figure, axs: np.ndarray[plt.Axes]) -> None:
    for ax in axs.flatten():
        ax.set_xlim(-0.8, 3.9)
        ax.set_ylim(1.5e-6, 200)
        ax.set_yscale("log")

        ax.get_yaxis().set_major_formatter(ScalarFormatter())
        ax.set_yticks([1e-5, 1e-4, 0.001, 0.01, 0.1, 1, 10, 100])
        ax.set_yticklabels([r"$10^{-5}$", r"$10^{-4}$", "0.001", "0.01", "0.1", "1", "10", "100"])

    fig.text(0.5, 0.05, r"Bp$-$Rp", ha='center', va='center', fontsize=50)
    fig.text(0.05, 0.5, r"$F_X/F_G$", ha='center', va='center', rotation=90, fontsize=50)
    # axs.set_xlabel(r"Bp$-$Rp")
    # axs.set_ylabel(r"$F_X/F_G$")


def make_figure() -> None:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(2, 2, figsize=(20, 20),
                           sharex=True, sharey=True)

    in_file_csv = (config.RESULTS_CATALOGUE_DIR / "high-v_sources"
                   / "combined_vpec_lolim_gt_150_unique_stage_9.csv")

    axes_settings(fig, ax)
    add_control_sample(ax)
    add_separatrix(ax)
    add_hvx(in_file_csv, fig, ax)
    plt.subplots_adjust(hspace=0.01, wspace=0.01, right=0.90)
    plt.savefig(config.RESULTS_FIGURES_DIR / "high-v_sources" / f"{in_file_csv.stem}_bprp_vs_fxfg.pdf")


if __name__ == "__main__":
    make_figure()

# def make_figure_all_hvx() -> None:
#     plt.style.use("mycustomised")
#     fig, ax = plt.subplots(1, 1, figsize=(10, 10))
#
#     df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_med_gt_200_unique_cleaned.csv")
#     fxfg_grid = 10 ** np.arange(-5, 1, 1.0)
#     for key, val in color_dict.items():
#         _filter = df["from"] == key
#         df_filtered = df[_filter]
#
#         x = df_filtered["bp_rp"]
#         y = df_filtered["fx_fg"]
#
#         ax.scatter(x, y, s=70, fc=color_dict[key], ec="k", marker="o", label=label_dict[key], alpha=0.8)
#
#     for i in range(1, len(fxfg_grid)):
#         _filter_fx = (df["fx_fg"] >= fxfg_grid[i - 1]) & (df["fx_fg"] <= fxfg_grid[i])
#         df = df.dropna(subset=["f_x_err"])
#         df_filtered_fx = df[_filter_fx]
#         df_filtered_fx["f_g"] = df_filtered_fx.f_x / df_filtered_fx.fx_fg
#         df_filtered_fx["fx_fg_err"] = df_filtered_fx.f_x_err / df_filtered_fx.f_g
#         med_fx_fg_err = np.median(df_filtered_fx["fx_fg_err"].values)
#
#         x = 5.0
#         y = 0.5 * (fxfg_grid[i - 1] + fxfg_grid[i])
#
#         ax.errorbar(x=x, y=y, xerr=0, yerr=med_fx_fg_err, marker="s", mfc="k", mec="k",
#                     ls="none", ecolor="k", lw=1.5, capsize=5.0)
#
#     bp_rp_min, bp_rp_max = ax.get_xlim()
#     bp_rp_line = np.linspace(bp_rp_min, bp_rp_max, 100)
#     fxfg_line = 10 ** (bp_rp_line - 3.5)
#     ax.plot(bp_rp_line, fxfg_line, lw=1.5, color="k")
#
#     ax.set_xlim(-0.8, 6.0)
#     ax.set_yscale("log")
#     ax.set_xlabel(r"Bp$-$Rp")
#     ax.set_ylabel(r"$F_X/F_G$")
#
#     ax.get_yaxis().set_major_formatter(ScalarFormatter())
#     ax.set_yticks([1e-5, 1e-4, 0.001, 0.01, 0.1, 1, 10])
#     ax.set_yticklabels([r"$10^{-5}$", r"$10^{-4}$", "0.001", "0.01", "0.1", "1", "10"])
#
#     # plt.legend(loc="upper center", bbox_to_anchor=(0.5, 1.1), ncol=3)
#     plt.savefig(config.RESULTS_FIGURES_DIR / "fxfg_vs_bprp.pdf")
