import astropy.constants as const
import numpy as np
import astropy.units as u
from dataclasses import dataclass
from astropy.coordinates import SkyCoord
from astropy.units import Quantity

# Constants
# 1. Some units and constants
pi = np.pi
kpc = const.kpc.cgs.value  # parsec in cgs value
yr = 365 * 24 * 3600  # time in a year in seconds
rv = 3.1  # ratio of total to selected extinction

# 2. Coordinates of the NGP (Reid+09)
alpha_NGP = '12:51:26.2817'
delta_NGP = '27:07:42.013'
coord_NGP = SkyCoord(alpha_NGP, delta_NGP, frame='icrs', unit=(u.hourangle, u.deg))
ra_P, dec_P = coord_NGP.ra.rad, coord_NGP.dec.rad  # NGP ra and dec in radian
theta = (122.932 * u.deg).to(u.rad).value

# 3. Solar motion constants (Reid+14)
U_sun, dU_sun = 10.7, 1.8
V_sun, dV_sun = 15.6, 6.8
W_sun, dW_sun = 8.9, 0.9

# 4. Rotation speed of the LSR (km/s)
Theta_0, dTheta_0 = 240.0, 8  # Galactic rotation
R_0, dR_0 = 8.34, 0.16  # distance to the GC (in kpc)

L = 1.97
# Minimum distance (in kpc) used for plotting and inferring parallaxes.
minimum_d = 1e-3


# For integrating Galactic orbits
class Galacticorbitintegrationconstants:
    time_grid: np.ndarray[Quantity] = np.linspace(0, -1, 1001) * u.Gyr
    n_rand: int = 1000


@dataclass()
class GalacticConstants:
    U: float = U_sun
    dU: float = dU_sun
    V: float = V_sun
    dV: float = dV_sun
    W: float = W_sun
    dW: float = dW_sun
    R0: float = R_0
    dR0: float = dR_0
    Theta0: float = Theta_0
    dTheta0: float = dTheta_0

    @staticmethod
    def __random_samples(x, dx, n_rand):
        return np.random.normal(x, dx, n_rand)

    @classmethod
    def get_random_samples(cls, n_rand: int = 10000):
        return (
            cls.__random_samples(cls.U, cls.dU, n_rand),
            cls.__random_samples(cls.V, cls.dV, n_rand),
            cls.__random_samples(cls.W, cls.dW, n_rand),
            cls.__random_samples(cls.R0, cls.dR0, n_rand),
            cls.__random_samples(cls.Theta0, cls.dTheta0, n_rand),
        )