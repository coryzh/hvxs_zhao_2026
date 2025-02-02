import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord
from typing import Tuple
from matplotlib import colors
# from plot_settings import (SCATTER_DICT_GALACTIC_MAP, PRIME_SOURCE_MARKER, PRIME_SOURCE_COLOR,
#                            PRIME_SCATTER_MARKER_SETTINGS)
import config
# from utils import process_string
# from plot_settings import SURVEY_COLOR_DICT


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


def calc_galactic_coordinates(df: pd.DataFrame,
                              ra_col: str = "ra_x", dec_col: str = "dec_x") -> Tuple[np.ndarray, np.ndarray]:
    # n_df = df.index

    coord = SkyCoord(df[ra_col], df[dec_col], unit="deg")

    coord_gal = coord.galactic

    l_arr = -coord_gal.l.wrap_at('180d').radian
    b_arr = coord_gal.b.radian

    return l_arr, b_arr


def add_catalog(ax: plt.Axes) -> None:
    catalogs = {"csc": "CSC 2.1", "xmm": "4XMM DR14", "swift": "2SXPS", "erass": "eRASS DE DR1"}
    cmap_dict = {"csc": "Greens", "xmm": "Reds", "swift": "Blues", "erass": "Purples"}
    pos_colname_dict = {"csc": ["ra_deg", "dec_deg"], "xmm": ["sc_ra", "sc_dec"], "swift": ["RA", "Decl"],
                        "erass": ["RA", "DEC"]}
    for key, survey_name in catalogs.items():
        in_file = config.ROOT_DIR / "results" / key / "catalogues" / "nway_match" / f"{key}_confident_point_sources.csv"
        df = pd.read_csv(in_file)
        ra_col, dec_col = pos_colname_dict[key]
        l, b = calc_galactic_coordinates(df, ra_col=ra_col, dec_col=dec_col)
        ax.scatter(l, b, s=0.01, marker="o", fc="k", ec="k", alpha=0.3, rasterized=True)
        # h, xedges, yedges = np.histogram2d(l, b, bins=40, density=True)
        # x_centers = 0.5 * (xedges[:-1] + xedges[1:])
        # y_centers = 0.5 * (yedges[:-1] + yedges[1:])
        # x, y = np.meshgrid(x_centers, y_centers)
        #
        # _c = ax.pcolormesh(x, y, h.T + 1, shading="auto", cmap=cmap_dict[key], edgecolors="face",
        #                    norm=colors.PowerNorm(0.5), alpha=0.3)


def make_galactic_map() -> None:
    fig, ax = setup_axes()
    add_catalog(ax)
    out_file = config.RESULTS_FIGURES_DIR / "galactic_map" / f"all_confident_sources.pdf"

    if not out_file.parent.exists():
        out_file.parent.mkdir()

    # legend = plt.legend(bbox_to_anchor=[0.5, -0.05], loc="upper center", ncols=5)
    # for handle in legend.legend_handles:
    #     handle.set_alpha(1.0)

    plt.savefig(out_file)


def main() -> None:
    make_galactic_map()


if __name__ == "__main__":
    main()
