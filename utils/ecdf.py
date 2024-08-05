import numpy as np
import matplotlib.pyplot as plt
from typing import Tuple


def get_ecdf(arr: np.ndarray, normalised: bool = True) -> Tuple[np.ndarray, np.ndarray]:
    x = np.sort(arr)
    y = np.arange(0, len(x) + 1)

    if normalised:
        y = y / float(len(x))

    x_new = np.insert(x, obj=0, values=0)
    return x_new, y


def plot_ecdf(arr: np.ndarray, ax: plt.Axes, bounds: Tuple[np.ndarray, np.ndarray] = None, normalised: bool = True, **kwargs) -> None:
    x, y = get_ecdf(arr, normalised=normalised)
    if bounds:
        arr_lo, arr_up = bounds
        x_lo, y_lo = get_ecdf(arr_lo, normalised=normalised)
        x_up, y_up = get_ecdf(arr_up, normalised=normalised)

        ax.step(x, y, where="post", lw=1.5, **kwargs)
        ax.step(x_lo, y_lo, where="post", lw=1.0, ls=":")
        ax.step(x_up, y_up, where="post", lw=1.0, ls=":")
        # ax.fill_betweenx(y, x_lo, x_up, step="post", alpha=0.5)

    else:
        ax.step(x, y, where="post", **kwargs)
