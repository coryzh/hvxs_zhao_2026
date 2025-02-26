import numpy as np


def get_errors(arr: np.ndarray, lolim_percentile: float = 16, uplim_percentile: float = 84):
    median = np.median(arr)
    lolim = np.percentile(arr, q=lolim_percentile)
    uplim = np.percentile(arr, q=uplim_percentile)

    if (lolim_percentile >= uplim_percentile) or (lolim_percentile >= 50) or (uplim_percentile <= 50):
        raise ValueError(f"Lower-limit or upper-limit percentile not valid.")

    up_error = uplim - median
    lo_error = median - lolim

    return median, lo_error, up_error
