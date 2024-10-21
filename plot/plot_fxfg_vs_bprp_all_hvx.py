import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import config
from catalog.select.clean import clean_for_fxfg_vs_bprp
from matplotlib.ticker import ScalarFormatter
from matplotlib import colors
# colors = sns.color_palette("hls", 4)
#
# color_dict = {
#     "csc": colors[0], "xmm": colors[1], "erass": colors[2], "swift": colors[3]
# }
#
# label_dict = {
#     "csc": "CSC", "xmm": "4XMM", "erass": "eRASS", "swift": "2SXP"
# }


def add_control_sample(ax: plt.Axes) -> None:
    """Control sample plotted in the background"""

    df_all = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources"
                         / "combined_vpec_med_gt_0.0_unique_cleaned.csv")
    df_all = df_all[df_all.dist_med <= 1.5]
    ax.scatter(df_all.bp_rp, df_all.fx_fg, s=0.01, color="k", marker="o", alpha=0.5, rasterized=True)


def add_hvx(fig: plt.Figure, ax: plt.Axes) -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_lolim_gt_200.0_unique.csv")
    df = clean_for_fxfg_vs_bprp(df, verbose=False)
    color_val = (df["vpec_min_med"] - df["e_vpec_min"]).values
    scatter = ax.scatter(df.bp_rp, df.fx_fg, s=50, marker="o", ec="k", c=color_val, cmap="Greens", norm=colors.LogNorm())
    # cbar = fig.colorbar(scatter, ax)


def add_separatrix(ax: plt.Axes) -> None:
    bp_rp_min, bp_rp_max = ax.get_xlim()
    bp_rp_line = np.linspace(bp_rp_min, bp_rp_max, 100)
    fxfg_line = 10 ** (bp_rp_line - 3.5)
    ax.plot(bp_rp_line, fxfg_line, lw=1.5, color="k")


def axes_settings(ax: plt.Axes) -> None:
    ax.set_xlim(-0.8, 6.0)
    ax.set_ylim(1.5e-6, 110)
    ax.set_yscale("log")
    ax.set_xlabel(r"Bp$-$Rp")
    ax.set_ylabel(r"$F_X/F_G$")

    ax.get_yaxis().set_major_formatter(ScalarFormatter())
    ax.set_yticks([1e-6, 1e-5, 1e-4, 0.001, 0.01, 0.1, 1, 10, 100])
    ax.set_yticklabels([r"$10^{-6}$", r"$10^{-5}$", r"$10^{-4}$", "0.001", "0.01", "0.1", "1", "10", "100"])


def make_figure() -> None:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    axes_settings(ax)
    add_control_sample(ax)
    add_separatrix(ax)
    add_hvx(fig, ax)


    plt.savefig(config.RESULTS_FIGURES_DIR / "high-v_sources" / "fxfg_vs_bprp_vpec_min_lolim_gt_200.pdf")

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


if __name__ == "__main__":
    make_figure()
