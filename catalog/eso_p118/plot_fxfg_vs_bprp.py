import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import config
import argparse
from typing import Tuple
from pathlib import Path


def make_figure() -> Tuple[plt.Figure, plt.Axes]:
    """
    Create a figure and axes for plotting.

    Returns:
        Tuple[plt.Figure, plt.Axes]: The created figure and axes.
    """
    plt.style.use("modernstix2")
    fig, ax = plt.subplots(figsize=(10, 10))

    ax.set_xlabel(r"BP$-$RP")
    ax.set_ylabel(r"$F_X/F_G$")

    ax.set_yscale("log")

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

    ax.scatter(
        df["bp_rp"], df["fx_fg"], s=0.1, color="k", alpha=0.1, rasterized=True
    )


def add_targets(target_path: Path, ax: plt.Axes) -> None:
    df = pd.read_csv(target_path)

    ax.scatter(
        df["bp_rp"], df["fx_fg"], s=80, fc="#3db434", ec="k"
    )


def add_r24_relation(ax: plt.Axes) -> None:
    bp_rp_grid = np.linspace(-1.2, 4.8, 10)
    fxfg_grid = 10 ** (bp_rp_grid - 3.5)

    ax.plot(
        bp_rp_grid,
        fxfg_grid,
        color="r",
        linestyle="--",
        label="Rodriguez 2024",
    )

    ax.set_xlim(-1.2, 4.1)
    ax.set_ylim(7e-7, 8)


def set_axes(ax: plt.Axes) -> None:
    ax.set_yticks([1e-6, 1e-5, 1e-4, 1e-3, 1e-2, 1e-1, 1])
    ax.set_yticklabels(
        [
            r"$10^{-6}$", r"$10^{-5}$", r"$10^{-4}$",
            r"$0.001$", r"$0.01$", r"$0.1$", r"$1$"
        ]
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Plot FX/FG vs BP-RP for the master catalogue and "
            "selected targets."
        )
    )
    parser.add_argument(
        "--targets",
        type=Path,
        default=None,
        help="Path to the CSV file containing the target data."
    )
    parser.add_argument(
        "--out_path",
        type=Path,
        default=None,
        help="Optional output path for saving the figure."
    )

    args = parser.parse_args()

    fig, ax = make_figure()
    add_r24_relation(ax)
    add_background_points(ax)
    set_axes(ax)

    if args.targets is not None:
        add_targets(args.targets, ax)

    if args.out_path is not None:
        fig.savefig(args.out_path, bbox_inches="tight")

    plt.show()


if __name__ == "__main__":
    main()
