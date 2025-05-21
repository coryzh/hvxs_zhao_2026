import seaborn as sns
import config
from matplotlib.colors import LinearSegmentedColormap
from itertools import product


IMAGE_DIR = config.DATA_DIR / "images" / "gold_sample"

SURVEY_KEYS = [
    "csc", "xmm", "swift", "erass", "panstarrs", "desi", "skymapper"
]

SURVEY_NAMES = [
    "CSC", "4XMM", "2SXPS", "eRASS", "PanSTARRS DR1", "DESI-DR10", "SkyMapper"
]

cblind_palette = sns.color_palette("colorblind", 5)

SURVEY_COLORS = [cblind_palette[i] for i in [0, 2, 3, 4]]

SURVEY_COLOR_DICT = {key: val for key, val in zip(SURVEY_KEYS, SURVEY_COLORS)}

SURVEY_NAME_DICT = {key: val for key, val in zip(SURVEY_KEYS, SURVEY_NAMES)}

DIST_INFERENCE_KEYS = ["exp_model", "simple_inversion"]

DIST_INFERENCE_COLORS = sns.color_palette(
    "colorblind", len(DIST_INFERENCE_KEYS)
)

DIST_INFERENCE_COLOR_DICT = {
    key: color
    for key, color in zip(
        DIST_INFERENCE_KEYS, DIST_INFERENCE_COLORS
    )
}

DIST_INFERENCE_LINESTYLE_DICT = {
    key: ls
    for key, ls in zip(
        DIST_INFERENCE_KEYS, ["-", ":"]
    )
}

BINNING_PARAM_LABEL_AXISLABELS = [
    r"$d$ (kpc)", r"$v_\mathrm{pec, min, lo}\,\mathrm{(km~s^{-1})}$"
]

BINNING_PARAM_LABEL_KEYS = ["dist_med", "vpec_min_lo"]

BINNING_PARAM_LABEL_DICT = {
    key: color
    for key, color in zip(
        BINNING_PARAM_LABEL_KEYS, BINNING_PARAM_LABEL_AXISLABELS
    )
}

SCATTER_DICT_GALACTIC_MAP = {
    's': 15, 'fc': 'green', 'marker': 'x', "alpha": 0.3
}

SCATTER_DICT_CMD = {
    's': 12, 'fc': 'r', 'ec': 'k', 'marker': 'o', "alpha": 0.2,
    'rasterized': True
}

SCATTER_DICT_HVXS = {
    's': 10, 'fc': "g", "ec": "g", 'marker': "x", "alpha": 0.2,
    "rasterized": False
}

SCATTER_DICT_CONTROL_CMD = {
    's': 0.1, 'fc': 'k', 'ec': 'k', 'marker': '.', 'alpha': 0.3,
    'zorder': -1, 'rasterized': True
}

SCATTER_DICT_GALACTIC_MAP_ALL = {
    's': 0.01, 'fc': 'k', 'marker': '.', 'alpha': 0.9, 'rasterized': True
}

HEX_COLORS = [
    '#2F26D7', '#A344AD', '#72C3DC', '#84E296', '#FFD166', '#D72638'
]

CMAP = LinearSegmentedColormap.from_list(' ', HEX_COLORS)

PRIME_SOURCE_MARKER = ["o", "s", "D", "H", "X"]

PRIME_SOURCE_COLOR = sns.color_palette("deep", 8)

PRIME_SCATTER_MARKER_SETTINGS = {"s": 160, "ec": "k", "zorder": 5, "lw": 2}


def generate_marker_styles(n, generate_for: str = "plot"):
    """
    Generate unique marker styles and colors for plotting.

    Parameters:
    - n (int): The number of unique marker styles and colors to generate.
    - generate_for (str): The style dictionary is generate for either
    matplotlib scatter (where the marker color is controlled by fc), or plot
    object where the marker color is controlled by mfc.

    Returns:
    - dict: A dictionary with keys 'marker' and 'color', each containing a
    list of styles and colors.
    """

    if generate_for == "scatter":
        color_key = "fc"

    elif generate_for == "plot":
        color_key = "mfc"

    else:
        raise ValueError(
            "Invalid option for generate_for. Must be either 'mfc' or 'fc'."
        )

    # Available marker styles and colors
    # Not that triangular shapes are ignored here because they could be
    # sometimes confused with upper/lower limits.
    marker_styles = [
        'o', 's', 'D', 'P',
        'X'
    ]
    color_palette = sns.color_palette("hls", 4)

    # The maximum number of markers. Too many individually distinguished
    # markers might make the plot look too messy.
    max_n = len(color_palette) * len(marker_styles)
    if n > max_n:
        raise ValueError(
            f"Too many pairs to generate.The maximum is {max_n}, but got {n}."
        )

    combinations = list(product(marker_styles, color_palette))[:n]
    styles = [{'marker': m, color_key: c} for m, c in combinations]

    return styles


def main() -> None:
    test = generate_marker_styles(5, generate_for="plot")
    print(test)


if __name__ == "__main__":
    main()
