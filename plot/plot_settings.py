import seaborn as sns
from matplotlib.colors import LinearSegmentedColormap

SURVEY_KEYS = ["csc", "xmm", "swift", "erass"]
SURVEY_NAMES = ["CSC", "4XMM", "2SXPS", "eRASS"]
SURVEY_COLORS = sns.color_palette("colorblind", len(SURVEY_KEYS))
SURVEY_COLOR_DICT = {key: val for key, val in zip(SURVEY_KEYS, SURVEY_COLORS)}
SURVEY_NAME_DICT = {key: val for key, val in zip(SURVEY_KEYS, SURVEY_NAMES)}

DIST_INFERENCE_KEYS = ["exp_model", "simple_inversion"]
DIST_INFERENCE_COLORS = sns.color_palette("colorblind", len(DIST_INFERENCE_KEYS))
DIST_INFERENCE_COLOR_DICT = {key: color for key, color in zip(DIST_INFERENCE_KEYS, DIST_INFERENCE_COLORS)}

BINNING_PARAM_LABEL_AXISLABELS = [r"$d$ (kpc)", r"$v_\mathrm{pec, min, lo}\,\mathrm{(km~s^{-1})}$"]
BINNING_PARAM_LABEL_KEYS = ["dist_med", "vpec_min_lo"]
BINNING_PARAM_LABEL_DICT = {key: color for key, color in zip(BINNING_PARAM_LABEL_KEYS, BINNING_PARAM_LABEL_AXISLABELS)}

SCATTER_DICT_GALACTIC_MAP = {'s': 12, 'fc': 'r', 'ec': 'k', 'marker': 'o', "alpha": 0.2}
SCATTER_DICT_CMD = {'s': 12, 'fc': 'r', 'ec': 'k', 'marker': 'o', "alpha": 0.2}
SCATTER_DICT_GALACTIC_MAP_ALL = {'s': 0.01, 'fc': 'k', 'marker': '.', 'alpha': 0.9, 'rasterized': True}

HEX_COLORS = ['#2F26D7', '#A344AD', '#72C3DC', '#84E296', '#FFD166', '#D72638']
CMAP = LinearSegmentedColormap.from_list(' ', HEX_COLORS)
