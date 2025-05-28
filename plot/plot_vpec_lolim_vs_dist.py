import matplotlib.pyplot as plt
import pandas as pd
import config
import plot.plot_settings as ps
import numpy as np
from utils.process_string import get_short_id
from typing import Tuple, Any
from astropy.units import Unit
from matplotlib.ticker import LogLocator
from matplotlib.colors import LogNorm
from matplotlib import cm
from matplotlib.lines import Line2D


def make_figure() -> Tuple[plt.Figure, dict]:
    plt.style.use("mycustomised")
    fig = plt.figure(figsize=(18, 10))

    gs = fig.add_gridspec(
        2, 2,
        width_ratios=[4, 4], height_ratios=[1, 4],
        left=0.1, right=0.9, bottom=0.1, top=0.9,
        wspace=0.03, hspace=0.03
    )

    ax_main = fig.add_subplot(gs[1, 0])
    ax_right = fig.add_subplot(gs[1, 1], sharey=ax_main)
    ax_top = fig.add_subplot(gs[0, 0], sharex=ax_main)
    ax_cbar = fig.add_subplot(gs[0, 1])

    ax_dict = {
        "main": ax_main,
        "right": ax_right,
        "top": ax_top,
        "cbar": ax_cbar
    }

    return fig, ax_dict


def axes_settings(ax_dict: dict) -> None:

    ax_main = ax_dict["main"]
    ax_right = ax_dict["right"]
    ax_top = ax_dict["top"]
    ax_cbar = ax_dict["cbar"]

    ax_main.set_xlabel(r"$d$ (kpc)")
    ax_main.set_ylabel(r"$v_\mathrm{pec, min, lo}\,(\mathrm{km~s^{-1}})$")

    ax_main.set_xscale("log")
    ax_main.set_yscale("log")

    ax_main.set_xlim(0.1, 42)
    ax_main.set_ylim(8, None)

    ax_main.set_xticks([0.1, 1, 10, 20, 40])
    ax_main.set_xticklabels(["0.1", "1", "10", "20", "40"])
    ax_main.set_yticks([10, 100, 1000, 2000])
    ax_main.set_yticklabels(["10", "100", "1000", "2000"])

    ax_right.set_xscale("log")

    ax_top.tick_params(axis='x', bottom=False, labelbottom=False)
    ax_top.tick_params(axis='y', labelleft=False)

    ax_right.set_xlabel(r"$\sqrt{2}d\epsilon$ (AU)")
    ax_right.tick_params(axis='y', labelleft=False)
    ax_right.set_xlim(5e-4, 300)
    ax_right.set_xticks([0.001, 0.01, 0.1, 1, 10, 100])
    ax_right.set_xticklabels([r"$10^{-3}$", "0.01", "0.1", "1", "10", "100"])
    ax_right.set_yticks([10, 100, 1000, 2000])

    for pos in ["top", "left", "bottom", "right"]:
        ax_cbar.spines[pos].set_visible(False)

    ax_cbar.tick_params(
        axis="both", which="both",
        bottom=False, top=False, left=False, right=False,
        labelbottom=False, labelleft=False
    )


def add_prime_sources(df_prime: pd.DataFrame, axs: dict[plt.Axes]) -> Any:
    marker_styles = ps.generate_marker_styles(
        df_prime.shape[0], generate_for="scatter"
    )
    for i, row in df_prime.iterrows():
        x_left = row["dist_med"]
        y_left = row["vpec_min_med"] - row["e_vpec_min"]
        # x_err_left = [[row["e_dist"]], [row["E_dist"]]]
        name = get_short_id(row["ID_x"])
        axs["main"].scatter(
            x_left, y_left, label=name, s=100, ec="k", zorder=2,
            **marker_styles[i]
        )

        # axs["main"].errorbar(
        #     x_left, y_left, xerr=x_err_left, ecolor="k", capsize=4.0,
        #     ls="none", elinewidth=2.5, zorder=1
        # )
        x_right = (
            np.sqrt(2)
            * row["dist_med"]
            * Unit("kpc") * row["astrometric_excess_noise"]
            * 1e-3 * (1. / 3600) * (np.pi / 180.)
        ).to(Unit("AU"))

        axs["right"].scatter(
            x_right, y_left, label=name, s=100, ec="k", zorder=2,
            **marker_styles[i]
        )

    handles, labels = axs["main"].get_legend_handles_labels()

    return handles, labels

    # legend = ax.legend(
    #     bbox_to_anchor=[0.02, 0.99], loc="upper left", fontsize=15
    # )
    # for handle in legend.legend_handles:
    #     handle.set_alpha(1.0)


def add_control_and_hvxs(
        ax: plt.Axes, fig: plt.Figure,
        df_hvxs: pd.DataFrame, df_control: pd.DataFrame, sm: cm.ScalarMappable
):

    # c = df_hvxs["parallax_over_error"]

    scatter_style = {
        "HVXS": {
            "s": 10, "c": "green", "alpha": 0.6, "rasterized": True,
            "marker": "x"
            # "cmap": sm.cmap, "norm": sm.norm, "ec": "k"
        },
        "Control": {
            "s": 0.01, "c": "k", "alpha": 0.4, "rasterized": True
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
            ax.scatter(x, y, **scatter_style[key])
        else:
            ax.scatter(x, y, **scatter_style[key])

    ax.axhline(y=200, ls=":", color="k")


def add_top_hist(
        ax_top: plt.Axes, df_hvxs: pd.DataFrame, df_control: pd.DataFrame
) -> None:
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
        "HVXS": "green",
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


def add_right_panel(
        ax_right: plt.Axes, fig: plt.Figure,
        df_hvxs: pd.DataFrame, df_control: pd.DataFrame, sm: cm.ScalarMappable
) -> None:

    df_dict = {
        "HVXS": df_hvxs,
        "Control": df_control
    }

    # c = df_hvxs["parallax_over_error"].values

    scatter_style = {
        "HVXS": {
            "s": 10, "c": "green", "alpha": 0.8, "rasterized": True,
            "marker": "x"
            # "cmap": sm.cmap,
            # "norm": sm.norm, "ec": "k",
        },
        "Control": {
            "s": 0.1, "c": "k", "alpha": 0.5, "rasterized": True
        }
    }

    for key, df in df_dict.items():
        x = (
            np.sqrt(2)
            * df["dist_med"].values
            * Unit("kpc") * df["astrometric_excess_noise"].values
            * 1e-3 * (1. / 3600) * (np.pi / 180.)
        ).to(Unit("AU"))

        y = df["vpec_min_med"] - df["e_vpec_min"]

        if key == "HVXS":
            ax_right.scatter(x, y, **scatter_style[key])
        else:
            ax_right.scatter(x, y, **scatter_style[key])
    ax_right.axhline(y=200, ls=":", color="k")


def add_cbar(ax: plt.Axes, fig: plt.Figure, df: pd.DataFrame,
             sm: cm.ScalarMappable) -> None:

    cax = ax.inset_axes([0.025, 0.15, 0.95, 0.2])
    _cbar = fig.colorbar(sm, cax=cax, orientation="horizontal")
    _cbar.set_label(
        r"$|\varpi|/\sigma_\varpi$", labelpad=10, size=20
    )
    _cbar.ax.xaxis.set_label_position("top")

    _cbar.ax.set_xscale('log')

    _cbar.set_ticks([0.001, 0.01, 0.1, 1, 10])
    _cbar.set_ticklabels(
        [
            "0.001", "0.01", "0.1", "1", "10"
        ], size=18
    )

    _cbar.ax.xaxis.set_minor_locator(
        LogLocator(base=10.0, subs=np.arange(0.1, 1, 0.1), numticks=12)
    )
    # _cbar.ax.xaxis.set_minor_formatter(
    #     FormatStrFormatter("%.1f")
    # )  # Optional: Format minor tick labels


def add_legend(axs: dict[plt.Axes], handles: list, labels: list) -> None:
    handle_HVXS = Line2D([0], [0], marker="x", color="green", ms=10,
                         ls="none", mew=2.0)
    labels_HVXS = "HVXS"

    handles.insert(0, handle_HVXS)
    labels.insert(0, labels_HVXS)

    axs["cbar"].legend(
        handles, labels, loc="upper left", bbox_to_anchor=(0, 1.0),
        ncols=3, handletextpad=0.01, columnspacing=0.6, borderaxespad=0.0,
        fontsize=20, frameon=False
    )


def make_plot() -> None:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources" / "hvxs_vpec_lo_gt_200.csv"
    )
    df_hvxs = pd.read_csv(in_file)
    df_gold = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR / "prime_sample"
        / "gold_sample_150525_curated_sorted_by_ra.csv"
    )
    df_control = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "control_sample" / "control_sample_stage_10.csv"
    )

    df_hvxs["parallax_over_error"] = (
        abs(df_hvxs["parallax_corr"]) / df_hvxs["parallax_error"]
    )

    poe = df_hvxs["parallax_over_error"]
    sm_lognorm = cm.ScalarMappable(norm=LogNorm(
        vmin=poe.min(), vmax=poe.max()), cmap=ps.CMAP
    )

    fig, ax_dict = make_figure()
    axes_settings(ax_dict)

    add_control_and_hvxs(
        df_hvxs=df_hvxs, df_control=df_control, ax=ax_dict["main"], fig=fig,
        sm=sm_lognorm
    )

    add_right_panel(
        ax_dict["right"], fig, df_hvxs=df_hvxs, df_control=df_control,
        sm=sm_lognorm
    )

    # add_cbar(ax=ax_dict["cbar"], df=df_hvxs, fig=fig, sm=sm_lognorm)

    add_top_hist(
        ax_dict["top"], df_hvxs=df_hvxs, df_control=df_control
    )

    handles, labels = add_prime_sources(df_prime=df_gold, axs=ax_dict)

    add_legend(axs=ax_dict, handles=handles, labels=labels)

    plt.savefig(
        config.RESULTS_FIGURES_DIR
        / "dist_vs_vpec"
        / "dist_vs_vpec_min_lolim.pdf"
    )


def main() -> None:
    make_plot()


if __name__ == "__main__":
    main()
