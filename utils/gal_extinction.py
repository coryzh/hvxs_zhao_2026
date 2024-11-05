# ===================================================================================
# MW extinction empirical function from Jason A. Cardelli et al. (1989)
# This part will calculate a extinction correction fraction for flam
# ===================================================================================
import numpy as np
import constants
from typing import Union
R_V_mw = constants.rv
pi = np.pi


def gal_extinction(lam: Union[float, np.ndarray], e_b_v: Union[float, np.ndarray]):
    """
    This function takes a wavelength in AA and a reddening value E(B-V)
    and returns the extinction factor: f_ext = f_extinct / f_original
    """
    lam = lam * 1.0e-8
    x = (1. / lam) * 1.0e-4  # in um^-1

    # Infrared and optical:
    if 0.3 <= x <= 1.1:
        a = 0.574 * x ** 1.61
        b = -0.527 * x ** 1.61
    if 1.1 <= x <= 3.3:
        y = x - 1.82
        a = 1. + 0.17699 * y - 0.50447 * y ** 2 - 0.02427 * y ** 3 + 0.72085 * y ** 4 \
            + 0.01979 * y ** 5 - 0.77530 * y ** 6 + 0.32999 * y ** 7
        b = 1.41338 * y + 2.28305 * y ** 2 + 1.07233 * y ** 3 - 5.38434 * y ** 4 \
            - 0.62251 * y ** 5 + 5.30260 * y ** 6 - 2.09002 * y ** 7
    # FUV and UV
    if 3.3 <= x <= 8.0:
        if x < 5.9:
            fa = 0.
            fb = 0.
        if 5.9 <= x <= 8.0:
            fa = -0.04473 * (x - 5.9) ** 2 - 0.009779 * (x - 5.9) ** 3
            fb = 0.2130 * (x - 5.9) ** 2 - 0.1207 * (x - 5.9) ** 3

        a = 1.752 - 0.316 * x - 0.104 / ((x - 4.67) ** 2 + 0.341) + fa
        b = -3.090 + 1.825 * x + 1.206 / ((x - 4.62) ** 2 + 0.263) + fb

    if 8. <= x <= 10.:
        a = -1.073 - 0.628 * (x - 8.) + 0.137 * (x - 8.) ** 2 - 0.070 * (x - 8.) ** 3
        b = 13.670 + 4.257 * (x - 8.) - 0.420 * (x - 8.) ** 2 + 0.374 * (x - 8.) ** 3

    if x < 0.3 or x > 10.:
        a = 0.
        b = 0.
        # i.e. no extinction

    a_v = e_b_v * R_V_mw
    a_lam = (a + b / R_V_mw) * a_v
    # frac_pow = (-1. / 2.5) * A_lam
    # frac = 10 ** frac_pow

    return a_lam


gal_extinction_vec = np.vectorize(gal_extinction)
