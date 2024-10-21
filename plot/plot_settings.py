import seaborn as sns

SURVEY_KEYS = ["csc", "xmm", "swift", "erass"]
SURVEY_NAMES = ["CSC", "4XMM", "2SXPS", "eRASS"]
SURVEY_COLORS = sns.color_palette("colorblind", len(SURVEY_KEYS))
SURVEY_COLOR_DICT = {key: val for key, val in zip(SURVEY_KEYS, SURVEY_COLORS)}
SURVEY_NAME_DICT = {key: val for key, val in zip(SURVEY_KEYS, SURVEY_NAMES)}
