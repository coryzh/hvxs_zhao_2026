import pandas as pd
from gaia_cmd_plotter.gaia_cmd_axis import GaiaCMDAxis
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Tuple, Any
from matplotlib import colors
# from plot.plot_settings import SCATTER_DICT_CMD
from utils.process_string import get_short_id
import plot.plot_settings as ps
import config
from matplotlib import cm
from matplotlib.lines import Line2D


def preprocessing(df: pd.DataFrame) -> pd.DataFrame:
    cols_to_imputate = ["ebpminrp_gspphot", "ag_gspphot"]
    cols_to_dropna = ["bp_rp", "phot_g_mean_mag", "dist_med"]
    df[cols_to_imputate] = df[cols_to_imputate].fillna(0)

    df = df.dropna(subset=cols_to_dropna, how="any")

    return df


def make_figure(
        use_nearby_star_cmd: bool = False) -> Tuple[plt.Figure, plt.Axes]:
    """
    Make a matplotlib figure and axis object
    """
    plt.style.use("mycustomised")
    if use_nearby_star_cmd:
        fig = plt.figure(figsize=(10, 10))
        ax = GaiaCMDAxis(fig)

    else:
        fig, ax = plt.subplots(1, 1, figsize=(8, 10))

    return fig, ax


def axes_settings(ax: plt.Axes) -> None:
    ax.set_xlim(-0.1, 3.1)
    ax.set_ylim(10.5, 1.1)

    ax.set_xlabel("Bp$-$Rp")
    ax.set_ylabel(r"$M_\mathrm{G}$")


def add_gold(ax: plt.Axes) -> Any:
    in_file_gold = (
        config.RESULTS_CATALOGUE_DIR / "prime_sample"
        / "gold_sample_150525_curated_sorted_by_ra.csv"
    )
    df = pd.read_csv(in_file_gold)
    df = preprocessing(df)
    # Dropping rows could mess up the indices,
    # so some future updates is needed to make the script more stable against
    # index changes.

    bp_rp = (
        df["phot_bp_mean_mag"]
        - df["phot_rp_mean_mag"]
        - df["ebpminrp_gspphot"]
    )

    dist = df["dist_med"]
    g_abs = (
        df["phot_g_mean_mag"]
        - df["ag_gspphot"]
        - 5.0 * np.log10(dist) - 10.0
    )

    marker_styles = ps.generate_marker_styles(df.shape[0])

    for i, row in df.iterrows():
        name = row["ID_x"]
        name_short = get_short_id(name)

        ax.plot(
            bp_rp[i], g_abs[i], mec="k", ms=12, ls="none", label=name_short,
            **marker_styles[i]
        )
    handles, labels = ax.get_legend_handles_labels()
    return handles, labels


def add_hvxs(in_file: Path, ax: plt.Axes) -> cm.ScalarMappable:
    df = pd.read_csv(in_file)
    # df_prime = pd.read_csv(in_file.parent / f"{in_file.stem}_prime.csv")

    df = preprocessing(df)
    # df_prime = preprocessing(df_prime)

    bp_rp = (
        df["phot_bp_mean_mag"]
        - df["phot_rp_mean_mag"]
        - df["ebpminrp_gspphot"]
    )

    dist = df["dist_med"]
    g_abs = (
        df["phot_g_mean_mag"]
        - df["ag_gspphot"]
        - 5.0 * np.log10(dist) - 10.0
    )

    df["vpec_min_lolim"] = df["vpec_min_med"] - df["e_vpec_min"]
    df = df.sort_values(by="vpec_min_lolim", ascending=True)
    # c = df["vpec_min_lolim"]
    sm = cm.ScalarMappable(
        norm=colors.PowerNorm(gamma=0.3), cmap=ps.CMAP
    )

    ax.scatter(
        bp_rp, g_abs, zorder=1, label="HVXS", **ps.SCATTER_DICT_HVXS
        # norm=sm.norm, cmap=sm.cmap
    )

    # for i, row in df_prime.iterrows():
    #     bp_rp_prime = row["bp_rp"]
    #     g_abs_prime = (
    #         row["phot_g_mean_mag"] - 5.0 * np.log10(row["dist_med"]) - 10.0
    #     )
    #     name = get_short_id(row["ID_x"])
    #     ax.scatter(
    #         bp_rp_prime, g_abs_prime, fc=ps.PRIME_SOURCE_COLOR[i],
    #         marker=ps.PRIME_SOURCE_MARKER[i], label=name,
    #         **ps.PRIME_SCATTER_MARKER_SETTINGS
    #     )

    # legend = ax.legend(
    #     bbox_to_anchor=[0.65, 0.99], loc="upper left", handletextpad=0.2
    # )
    # for handle in legend.legend_handles:
    #     handle.set_alpha(1.0)

    return sm


def add_background(ax: plt.Axes, fig: plt.Figure) -> None:
    df_all = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR / "control_sample"
        / "control_sample_stage_10.csv"
    )

    df_all = preprocessing(df_all)

    bp_rp = df_all["bp_rp"] - df_all["ebpminrp_gspphot"]
    dist = df_all["dist_med"]
    g_abs = (
        df_all["phot_g_mean_mag"]
        - df_all["ag_gspphot"] - 5.0 * np.log10(dist) - 10.0
    )
    _ = ax.hist2d(
        bp_rp, g_abs, bins=180, cmin=0.1, norm=colors.PowerNorm(0.3),
        zorder=0.5, cmap="Greens"
    )


def add_control(ax: plt.Axes, df_control: pd.DataFrame) -> None:
    bp_rp = df_control["bp_rp"] - df_control["ebpminrp_gspphot"]
    dist = df_control["dist_med"]
    g_abs = (
        df_control["phot_g_mean_mag"]
        - df_control["ag_gspphot"] - 5.0 * np.log10(dist) - 10.0
    )

    ax.scatter(
        bp_rp, g_abs, **ps.SCATTER_DICT_CONTROL_CMD,
    )


def add_cbar(ax: plt.Axes, fig: plt.Figure, sm: cm.ScalarMappable) -> None:
    cax = ax.inset_axes([0.5, 0.85, 0.45, 0.05])
    cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
    cbar.set_label(
        r"$v_\mathrm{pec, min, lo}\,(\mathrm{km~s^{-1}})$",
        labelpad=10, size=20
    )
    cbar.ax.xaxis.set_label_position("top")
    cbar.ax.set_xscale('log')

    cbar.set_ticks([200, 500, 1000])
    cbar.set_ticklabels(["200", "500", "1000"], size=18)


def make_cmd(in_file: Path) -> None:
    fig, ax = make_figure(use_nearby_star_cmd=False)
    df_control = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "control_sample"
        / "control_sample_stage_11.csv"
    )
    add_control(ax, df_control=df_control)
    _ = add_hvxs(in_file, ax)
    handles, labels = add_gold(ax)
    handle_HVXS = Line2D([0], [0], marker="x", color="green", ms=10,
                         ls="none", mew=2.0)
    handles[0] = handle_HVXS
    axes_settings(ax)
    # add_cbar(ax, fig, sm)
    out_file = (
        config.RESULTS_FIGURES_DIR
        / "gaia_cmd" / "gaia_cmd.pdf"
    )

    legend = plt.legend(
        handles, labels, loc="center left", bbox_to_anchor=[1.0, 0.5]
    )
    for handle in legend.legend_handles:
        handle.set_alpha(1.0)

    plt.savefig(out_file)


def main() -> None:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources"
        / "hvxs_vpec_lo_gt_200_2sigma_one_neighbour_w_bitmask.csv"
    )
    make_cmd(in_file)


if __name__ == "__main__":
    main()
