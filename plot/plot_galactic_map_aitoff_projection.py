import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from typing import Tuple
from plot_settings import (
    SCATTER_DICT_GALACTIC_MAP, PRIME_SOURCE_MARKER, PRIME_SOURCE_COLOR,
    PRIME_SCATTER_MARKER_SETTINGS
)
import config
from utils import process_string


def setup_axes() -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("mycustomised")
    fig = plt.figure(figsize=(19, 16))
    ax = plt.subplot(111, projection='aitoff')
    ax.grid(True)

    x_ticks = (np.linspace(150, -150, 11) * u.deg).to(u.radian).value
    x_tick_range = [str(item) for item in np.linspace(-150, 150, 11)]
    x_tick_labels = [fr"${item.split('.')[0]}^\circ$" for item in x_tick_range]

    y_ticks = (np.linspace(-75, 75, 11) * u.deg).to(u.radian).value
    y_tick_range = [str(item) for item in np.linspace(-75, 75, 11)]
    y_tick_labels = [fr"${item.split('.')[0]}^\circ$" for item in y_tick_range]

    ax.set_xticks(x_ticks)
    ax.set_xticklabels(x_tick_labels)
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_tick_labels)

    return fig, ax


def calc_galactic_coordinates(
        df: pd.DataFrame
) -> Tuple[np.ndarray, np.ndarray]:
    coord = SkyCoord(df["ra_x"], df["dec_x"], unit="deg")

    coord_gal = coord.galactic

    l_arr = -coord_gal.l.wrap_at('180d').radian
    b_arr = coord_gal.b.radian

    return l_arr, b_arr


def background_histogram(ax: plt.Axes) -> None:
    df_all = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "control_sample" / "control_sample_stage_10.csv"
    )
    _filter = df_all["dist_med"] < 1.5
    df_all = df_all[_filter]
    l, b = calc_galactic_coordinates(df_all)
    h, xedges, yedges = np.histogram2d(l, b, bins=60, density=True)
    x_centers = 0.5 * (xedges[:-1] + xedges[1:])
    y_centers = 0.5 * (yedges[:-1] + yedges[1:])
    x, y = np.meshgrid(x_centers, y_centers)

    _ = ax.pcolormesh(
        x, y, h.T, shading="auto", cmap="Greens", edgecolors="face"
    )


def add_sources(df: pd.DataFrame, ax: plt.Axes) -> None:
    l, b = calc_galactic_coordinates(df)
    ax.scatter(l, b, label="HVXS", **SCATTER_DICT_GALACTIC_MAP)


def add_prime_sources(df: pd.DataFrame, ax: plt.Axes) -> None:
    l, b = calc_galactic_coordinates(df)
    for i, row in df.iterrows():
        name = process_string.get_short_id(row["ID_x"])
        print(name)
        ax.scatter(
            l[i], b[i], marker=PRIME_SOURCE_MARKER[i],
            fc=PRIME_SOURCE_COLOR[i], label=rf'{name}',
            **PRIME_SCATTER_MARKER_SETTINGS
        )


def make_galactic_map() -> None:
    fig, ax = setup_axes()
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources" / "combined_vpec_lolim_gt_150_unique_stage_9.csv"
    )
    df = pd.read_csv(in_file)

    df_prime = pd.read_csv(in_file.parent / f"{in_file.stem}_prime.csv")
    background_histogram(ax)
    add_sources(df, ax)
    add_prime_sources(df_prime, ax)

    out_file = (
        config.RESULTS_FIGURES_DIR
        / "galactic_map" / f"{in_file.stem}_gal_map_no_prime.pdf"
    )

    if not out_file.parent.exists():
        out_file.parent.mkdir()

    legend = plt.legend(
        bbox_to_anchor=[0.5, -0.05], loc="upper center", ncols=5
    )
    for handle in legend.legend_handles:
        handle.set_alpha(1.0)

    plt.savefig(out_file)


def main() -> None:
    make_galactic_map()


if __name__ == "__main__":
    main()
