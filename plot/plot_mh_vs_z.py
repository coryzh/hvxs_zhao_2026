import config
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import constants as const
import astropy.units as u
import matplotlib.gridspec as gridspec
import gdr3apcal
from computation.distance_estimate_old import estimate_distances_df
from astropy.coordinates import SkyCoord, Galactocentric
from typing import Tuple, Dict


def set_up_figure() -> Tuple[plt.Figure, Dict[str, plt.Axes]]:
    plt.style.use("mycustomised")
    fig = plt.figure(figsize=(10, 10))
    gs = gridspec.GridSpec(4, 4, figure=fig, hspace=0.05, wspace=0.05)

    ax_main = fig.add_subplot(gs[1:4, 0:3])
    ax_xhist = fig.add_subplot(gs[0, 0:3], sharex=ax_main)
    ax_yhist = fig.add_subplot(gs[1:4, 3], sharey=ax_main)
    ax_yhist.tick_params(labelleft=False, labelbottom=False)
    ax_xhist.tick_params(labelbottom=False, labelleft=False)
    ax_legend = fig.add_subplot(gs[0, 3])  # Upper right corner of the grid

    axs = {
        "main": ax_main,
        "xhist": ax_xhist,
        "yhist": ax_yhist,
        "legend": ax_legend
    }

    return fig, axs


def axes_settings(axs: Dict[str, plt.Axes]) -> None:
    ax_main = axs["main"]

    ax_main.set_ylim(0, 9)
    ax_main.set_xlim(-4, 2)

    ax_main.set_xlabel(r"$\mathrm{[M/H]}$")
    ax_main.set_ylabel(r"$|z|\,(\mathrm{kpc})$")


def add_legends(fig: plt.Figure, axs: Dict[str, plt.Axes]) -> None:
    bbox_xhist = axs["xhist"].get_position(fig)
    bbox_yhist = axs["yhist"].get_position(fig)
    ax_legend = axs["legend"]

    # Calculate width and height of the legend box to match the histogram sizes
    legend_width = bbox_yhist.width
    legend_height = bbox_xhist.height
    ax_legend.axis("off")
    # Place legend in ax_legend and use calculated bbox_to_anchor
    handles, labels = axs["main"].get_legend_handles_labels()
    _ = ax_legend.legend(
        handles, labels,
        loc="lower left",
        frameon=False,
        bbox_to_anchor=(1.0, 1.0, legend_width, legend_height),
        bbox_transform=axs["main"].transAxes,
        fontsize=18,
        labelspacing=1.8,
        borderpad=0.4
    )


def add_data(axs: Dict[str, plt.Axes]) -> None:
    ax_main = axs["main"]
    ax_xhist = axs["xhist"]
    ax_yhist = axs["yhist"]

    df_co = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR / "known_co_binaries_zp_corrected.csv"
    )

    df_hvx = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources" / "combined_vpec_lolim_gt_150_unique_stage_9.csv"
    )

    df_control = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "control_sample" / "control_sample_stage_10.csv"
    )

    dist_estimate = df_co.apply(
        estimate_distances_df, axis=1, result_type="expand"
    )

    dist_estimate.columns = [
        "dist_med", "e_dist", "E_dist", "distance_inference"
    ]

    df_co_w_dist = pd.concat([df_co, dist_estimate], axis=1)

    df_dict = {"Known": df_co_w_dist, "HVXSs": df_hvx, "Control": df_control}
    style_dict = {
        "Known": {
            "s": 50, "marker": "s", "ec": "w", "fc": "b", "zorder": 2,
            "label": "Known", "rasterized": True
        },

        "HVXSs": {
            "s": 20, "marker": "o", "ec": "w", "fc": "r",
            "label": "HVXSs", "rasterized": True
        },

        "Control": {
            "s": 0.1, "marker": ".", "c": "k", "fc": "k", "zorder": -9,
            "label": "Control", "rasterized": True
        }
    }

    gc_frame = Galactocentric(
        galcen_distance=const.R_0 * u.kpc, z_sun=25.0 * u.pc
    )

    gc_frame.representation_type = "cylindrical"

    calib = gdr3apcal.GaiaDR3_GSPPhot_cal()

    bins_x = np.linspace(
        df_control.mh_gspphot.min(), df_control.mh_gspphot.max(), 25
    )
    bins_y = np.linspace(0, 10, 25)

    for key, val in style_dict.items():
        df_indiv = df_dict[key]
        coords = SkyCoord(
            df_indiv.ra.values * u.deg, df_indiv.dec.values * u.deg,
            distance=df_indiv.dist_med.values * u.kpc, frame="icrs"
        )
        coords_gc = coords.transform_to(gc_frame)
        z = coords_gc.z.value
        y = np.abs(z)
        # coords_gal = coords.galactic
        # y = coords_gal.b.deg
        # metal = df_indiv["mh_gspphot"]
        x = calib.calibrateMetallicity(df_indiv)

        ax_main.scatter(x, y, **val)
        _ = ax_xhist.hist(
            x, bins=bins_x, density=True, histtype="step", ec=val["fc"], lw=2.0
        )
        _ = ax_yhist.hist(
            y, bins=bins_y, density=True, histtype="step", lw=2.0,
            ec=val["fc"], orientation="horizontal"
        )


def make_figure() -> None:
    fig, axs = set_up_figure()
    axes_settings(axs)
    add_data(axs)
    add_legends(fig, axs)

    out_file = config.RESULTS_FIGURES_DIR / "mh_vs_z" / "mh_vs_z.pdf"

    plt.savefig(out_file)


if __name__ == "__main__":
    make_figure()
