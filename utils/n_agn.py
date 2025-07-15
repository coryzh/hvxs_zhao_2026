import numpy as np
from typing import Union

FloatOrVector = Union[float, np.ndarray]

s_b_f = 1.24e-14
s_b_b = 4.09e-14
gamma_b = 2.69
gamma_i = 2.40
gamma_f = 0.96
K = 60.2


def density_agn(s: FloatOrVector) -> FloatOrVector:
    if s <= s_b_f:
        gamma = gamma_f
        norm = K / (s_b_f ** (1 - gamma))

    elif s <= s_b_b:
        gamma = gamma_i
        norm = K / (s_b_b ** (1 - gamma))

    else:
        gamma = gamma_b
        norm = K / (s_b_b ** (1 - gamma))

    return norm * s ** (1 - gamma)


density_agn_vec = np.vectorize(density_agn)


def n_agn(s: float) -> float:
    term_1 = (
        (K / s_b_f ** (1 - gamma_f))
        * (1 / (1 - gamma_f)) * (s_b_f ** (1 - gamma_f) - s ** (1 - gamma_f))
    )
    term_2 = (
        (K / s_b_b ** (1 - gamma_i))
        * (1 / (1 - gamma_i))
        * (s_b_b ** (1 - gamma_i) - s_b_f ** (1 - gamma_i))
    )
    term_3 = (
        -(K / s_b_b ** (1 - gamma_b))
        * (1 / (1 - gamma_b)) * s_b_b ** (1 - gamma_b)
    )

    return (term_1 + term_2 + term_3) / ((s / 1e-14) ** 1.5)


def n_agn_r(s: float, r: float) -> float:
    """
    Number of AGNs as a function of flux limit and radial offset
    Parameters
    ----------
    s : float
    Flux limit in cgs unit (erg/s/cm^2)

    r : float
    Angular offset from the cluster centre in units of arcmin.

    Returns
    -------
    N_agn: Cumulative number of AGNs at the given radial offset.

    """
    area = (
        2 * np.pi * (1 - np.cos((r / 60) * (np.pi / 180))) * (180 / np.pi) ** 2
    )

    return n_agn(s) * area


def prob_agn(s: float, r: float) -> float:
    """
    Compute the Poisson probability that a given X-ray source at a given
    radial offset is an AGN based on the
    estimated number of AGNs within that radial offset.

    s : float
    Flux limit in cgs unit (erg/s/cm^2)

    r : float
    Angular offset from the cluster centre in units of arcmin.

    Returns
    -------
    p_agn : float

    Poisson probability.
    """
    p_agn = 1 - np.exp(-n_agn_r(s, r))
    # return poisson.pmf(k=1, mu=n_agn_r(s, r))
    return p_agn
