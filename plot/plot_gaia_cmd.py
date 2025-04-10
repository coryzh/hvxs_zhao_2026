import pandas as pd
from gaia_cmd_plotter.gaia_cmd_axis import GaiaCMDAxis
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from typing import Tuple
from matplotlib import colors
from plot.plot_settings import SCATTER_DICT_CMD
# from utils.process_string import get_short_id
# import plot.plot_settings as ps
import config


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
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    return fig, ax


def axes_settings(ax: plt.Axes) -> None:
    ax.set_xlim(-1.1, 4.5)
    ax.set_ylim(15, -2.5)

    ax.set_xlabel("Bp$-$Rp")
    ax.set_ylabel(r"$M_\mathrm{G}$")


def add_sample(in_file: Path, ax: plt.Axes) -> None:
    df = pd.read_csv(in_file)
    df_prime = pd.read_csv(in_file.parent / f"{in_file.stem}_prime.csv")

    df = preprocessing(df)
    df_prime = preprocessing(df_prime)

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

    ax.scatter(bp_rp, g_abs, label="HVXS", **SCATTER_DICT_CMD)

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


def make_cmd(in_file: Path) -> None:
    fig, ax = make_figure(use_nearby_star_cmd=False)
    add_background(ax, fig)
    add_sample(in_file, ax)
    axes_settings(ax)

    out_file = (
        config.RESULTS_FIGURES_DIR
        / "gaia_cmd" / f"{in_file.stem}_gaia_cmd.pdf"
    )

    plt.savefig(out_file)


def main() -> None:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources" / "combined_vpec_lolim_gt_150_unique_stage_9.csv"
    )
    make_cmd(in_file)


if __name__ == "__main__":
    main()
