import argparse
from pathlib import Path
from typing import Tuple

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import config


def make_figure() -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("modernstix2")
    fig, ax = plt.subplots(figsize=(10, 10))

    ax.set_xlabel(r"BP$-$RP")
    ax.set_ylabel(r"$M_G$")

    return fig, ax


def add_background_points(ax: plt.Axes) -> None:
    catalog_path = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "combined_xray_gaia_catalogue.csv"
    )

    df = pd.read_csv(catalog_path)
    df = df.query(
        "parallax / parallax_error >= 5 and 1 / parallax <= 1.0"
    )

    if df.shape[0] > 50000:
        df = df.sample(n=50000, random_state=42)

    g_abs = (
        df["phot_g_mean_mag"]
        - 5.0 * np.log10(1.0 / df["parallax"])
        - 10.0
    )

    ax.scatter(
        df["bp_rp"],
        g_abs,
        s=0.1,
        color="k",
        alpha=0.1,
        rasterized=True,
    )

    # ax.hexbin(
    #     df["bp_rp"],
    #     g_abs,
    #     gridsize=100,
    #     cmap="Blues",
    #     mincnt=1,
    #     alpha=0.5,
    #     linewidths=0.2,
    #     label=r"$\varpi/\sigma_\varpi\geq 5$ and $1/\varpi \leq 1$ kpc"
    # )


def add_targets(target_path: Path, ax: plt.Axes) -> None:
    df = pd.read_csv(target_path)
    g_abs = (
        df["phot_g_mean_mag"]
        - 5.0 * np.log10(1.0 / df["parallax"])
        - 10.0
    )

    ax.scatter(
        df["bp_rp"],
        g_abs,
        s=80,
        fc="#3db434",
        ec="k",
    )


def set_axes(ax: plt.Axes) -> None:
    ax.set_xlim(-1.2, 4.2)
    ax.set_ylim(15.5, -5.5)


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Plot BP-RP versus absolute Gaia G magnitude for selected "
            "targets."
        )
    )
    parser.add_argument(
        "--targets",
        type=Path,
        default=None,
        help="Path to the CSV file containing the target data.",
    )
    parser.add_argument(
        "--out_path",
        type=Path,
        default=None,
        help="Optional output path for saving the figure."
    )

    args = parser.parse_args()

    fig, ax = make_figure()
    add_background_points(ax)

    if args.targets is not None:
        add_targets(args.targets, ax)

    set_axes(ax)
    ax.legend(loc="best")

    if args.out_path is not None:
        fig.savefig(args.out_path, bbox_inches="tight")
    else:
        plt.show()


if __name__ == "__main__":
    main()
