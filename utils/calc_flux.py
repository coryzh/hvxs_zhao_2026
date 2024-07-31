import astropy.units as u
import numpy as np
from typing import Union


# Constants
ZP_VEG = 25.6874
C_LAMBDA = 1.346109e-21
OPTICAL_WAVELENGTH_RANGE = (750 - 380) * u.nm


def calculate_optical_flux(g_mag: Union[float, np.ndarray]) -> Union[float, np.ndarray, u.Quantity]:
    """
    Calculate the optical flux from the G band magnitude.
    Parameters
    ----------
    g_mag : Union[float, np.ndarray]
        The G band magnitude, could be a single value or a np.array.

    Returns
    -------
    flux_opt : Union[float, np.ndarray]
        The optical flux in unit of erg/s/cm^2, which will have the same shape as g_mag.
    """

    flux_e = 10 ** (-0.4 * (g_mag - ZP_VEG))  # mean flux in G band in unit of photon e-/s
    flux_lambda = flux_e * C_LAMBDA * (u.Watt / (u.m ** 2 * u.nm))
    flux_optical = (flux_lambda * OPTICAL_WAVELENGTH_RANGE).to(u.erg / (u.s * u.cm ** 2))

    return flux_optical
