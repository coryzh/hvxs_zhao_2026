from galpy.potential import calcRotcurve, \
    PowerSphericalPotentialwCutoff, MiyamotoNagaiPotential, NFWPotential
from galpy.util import conversion
from scipy.interpolate import interp1d
import constants as con
import astropy.units as u
import numpy as np
from numba import jit

# This python script extract rotation curve data from the galpy MWPotential2014

ro = con.R_0
vo = con.Theta_0


def calc_v_rot(R):
    psp = PowerSphericalPotentialwCutoff(
        alpha=1.8, rc=1.9 / 8., normalize=0.05, ro=ro, vo=vo
    )
    myp = MiyamotoNagaiPotential(
        a=3. / 8., b=0.28 / 8., normalize=.6, ro=ro, vo=vo
    )
    nfw = NFWPotential(
        a=16 / 8., normalize=.35, ro=ro, vo=vo
    )
    mw = psp + myp + nfw

    v_rot_galpy = (
        calcRotcurve(mw, Rs=R * u.kpc)
        * conversion.velocity_in_kpcGyr(240, 8.34)
        * (u.kpc / u.Gyr).to(u.km / u.s)
    )

    return v_rot_galpy


r_grid = np.arange(0.00, 100, 0.01)
v_grid = np.zeros(len(r_grid))

for i, r_val in enumerate(r_grid):
    if r_val < 0.01:
        v_grid[i] = calc_v_rot([0.01])[0]
    else:
        v_grid[i] = calc_v_rot([r_val])[0]


@jit(nopython=True)
def v_rot_nearest(x):
    x = np.asarray(x)

    idx = np.abs(x[:, np.newaxis] - r_grid).argmin(axis=1)

    return v_grid[idx]


v_rot = interp1d(r_grid, v_grid, bounds_error=False, fill_value=v_grid[-1])
