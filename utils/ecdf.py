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


def plot_ecdf(arr: np.ndarray, ax: plt.Axes, normalised: bool = True, **kwargs) -> None:
    x, y = get_ecdf(arr, normalised=normalised)

    ax.step(x, y, where="post", **kwargs)
