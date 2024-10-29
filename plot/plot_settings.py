import seaborn as sns

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