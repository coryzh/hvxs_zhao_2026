import matplotlib.pyplot as plt
import pandas as pd
import config
import plot.plot_settings as ps
import numpy as np
from utils.process_string import get_short_id
from matplotlib import colors
from typing import Tuple


def make_figure() -> Tuple[plt.Figure, dict]:
    plt.style.use("mycustomised")
    fig = plt.figure(figsize=(10, 10))

    gs = fig.add_gridspec(
        2, 2,
        width_ratios=[4, 1], height_ratios=[1, 4],
        left=0.1, right=0.9, bottom=0.1, top=0.9,
        wspace=0.03, hspace=0.03
    )

    ax_main = fig.add_subplot(gs[1, 0])
    ax_top = fig.add_subplot(gs[0, 0], sharex=ax_main)

    ax_dict = {
        "main": ax_main,
        "top": ax_top
    }

    return fig, ax_dict


def axes_settings(ax: list[plt.Axes]) -> None:
    ax.set_xlabel(r"$d$ (kpc)")
    ax.set_ylabel(r"$v_\mathrm{pec, min, lo}\,(\mathrm{km~s^{-1}})$")

    ax.set_xscale("log")
    ax.set_yscale("log")

    ax.set_xlim(0.1, 42)
    ax.set_ylim(8, 2200)

    ax.set_xticks([0.1, 1, 10, 20, 40])
    ax.set_xticklabels(["0.1", "1", "10", "20", "40"])
    ax.set_yticks([10, 100, 1000, 2000])
    ax.set_yticklabels(["10", "100", "1000", "2000"])


def add_prime_sources(df_prime: pd.DataFrame, ax: list[plt.Axes]) -> None:
    ax_scatter = ax

    for i, row in df_prime.iterrows():
        x = row["dist_med"]
        y = row["vpec_min_med"] - row["e_vpec_min"]
        name = get_short_id(row["ID_x"])
        ax_scatter.scatter(
            x, y, marker=ps.PRIME_SOURCE_MARKER[i],
            fc=ps.PRIME_SOURCE_COLOR[i], label=name,
            **ps.PRIME_SCATTER_MARKER_SETTINGS
        )

    legend = ax.legend(
        bbox_to_anchor=[0.02, 0.99], loc="upper left", fontsize=15
    )
    for handle in legend.legend_handles:
        handle.set_alpha(1.0)


def add_control_and_hvxs(
        ax: plt.Axes, fig: plt.Figure,
        df_hvxs: pd.DataFrame, df_control: pd.DataFrame) -> None:

    min_aen_val = 1e-3
    df_hvxs["parallax_over_error"] = (
        abs(df_hvxs["parallax_corr"]) / df_hvxs["parallax_error"]
    )
    # df_hvxs = df_hvxs.sort_values(
    #     by="parallax_over_error",
    #     ascending=False
    # )

    df_hvxs["astrometric_excess_noise"] = (
        df_hvxs["astrometric_excess_noise"]
        .replace(0, min_aen_val)
    )

    c = df_hvxs["parallax_over_error"]

    scatter_style = {
        "HVXS": {
            "s": 30, "ec": "k", "c": c, "alpha": 0.8, "rasterized": True,
            "label": "HVXS", "cmap": ps.CMAP,
            "norm": colors.LogNorm()
        },
        "Control": {
            "s": 0.1, "c": "k", "alpha": 0.5, "rasterized": True,
            "label": "Control"
        }
    }

    df_dict = {
        "HVXS": df_hvxs,
        "Control": df_control
    }

    for key, df in df_dict.items():
        x = df["dist_med"]
        y = df["vpec_min_med"] - df["e_vpec_min"]
        if key == "HVXS":
            scatter = ax.scatter(x, y, **scatter_style[key])
            cax = ax.inset_axes([0.06, 0.85, 0.4, 0.05])
            _cbar = fig.colorbar(scatter, cax=cax, orientation="horizontal")
            _cbar.set_label(r"$|\varpi|/\sigma_\varpi$", labelpad=10,
                            size=20)

            _cbar.set_ticks([0.001, 0.1, 10])
            _cbar.set_ticklabels([
                0.001, 0.1, 10
            ], size=18)
            _cbar.ax.xaxis.set_label_position("top")
        else:
            ax.scatter(x, y, **scatter_style[key])

    ax.axhline(y=150, ls=":", color="k")


def add_top_hist(
        ax_top: plt.Axes, df_hvxs: pd.DataFrame, df_control: pd.DataFrame
) -> None:
    ax_top.tick_params(axis='x', bottom=False, labelbottom=False)
    ax_top.tick_params(axis='y', labelleft=False)
    bins = np.logspace(
        np.log10(min(df_hvxs["dist_med"].min(), df_control["dist_med"].min())),
        np.log10(max(df_hvxs["dist_med"].max(), df_control["dist_med"].max())),
        100
    )

    bin_centres = 0.5 * (bins[1:] + bins[:-1])

    df_dict = {
        "HVXS": df_hvxs,
        "Control": df_control
    }

    ec_dict = {
        "HVXS": "r",
        "Control": "k"
    }

    for key, df in df_dict.items():
        x = df["dist_med"].values
        hist = ax_top.hist(
            x, bins=bins, histtype="step", density=False,
            lw=2.0, ec=ec_dict[key]
        )

        ax_top.step(
            bin_centres, hist[0], color=ec_dict[key],
            lw=2.0, where="mid", label=key
        )

    ax_top.legend(loc="best", fontsize=14)


def make_plot() -> None:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources" / "combined_vpec_lolim_gt_150_unique_stage_9.csv"
    )
    df_hvxs = pd.read_csv(in_file)
    df_control = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "control_sample" / "control_sample_stage_10.csv"
    )

    fig, ax_dict = make_figure()
    axes_settings(ax_dict["main"])
    add_control_and_hvxs(
        df_hvxs=df_hvxs, df_control=df_control, ax=ax_dict["main"], fig=fig
    )

    add_top_hist(
        ax_dict["top"], df_hvxs=df_hvxs, df_control=df_control
    )

    plt.savefig(
        config.RESULTS_FIGURES_DIR
        / "dist_vs_vpec"
        / "dist_vs_vpec.pdf"
    )


def main() -> None:
    make_plot()


if __name__ == "__main__":
    main()
