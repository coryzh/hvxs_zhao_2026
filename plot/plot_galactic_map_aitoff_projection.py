import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from typing import Tuple, Any
from plot_settings import (
    SCATTER_DICT_GALACTIC_MAP, generate_marker_styles
)
import config
from utils import process_string
from matplotlib.lines import Line2D
from matplotlib import colors


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


def add_control(ax: plt.Axes) -> None:
    df_all = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "ready_catalogues" / "control.csv"
    )
    # _filter = df_all["dist_med"] < 1.5
    # df_all = df_all[_filter]
    l, b = calc_galactic_coordinates(df_all)
    # ax.scatter(l, b, s=0.1, marker="o", color="k", alpha=0.6, rasterized=False)
    h, xedges, yedges = np.histogram2d(l, b, bins=100, density=True)
    x_centers = 0.5 * (xedges[:-1] + xedges[1:])
    y_centers = 0.5 * (yedges[:-1] + yedges[1:])
    x, y = np.meshgrid(x_centers, y_centers)

    _ = ax.pcolormesh(
        x, y, h.T, shading="auto", cmap="Greys", edgecolors="face", 
        norm=colors.PowerNorm(gamma=0.5), rasterized=True
    )


def add_hvxs(df: pd.DataFrame, ax: plt.Axes) -> None:
    l, b = calc_galactic_coordinates(df)
    ax.scatter(
        l, b, label="HVXS", rasterized=False, **SCATTER_DICT_GALACTIC_MAP
    )


def add_gold(ax: plt.Axes) -> Any:
    in_file_gold = (
        config.RESULTS_CATALOGUE_DIR / "ready_catalogues"
        / "gold.csv"
    )
    df = pd.read_csv(in_file_gold)
    marker_styles = generate_marker_styles(df.shape[0], generate_for="scatter")

    l, b = calc_galactic_coordinates(df)
    for i, row in df.iterrows():
        name = process_string.get_short_id(row["ID_x"])
        print(i, name, l[i], b[i])
        ax.scatter(
            l[i], b[i], label=rf'{name}', zorder=2, lw=2, s=160, ec="k",
            **marker_styles[i]
        )
    handles, labels = ax.get_legend_handles_labels()
    return handles, labels


def make_galactic_map() -> None:
    fig, ax = setup_axes()
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "ready_catalogues"
        / "hvxs.csv"
    )
    df = pd.read_csv(in_file)

    add_control(ax)
    add_hvxs(df, ax)
    handles, labels = add_gold(ax)

    handle_HVXS = Line2D([0], [0], marker="x", color="green", ms=10,
                         ls="none", mew=2)
    handles[0] = handle_HVXS
    plt.legend(
        handles, labels,
        bbox_to_anchor=[0.5, -0.05], loc="upper center", ncols=5
    )

    out_file = (
        config.RESULTS_FIGURES_DIR
        / "galactic_map" / "galactic_map.pdf"
    )

    if not out_file.parent.exists():
        out_file.parent.mkdir()

    plt.savefig(out_file)


def main() -> None:
    make_galactic_map()


if __name__ == "__main__":
    main()
