from astropy.io import fits
from astropy.wcs import WCS
import matplotlib.pyplot as plt
import warnings
from typing import Tuple


def get_wcs(hdu: fits.PrimaryHDU) -> WCS:
    header = hdu.header
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        wcs = WCS(header)

    return wcs


def set_figure(wcs: WCS, figsize: tuple[float, float] = (10, 10)) -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("mycustomised")
    fig = plt.figure(figsize=figsize)
    ax = fig.add_subplot(111, projection=wcs)

    return fig, ax


def set_axis(ax: plt.Axes) -> None:
    ax.set_xlabel(r"$\alpha$ (ICRS)")
    ax.set_ylabel(r"$\delta$ (ICRS)")
