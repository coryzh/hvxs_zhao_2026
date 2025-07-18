import config
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import gdr3apcal
from matplotlib.gridspec import GridSpec
from typing import Any, List
from matplotlib.lines import Line2D
from matplotlib.patches import Patch


def calibration_of_mh(df: pd.DataFrame) -> pd.DataFrame:
    df = df.rename(
        columns={"ra_gaia": "ra", "dec_gaia": "dec"}
    )
    calib = gdr3apcal.GaiaDR3_GSPPhot_cal()
    mh_calibrated = calib.calibrateMetallicity(df)

    df["mh_gspphot"] = mh_calibrated

    return df


def build_subplot_grid(n_dim: int) -> Any:
    plt.style.use("mycustomised")
    fig = plt.figure(figsize=(14, 14))

    gs = GridSpec(
        n_dim, n_dim, wspace=0.02, hspace=0.02
    )
    axs = [[None for _ in range(n_dim)] for _ in range(n_dim)]
    for i in range(n_dim):
        for j in range(n_dim):
            if j > i:
                continue

            ax = fig.add_subplot(gs[i, j])

            if (i == j) and (j < n_dim - 1):
                ax.set_xticklabels([])

            if i == j:
                ax.set_yticklabels([])

            axs[i][j] = ax

    return fig, axs, gs


def axes_settings(axs: List[plt.Axes]) -> None:
    ax_scatter = axs[-1][0]
    ax_scatter.set_xlabel(r"$\mathrm{[M/H]_{gspphot}}$")
    ax_scatter.set_ylabel(r"$|z|\,\mathrm{(kpc)}$")
    # ax_scatter.set_yscale("log")
    ax_scatter.set_ylim(0, 12)
    ax_scatter.set_xlim(-4.15, 0.80)

    ax_yhist = axs[-1][-1]
    ax_xhist = axs[0][0]

    ax_yhist.set_xlim(ax_scatter.get_ylim())
    ax_xhist.set_xlim(ax_scatter.get_xlim())

    ax_yhist.set_xlabel(ax_scatter.get_ylabel())


def add_scatter(
        df: pd.DataFrame, axs: List[plt.Axes], **kwargs_scatter
) -> None:

    x = df["mh_gspphot"].values
    y = np.abs(df["z_med"].values)

    axs[-1][0].scatter(x, y, **kwargs_scatter)


def add_hist(df: pd.DataFrame, axs: List[plt.Axes], **kwargs_hist) -> None:

    x = df["mh_gspphot"].values
    y = np.abs(df["z_med"].values)

    x_bins = np.linspace(-4.1, 0.8, 30)
    y_bins = np.linspace(0, 24, 30)
    x_ax = axs[0][0]
    y_ax = axs[1][1]

    x_hist = x_ax.hist(
        x, bins=x_bins, density=True, histtype="stepfilled", **kwargs_hist
    )

    y_hist = y_ax.hist(
        y, bins=y_bins, density=True, histtype="stepfilled", **kwargs_hist
    )


def add_legend(fig: plt.figure, gs: GridSpec) -> None:
    legned_ax = fig.add_subplot(gs[0, 1])
    legned_ax.axis("off")

    handle_hvxs = Line2D(
        [0], [0], marker="x", color="green", ms=10,
                         ls="none", mew=2.0
    )

    handle_cob = Line2D(
        [0], [0], marker="s", color="r", ms=10, ls="none"
    )

    handle_hist_hvxs = Patch(
        facecolor="g", edgecolor="g", alpha=0.5, lw=2.0
    )

    handle_hist_cob = Patch(
        facecolor="r", edgecolor="r", alpha=0.5, lw=2.0
    )

    handle_hist_control = Patch(
        facecolor="k", edgecolor="k", alpha=0.5, lw=2.0
    )

    handles = [
        handle_hvxs, handle_cob,
        handle_hist_hvxs, handle_hist_cob, handle_hist_control
    ]

    labels = ["HVXS", "Known COBs", "HVXS", "Known COBs", "Control"]

    legned_ax.legend(handles, labels, loc="center", frameon=False)


def main() -> None:
    in_file_control = (
        config.RESULTS_CATALOGUE_DIR / "ready_catalogues" / "control_c.csv"
    )

    in_file_hvxs = (
        config.RESULTS_CATALOGUE_DIR / "ready_catalogues" / "hvxs.csv"
    )

    in_file_cob = (
        config.RESULTS_CATALOGUE_DIR
        / "v_catalogs_contaminants"
        / "known_cobs_w_gspphot_params_c.csv"
    )

    df_control = pd.read_csv(in_file_control)
    df_hvxs = pd.read_csv(in_file_hvxs)
    df_cob = pd.read_csv(in_file_cob)

    df_hvxs = calibration_of_mh(df_hvxs)
    df_cob = calibration_of_mh(df_cob)
    df_control = calibration_of_mh(df_control)

    fig, axs, gs = build_subplot_grid(n_dim=2)
    axes_settings(axs)
    add_scatter(
        df_control, axs=axs, marker=".", s=0.01,
        alpha=0.5, c="k", rasterized=True
    )
    add_scatter(
        df_hvxs, axs=axs, s=30, marker="x", c="green", alpha=0.6, zorder=1,
        label="HVXS"
    )
    add_scatter(
        df_cob, axs=axs, s=30, marker="s", c="r", zorder=1,
        label="COBs"
    )

    add_hist(df_control, axs=axs, fc="k", ec="k", lw=2, alpha=0.5)
    add_hist(df_hvxs, axs=axs, fc="g", ec="g", lw=2, alpha=0.5)
    add_hist(df_cob, axs=axs, fc="r", ec="r", lw=2, alpha=0.5)

    add_legend(fig, gs)

    plt.savefig(
        config.RESULTS_FIGURES_DIR / "mh_vs_z" / "mh_vs_z.pdf"
    )


if __name__ == "__main__":
    main()
