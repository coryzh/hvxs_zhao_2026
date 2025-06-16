import matplotlib.pyplot as plt
import pandas as pd
import config
import numpy as np
import plot.plot_settings as ps
from typing import Tuple, Any
from utils.process_string import get_short_id
from matplotlib.lines import Line2D
from matplotlib.ticker import ScalarFormatter


def make_figure() -> Tuple[plt.Axes, plt.Figure]:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(12, 12))

    return fig, ax


def axes_settings(ax: plt.Axes) -> None:
    ax.set_yscale("log")
    ax.get_yaxis().set_major_formatter(ScalarFormatter())
    ax.set_yticks([1e-5, 1e-4, 0.001, 0.01, 0.1, 1, 10, 100, 1000])
    ax.set_yticklabels(
        [
            r"$10^{-5}$", r"$10^{-4}$",
            "0.001", "0.01", "0.1", "1", "10", "100", "1000"
        ]
    )

    ax.set_xlim(-0.8, 5.0)
    ax.set_ylim(6e-6, 1050)
    ax.set_xlabel("Bp$-$Rp", fontsize=38)
    ax.set_ylabel("$F_X / F_G$", fontsize=38)


def add_control(ax: plt.axes) -> None:
    df_control = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "control_sample" / "control_sample_stage_11.csv"
    )

    x = df_control["bp_rp"]
    y = df_control["fx_fg"]

    ax.scatter(
        x, y, s=0.1, marker=".", c="k", alpha=0.5, rasterized=True, zorder=0
    )


def add_hvxs(df: pd.DataFrame, ax: plt.Axes) -> None:
    x = df["bp_rp"]
    y = df["fx_fg"]

    ax.scatter(
        x, y, s=20, marker="x", c="green", alpha=0.4, zorder=1, label="HVXS"
    )


def add_gold(df: pd.DataFrame, ax: plt.Axes) -> Any:
    df = df.sort_values(by="ra_x", ascending=True)
    marker_styles = ps.generate_marker_styles(
        df.shape[0], generate_for="scatter"
    )

    for i, row in df.iterrows():
        x = row["bp_rp"]
        y = row["fx_fg"]
        name = get_short_id(row["ID_x"])

        ax.scatter(
            x, y, label=name, zorder=2, s=150, ec="k", **marker_styles[i]
        )

    handles, labels = ax.get_legend_handles_labels()

    return handles, labels


def add_separatrix(ax: plt.Axes) -> None:
    bp_rp_min, bp_rp_max = ax.get_xlim()
    bp_rp_line = np.linspace(bp_rp_min, bp_rp_max, 100)
    fxfg_line = 10 ** (bp_rp_line - 3.5)
    ax.plot(bp_rp_line, fxfg_line, lw=2.5, color="r", label="R24")


def add_legend(handles, labels) -> None:
    handle_HVXS = Line2D([0], [0], marker="x", color="green", ms=10,
                         ls="none", mew=2.0)
    handles[0] = handle_HVXS

    plt.legend(
        handles, labels, loc="upper left", bbox_to_anchor=(1.0, 1.0),
        borderaxespad=0.0
    )


def main() -> None:
    fig, ax = make_figure()

    df_hvxs = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR / "high-v_sources"
        / "hvxs_vpec_lo_gt_200_2sigma_one_neighbour_w_bitmask.csv"
    )

    df_gold = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR / "prime_sample"
        / "gold_sample_150525_curated_sorted_by_ra.csv"
    )

    add_hvxs(df_hvxs, ax)
    add_control(ax)
    handles, labels = add_gold(df_gold, ax)
    add_separatrix(ax)
    axes_settings(ax)
    add_legend(handles, labels)

    plt.savefig(
        config.RESULTS_FIGURES_DIR
        / "fxfg_vs_bprp" / "fxfg_vs_bprp.pdf"
    )


if __name__ == "__main__":
    main()
