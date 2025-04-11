import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

SURVEY_KEYS = ["csc", "xmm", "swift", "erass"]

SURVEY_NAMES = ["CSC", "4XMM", "2SXPS", "eRASS"]

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
    's': 12, 'fc': 'r', 'ec': 'k', 'marker': 'o', "alpha": 0.2
}

SCATTER_DICT_CMD = {
    's': 12, 'fc': 'r', 'ec': 'k', 'marker': 'o', "alpha": 0.2,
    'rasterized': True
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
