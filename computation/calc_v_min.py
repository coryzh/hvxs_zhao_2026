"""
This is a remake for the script used to find the minimum space velocity. The related function for coordinate conversion
and kinematics are all included in this script. The functions are also re-worked to be compatible with numba.
"""
import config
import numpy as np
import pandas as pd
import constants as con
from utils.distances import ExponentialPriorModel, SimpleInversion
from typing import Any, Tuple
from scipy.optimize import minimize
from utils.rotation_curve import v_rot
from numba import jit
from tqdm import tqdm

# Rotation velocity curve. Gridded values used for numpy.interp
print("Initializing ...\n")

print("1. Importing Galactic potential and performing pre-computation of Galactic rotation curve ...\n")
r_grid = np.arange(0, 150, 0.01)
v_rot_val = v_rot(r_grid)

# Constants
print("2. Importing Galactic and solar constants ...\n")
U_sun = con.U_sun
V_sun = con.V_sun
W_sun = con.W_sun
Theta_0 = con.Theta_0
R_0 = con.R_0
nrand = 1000

# Random state
print("3. Setting random state ...\n")
random_seed: int = 114514
np.random.seed(random_seed)


@jit(nopython=True)
def convert_to_galactic(ra, dec):
    """
    This function convert equatorial coordinates to Galactic coordinates. The input ra and dec should be in unit
    of degrees, and the function returns Galactic longitudes and latitudes in degrees.
    """
    ra = np.array(ra)
    dec = np.array(dec)

    # Source coordinates to radian
    conv = 3.14 / 180
    ra_rad, dec_rad = ra * conv, dec * conv  # source ra and dec in radians

    # This part compute the Galactic coordinates of the source
    sinb = np.sin(dec_rad) * np.sin(con.dec_P) + np.cos(dec_rad) * np.cos(ra_rad - con.ra_P) * np.cos(con.dec_P)
    gal_b = np.arcsin(sinb)  # Galactic latitude from -90 deg to 90 deg, this is the default range of np.arcsin()

    # phi is an angle defined to calculate Galactic longitude
    sinphi = (1 / np.cos(gal_b)) * (-np.cos(dec_rad) * np.cos(ra_rad - con.ra_P) * np.sin(con.dec_P)
                                    + np.sin(dec_rad) * np.cos(con.dec_P))

    cosphi = (1 / np.cos(gal_b)) * np.cos(dec_rad) * np.sin(ra_rad - con.ra_P)

    # math.atan2 function can handle the sign, the result is between -pi and pi
    # to convert negative angle to positive angle, add 2 * pi
    phi = np.arctan2(sinphi, cosphi) + 2 * np.pi

    gal_lon = phi + (con.theta - con.pi / 2)
    gal_lon = gal_lon % (2 * con.pi)  # this is to wrap the angle at 2pi or 360 degree.

    l_deg = gal_lon / conv
    b_deg = gal_b / conv  # convert to degree

    return l_deg, b_deg


@jit(nopython=True)
def galactic_proper_motion(ra, dec, mu_ra_cosdec, mu_dec, dt=1.0):
    """
    This function calculate differences in ra and dec due to PM and convert it to Galactic coordinate.
    Input ra and dec should be in degrees.
    Input equatorial PMs should be in units of mas/yr; note that mu_ra_cosdec contain the cos(dec) factor.
    Input timestep should be in unit of years (default is 1).
    Return: mu_l=dl/dt, mu_b=db/dt in mas/yr
    """

    mu_ra_cosdec = np.array(mu_ra_cosdec)
    mu_dec = np.array(mu_dec)

    # Compute differences in ra and dec (in degrees)
    dra = mu_ra_cosdec / (np.cos(dec * con.pi / 180)) * dt
    ddec = mu_dec * dt

    conv = 1e-3 * (1 / 3600)  # conversion factor from mas to degree

    dra *= conv
    ddec *= conv

    # Then, apply the differences to the equatorial coordinates
    ra_new = ra + dra
    dec_new = dec + ddec

    l_old, b_old = convert_to_galactic(ra, dec)
    l_new, b_new = convert_to_galactic(ra_new, dec_new)

    dl = l_new - l_old
    db = b_new - b_old

    mu_l = dl / dt  # in degree/yr
    mu_b = db / dt

    mu_l /= conv
    mu_b /= conv

    return mu_l, mu_b


@jit(nopython=True)
def galactocentric_cartesian_velocity(ra, dec, pmra, pmdec, dist, v_r):
    # Constants
    conv = (3.14 / 180)
    conv1 = 3600 * 1e3

    # Source distance
    conv_kpc_to_cm = 3.086e+21
    D_cgs = dist * conv_kpc_to_cm

    # Galactic coordinates:
    l, b = convert_to_galactic(ra, dec)
    b *= conv  # convert to radian
    l *= conv

    # PMs in Galactic coordinate
    mu_l, mu_b = galactic_proper_motion(ra, dec, pmra, pmdec, dt=0.1)

    # Physical velocities
    conv_yr_to_s = 3.1536e7
    v_b = D_cgs * (mu_b / conv1) * conv * (1e-5 / conv_yr_to_s)  # in km/s
    v_l = D_cgs * (mu_l / conv1) * np.cos(b) * conv * (1e-5 / conv_yr_to_s)  # in km/s

    # Convert the spherical coordinate to Galactic Cartesian coordinates at the location of the Sun
    U_1 = (v_r * np.cos(b) - v_b * np.sin(b)) * np.cos(l) - v_l * np.sin(l)
    V_1 = (v_r * np.cos(b) - v_b * np.sin(b)) * np.sin(l) + v_l * np.cos(l)
    W_1 = v_b * np.cos(b) + v_r * np.sin(b)

    # Add the full orbital motion of the Sun, converting the source velocity to velocity wrp to the
    U_2 = U_1 + U_sun
    V_2 = V_1 + V_sun + Theta_0
    W_2 = W_1 + W_sun
    v_space = np.sqrt(U_2 ** 2 + V_2 ** 2 + W_2 ** 2)

    return U_2, V_2, W_2, v_space


@jit(nopython=True)
def cartesian_peculiar_velocity_components(ra, dec, pmra, pmdec, dist, v_r):
    """
    This function takes equatorial coordinates, source distance (in kpc), and source radial velocity (v_r; in km/s) to
    compute Galactocentric Cartesian specific velocities.
    pmra is the proper motion in the direction of ra including the cosdec factor.
    """

    l, b = convert_to_galactic(ra, dec)
    U_2, V_2, W_2, _v_space = galactocentric_cartesian_velocity(ra, dec, pmra, pmdec, dist, v_r)
    # R_p: Galactocentric distance to the source projected onto the Galactic plane
    D_p = dist * np.cos(b)
    R_p = np.sqrt(R_0 ** 2 + D_p ** 2 - 2 * R_0 * D_p * np.cos(l))

    # Calculate sin and cos values for angel beta, which is the angle between the Sun and the source as viewed from
    # the GC.
    sinbeta = (D_p / R_p) * np.sin(l)
    cosbeta = (R_0 - D_p * np.cos(l)) / R_p

    # Finally, rotate vector (U_2, V_2, W_2) through angle beta in the Galactic plane and remove circular Galactic
    # rotation from the motion to give the specific velocity wrp to the GC

    Theta_s = np.interp(R_p, r_grid, v_rot_val)  # Assuming MWPotential2014
    # Theta_s = Theta_0
    U_s = U_2 * cosbeta - V_2 * sinbeta
    V_s = V_2 * cosbeta + U_2 * sinbeta - Theta_s
    W_s = W_2

    v_pec = np.sqrt(U_s ** 2 + V_s ** 2 + W_s ** 2)

    return v_pec


def get_random_distances(parallax: float, parallax_error: float) -> Tuple[np.ndarray[Any, np.dtype[np.float64]], str]:
    parallax_over_error = abs(parallax / parallax_error)

    if (parallax_over_error >= 5) and parallax >= 0.1:
        method = SimpleInversion(parallax, parallax_error)
        d_rand = method.gaussian_sampler(nrand=nrand)
        comment = "simple_inversion"

    elif parallax_over_error >= 0.5 and parallax >= -2.0:
        method = ExponentialPriorModel(parallax, parallax_error)
        d_rand = method.sample_posterior(nsteps=1000, nwalkers=4, burn_in=750)
        comment = "exponential_prior"

    else:
        d_rand = np.full(fill_value=10.0, shape=nrand)
        comment = "fixed_at_10"

    return d_rand, comment


@jit(nopython=True)
def get_random_astrometry(ra: float, dec: float,
                          pmra: float, pmra_error: float, pmdec: float, pmdec_error: float):
    ra_rand = np.full(fill_value=ra, shape=nrand)
    dec_rand = np.full(fill_value=dec, shape=nrand)
    pmra_rand = pmra + pmra_error * np.random.randn(nrand)
    pmdec_rand = pmdec + pmdec_error * np.random.randn(nrand)

    return ra_rand, dec_rand, pmra_rand, pmdec_rand


@jit(nopython=True)
def minimize_velocity_numpy(args):
    ra, dec, pmra, pmdec, dist, opt = args
    gamma_grid = np.arange(-500, 500, 0.01)
    if opt == "vpec":
        v_grid = cartesian_peculiar_velocity_components(ra, dec, pmra, pmdec, dist, gamma_grid)
    elif opt == "vspace":
        v_grid = galactocentric_cartesian_velocity(ra, dec, pmra, pmdec, dist, gamma_grid)[-1]
    else:
        raise ValueError(f"{opt} is not a valid option. Choose between 'vpec' and 'vspace'.")

    idx = v_grid.argmin()

    return v_grid[idx], gamma_grid[idx]


def minimize_velocity_scipy(args):
    ra, dec, pmra, pmdec, dist, opt = args
    if opt == "vpec":
        func_v = lambda v_r: cartesian_peculiar_velocity_components(ra, dec, pmra, pmdec, dist, v_r)
    elif opt == "vspace":
        func_v = lambda v_r: galactocentric_cartesian_velocity(ra, dec, pmra, pmdec, dist, v_r)[-1]
    else:
        raise ValueError(f"{opt} is not a valid option. Choose between 'vpec' and 'vspace'.")

    v_min_result = minimize(func_v, x0=0, options={'gtol': 1e-3}, method="BFGS")
    return v_min_result.fun, v_min_result.x[0]


def find_v_min(ra_rand, dec_rand, pmra_rand, pmdec_rand, dist_rand, opt: str = "vpec", method: str = "scipy"):
    args = [(ra_rand[i], dec_rand[i], pmra_rand[i], pmdec_rand[i], dist_rand[i], opt) for i in range(nrand)]

    if method == "scipy":
        results = [minimize_velocity_scipy(arg) for arg in args]

    elif method == "numpy":
        results = [minimize_velocity_numpy(arg) for arg in args]

    else:
        raise ValueError(f"{method} is not a valid method. Please choose between 'numpy' and 'scipy'.")

    v_min, gamma_min = zip(*results)

    return np.array(v_min), np.array(gamma_min)


def get_errors(arr: np.ndarray, lolim_percentile: float = 16, uplim_percentile: float = 84):
    median = np.median(arr)
    lolim = np.percentile(arr, q=lolim_percentile)
    uplim = np.percentile(arr, q=uplim_percentile)

    if (lolim_percentile >= uplim_percentile) or (lolim_percentile >= 50) or (uplim_percentile <= 50):
        raise ValueError(f"Lower-limit or upper-limit percentile not valid.")

    up_error = uplim - median
    lo_error = median - lolim

    return median, lo_error, up_error


def run_computation(df: pd.DataFrame, method: str = "scipy") -> None:
    pm_and_position_cols = ["ra", "dec", "pmra", "pmra_error", "pmdec", "pmdec_error"]
    parallax_cols = ["parallax_corr", "parallax_error"]
    for i, row in tqdm(df.iterrows()):
        pm_and_pos_args = tuple(row[colname] for colname in pm_and_position_cols)
        parallax_args = tuple(row[colname] for colname in parallax_cols)

        pos_and_pm_rand = get_random_astrometry(*pm_and_pos_args)
        d_rand, comment = get_random_distances(*parallax_args)

        for opt in ["vpec", "vspace"]:
            args = pos_and_pm_rand + (d_rand,) + (opt, method)
            v_min, gamma_min = find_v_min(*args)

            v_med, v_lo_err, v_up_err = get_errors(v_min)
            # gamma_min_med, gamma_min_lo_err, gamma_min_up_err = get_errors(gamma_min)
            print(f"v_{opt}={v_med:.2f} +{v_up_err:.2f} -{v_lo_err:.2f}")


def main() -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources"
                     / "combined_vpec_lolim_gt_150_unique_stage_9_prime.csv")

    run_computation(df, method="scipy")


if __name__ == "__main__":
    main()
