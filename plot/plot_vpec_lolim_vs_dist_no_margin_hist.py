import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import config
import plot.plot_settings as ps
from utils.process_string import get_short_id
from typing import Tuple
from plot.plot_settings import DIST_INFERENCE_COLOR_DICT


def make_figure() -> Tuple[plt.Figure, list[plt.Axes]]:
    plt.style.use("mycustomised")

    fig, ax = plt.subplots(1, 2, figsize=(16, 8))

    plt.subplots_adjust(hspace=0.1)
    return fig, ax


def axes_settings(ax: list[plt.Axes]) -> None:
    ax[0].set_xlabel(r"$d$ (kpc)")
    ax[0].set_ylabel(r"$v_\mathrm{pec, min, lo}\,(\mathrm{km~s^{-1}})$")

    ax[0].set_xscale("log")
    ax[0].set_yscale("log")

    # ax[1].set_yscale("log")
    # ax[2].set_xscale("log")

    ax[0].set_xlim(0.1, 15)
    ax[0].set_ylim(8, 1400)

    ax[0].set_xticks([0.1, 1, 10])
    ax[0].set_xticklabels(["0.1", "1", "10"])
    ax[0].set_yticks([10, 100, 1000])
    ax[0].set_yticklabels(["10", "100", "1000"])

    # ax[1].tick_params(labelleft=False, labelbottom=False)
    ax[1].set_xlim(0.0, 15)
    ax[1].set_ylim(0.8, 4e4)
    ax[1].set_xlabel(r"$d$ (kpc)")
    ax[1].set_ylabel(r"Counts")
    ax[1].set_yscale("log")

    ax[1].set_yticks([1, 10, 100, 1000, 1e4])
    ax[1].set_yticklabels(["1", "10", "100", "1000", r"$10^4$"], rotation=90)


def add_prime_sources(df_prime: pd.DataFrame, ax: list[plt.Axes]) -> None:
    ax_scatter = ax[0]

    for i, row in df_prime.iterrows():
        x = row["dist_med"]
        y = row["vpec_min_med"] - row["e_vpec_min"]
        name = get_short_id(row["ID_x"])
        ax_scatter.scatter(
            x, y, marker=ps.PRIME_SOURCE_MARKER[i],
            fc=ps.PRIME_SOURCE_COLOR[i], label=name,
            **ps.PRIME_SCATTER_MARKER_SETTINGS
        )

    legend = ax[0].legend(
        bbox_to_anchor=[0.02, 0.99], loc="upper left", fontsize=15
    )
    for handle in legend.legend_handles:
        handle.set_alpha(1.0)


def add_control_and_hvxs(df_hvxs: pd.DataFrame, ax: list[plt.Axes]) -> None:
    df_control = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "control_sample" / "control_sample_stage_9.csv"
    )
    _filter = df_control["distance_inference"] != "fixed_at_1"
    df_control = df_control[_filter]

    min_aen_val = 1e-3
    df_hvxs = df_hvxs.sort_values("astrometric_excess_noise", ascending=True)
    df_hvxs["astrometric_excess_noise"] = (
        df_hvxs["astrometric_excess_noise"]
        .replace(0, min_aen_val)
    )
    n_hvxs = df_hvxs[df_hvxs["distance_inference"] != "fixed_at_1"].shape[0]

    dist = df_hvxs["dist_med"]
    dist_bins = np.linspace(min(dist), max(dist), 60)
    # dist_bin_centres = 0.5 * (dist_bins[1:] + dist_bins[:-1])

    # c_val = df_hvxs["astrometric_excess_noise"] + min_aen_val
    # color_norm = colors.LogNorm(vmin=min_aen_val, vmax=max(c_val))
    # hist_style = {
    #     "HVXS": {"ec": "r", "lw": 2.0},
    #     "Control": {"ec": "k", "lw": 2.0}
    # }

    scatter_style = {
        "HVXS": {
            "s": 20, "ec": "k", "c": "r", "alpha": 0.5, "rasterized": True,
            "label": "HVXS"
        },
        "Control": {
            "s": 0.01, "c": "k", "alpha": 0.2, "rasterized": True,
            "label": "Control"
        }
    }

    df_dict = {
        "HVXS": df_hvxs,
        "Control": df_control
    }

    dist_hist_label_names = {
        "simple_inversion": "Direct inversion",
        "exp_model": "Bayesian method"
    }

    for key, df in df_dict.items():
        df = df[df["distance_inference"] != "fixed_at_1"]
        x = df["dist_med"]
        y = df["vpec_min_med"] - df["e_vpec_min"]
        if key == "HVXS":
            ax[0].scatter(x, y, **scatter_style[key])
        else:
            ax[0].scatter(x, y, **scatter_style[key])

    for i, (key, val) in enumerate(DIST_INFERENCE_COLOR_DICT.items()):
        df_sub = df_hvxs[df_hvxs["distance_inference"] == key]
        percentage = (df_sub.shape[0] / n_hvxs) * 100

        dist = df_sub["dist_med"]

        hist = ax[1].hist(
            dist, bins=dist_bins, histtype="stepfilled", ec="k",
            lw=2.0, alpha=0.7, label=dist_hist_label_names[key], 
            zorder=-2 + i
        )

        mode_index = np.argmax(hist[0])

        ax[1].text(
            x=dist_bins[mode_index], y=1.5, s=f"{percentage:.1f}%", color="w",
            fontsize=18, va="center", ha="left"
        )

    df_control_filtered = (
        df_control[df_control["distance_inference"] != "fixed_at_1"]
    )

    dist_control = df_control_filtered["dist_med"]
    ax[1].hist(
        dist_control, bins=dist_bins, color="k", label="Control", alpha=0.5,
        ec="k", lw=2.0, histtype="stepfilled"
    )

    ax[0].axhline(y=150, ls=":", color="k")

    plt.legend(loc="upper right", fontsize=15)

    # cax = ax[0].inset_axes(bounds=(0.08, 0.8, 0.35, 0.05))
    # _cbar = plt.colorbar(scatter, cax=cax, orientation="horizontal")
    # _cbar.set_label(r"$\epsilon$", labelpad=10)  # Set the label text
    # _cbar.ax.xaxis.set_label_position("top")
    # _cbar.ax.set_xticks([0.001, 0.1, 10])
    # _cbar.ax.set_xticklabels(["0.001", "0.1", "10"], fontsize=17)
# def add_hvxs(df: pd.DataFrame, ax: list[plt.Axes]) -> None:
#     x = df["dist_med"]
#     y = df["vpec_min_med"] - df["e_vpec_min"]
#     ax[0].scatter(x, y, s=40, marker="o", ec="k", fc="r")
#     ax[0].axhline(y=150, ls=":", color="k")


def make_plot() -> None:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources" / "combined_vpec_lolim_gt_150_unique_stage_9.csv"
    )
    df = pd.read_csv(in_file)
    df_prime = pd.read_csv(in_file.parent / f"{in_file.stem}_prime.csv")

    fig, ax = make_figure()
    axes_settings(ax)
    add_control_and_hvxs(df_hvxs=df, ax=ax)
    add_prime_sources(df_prime, ax=ax)
    plt.savefig(
        config.RESULTS_FIGURES_DIR
        / "dist_vs_vpec"
        / "vpec_lolim_gt_150_vpec_vs_dist_stage_9_no_prime.pdf"
    )


def main() -> None:
    make_plot()


if __name__ == "__main__":
    main()
