import numpy as np
import constants as con
from utils.rotation_curve import v_rot
from collections.abc import Iterable
from typing import Union

FloatOrIterable = Union[float, Iterable[float]]


# ============================================================
# Convert equatorial coordinates to Galactocentric coordinates
# ============================================================
def convert_to_galactic(ra: FloatOrIterable, dec: FloatOrIterable) -> tuple[FloatOrIterable, FloatOrIterable]:
    """
    This function convert equatorial coordinates to Galactic coordinates. The input ra and dec should be in unit
    of degrees, and the function returns Galactic longitudes and latitudes in degrees.
    """
    ra = np.array(ra)
    dec = np.array(dec)

    # Source coordinates to radian
    conv = con.pi / 180
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


# ===============================================================
# Calculate proper motions in the direction of Galactic longitude
# and latitude.
# ===============================================================
def galactic_proper_motion(ra: FloatOrIterable, dec: FloatOrIterable,
                           mu_ra_cosdec: FloatOrIterable, mu_dec: FloatOrIterable,
                           dt: float = 1) -> FloatOrIterable:
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


# ============================================================
# Calculate peculiar velocities in the Galactocentric frame
# ============================================================

def galactocentric_cartesian_velocity(ra: FloatOrIterable, dec: FloatOrIterable,
                                      pmra: FloatOrIterable, pmdec: FloatOrIterable,
                                      dist: FloatOrIterable, v_r: FloatOrIterable,
                                      U_sun: FloatOrIterable = con.U_sun,
                                      V_sun: FloatOrIterable = con.V_sun,
                                      W_sun: FloatOrIterable = con.W_sun,
                                      Theta_0: FloatOrIterable = con.Theta_0,
                                      R_0: FloatOrIterable = con.R_0,
                                      print_results: bool = False,
                                      random_seed: int = 114514):
    """
    This function takes equatorial coordinates, source distance (in kpc), and source radial velocity (v_r; in km/s) to
    compute Galactocentric Cartesian specific velocities.
    pmra is the proper motion in the direction of ra including the cosdec factor.
    """
    np.random.seed(random_seed)

    # Constants
    conv = (con.pi / 180)
    conv1 = 3600 * 1e3

    # Source distance
    D_cgs = dist * con.kpc

    # Galactic coordinates:
    l, b = convert_to_galactic(ra, dec)
    b *= conv  # convert to radian
    l *= conv

    # PMs in Galactic coordinate
    mu_l, mu_b = galactic_proper_motion(ra, dec, pmra, pmdec, dt=0.1)

    # Physical velocities
    v_b = D_cgs * (mu_b / conv1) * conv * (1e-5 / con.yr)  # in km/s
    v_l = D_cgs * (mu_l / conv1) * np.cos(b) * conv * (1e-5 / con.yr)  # in km/s

    # Convert the spherical coordinate to Galactic Cartesian coordinates at the location of the Sun
    U_1 = (v_r * np.cos(b) - v_b * np.sin(b)) * np.cos(l) - v_l * np.sin(l)
    V_1 = (v_r * np.cos(b) - v_b * np.sin(b)) * np.sin(l) + v_l * np.cos(l)
    W_1 = v_b * np.cos(b) + v_r * np.sin(b)

    # Add the full orbital motion of the Sun, converting the source velocity to velocity wrp to the
    U_2 = U_1 + U_sun
    V_2 = V_1 + V_sun + Theta_0
    W_2 = W_1 + W_sun
    v_space = np.sqrt(U_2 ** 2 + V_2 ** 2 + W_2 ** 2)

    if print_results:
        print('mu_l=%.2f, mu_b=%.2f' % (mu_l, mu_b))
        print('v_l=%.2f, v_b=%.2f' % (v_l, v_b))
        print('U_1=%.2f, V_1=%.2f, W_1=%.2f' % (U_1, V_1, W_1))
        print('U_2=%.2f, V_2=%.2f, W_2=%.2f' % (U_2, V_2, W_2))

    return U_2, V_2, W_2, v_space


def cartesian_peculiar_velocity_components(ra: FloatOrIterable, dec: FloatOrIterable,
                                           pmra: FloatOrIterable, pmdec: FloatOrIterable,
                                           dist: FloatOrIterable, v_r: FloatOrIterable,
                                           U_sun: FloatOrIterable = con.U_sun,
                                           V_sun: FloatOrIterable = con.V_sun,
                                           W_sun: FloatOrIterable = con.W_sun,
                                           Theta_0: FloatOrIterable = con.Theta_0,
                                           R_0: FloatOrIterable = con.R_0,
                                           print_results: bool = False,
                                           random_seed: int = 114514):
    """
    This function takes equatorial coordinates, source distance (in kpc), and source radial velocity (v_r; in km/s) to
    compute Galactocentric Cartesian specific velocities.
    pmra is the proper motion in the direction of ra including the cosdec factor.
    """
    np.random.seed(random_seed)

    l, b = convert_to_galactic(ra, dec)
    U_2, V_2, W_2, _v_space = galactocentric_cartesian_velocity(ra, dec, pmra, pmdec, dist, v_r,
                                                                U_sun, V_sun, W_sun, Theta_0, R_0)
    # R_p: Galactocentric distance to the source projected onto the Galactic plane
    D_p = dist * np.cos(b)
    R_p = np.sqrt(R_0 ** 2 + D_p ** 2 - 2 * R_0 * D_p * np.cos(l))

    # Calculate sin and cos values for angel beta, which is the angle between the Sun and the source as viewed from
    # the GC.
    sinbeta = (D_p / R_p) * np.sin(l)
    cosbeta = (R_0 - D_p * np.cos(l)) / R_p

    # Finally, rotate vector (U_2, V_2, W_2) through angle beta in the Galactic plane and remove circular Galactic
    # rotation from the motion to give the specific velocity wrp to the GC

    # Theta_s = Theta_0 # Assume flat rotation curve
    Theta_s = v_rot(R_p)  # Assuming MWPotential2014

    U_s = U_2 * cosbeta - V_2 * sinbeta
    V_s = V_2 * cosbeta + U_2 * sinbeta - Theta_s
    W_s = W_2

    # print(V_2)

    v_pec = np.sqrt(U_s ** 2 + V_s ** 2 + W_s ** 2)
    #     conv1 = 3600 * 1e3
    #     return mu_l*conv1, mu_b*conv1
    #     return np.cos(l)

    if print_results:
        print('mu_l=%.2f, mu_b=%.2f' % (mu_l, mu_b))
        print('v_l=%.2f, v_b=%.2f' % (v_l, v_b))
        print('U_1=%.2f, V_1=%.2f, W_1=%.2f' % (U_1, V_1, W_1))
        print('U_2=%.2f, V_2=%.2f, W_2=%.2f' % (U_2, V_2, W_2))
        print('U_s=%.2f, V_s=%.2f, W_s=%.2f' % (U_s, V_s, W_s))

    return v_pec
    # return U_2, V_2, W_2, v_pec


def main():
    # from astropy.coordinates import SkyCoord
    # import astropy.units as u
    # ra = np.random.uniform(0, 360, 20)
    # dec = np.random.uniform(-90, 90, 20)
    # pmra = np.random.uniform(-5, 5, 20)
    # pmdec = np.random.uniform(-5, 5, 20)
    # d = np.random.uniform(0, 10, 20)
    #
    # coords = SkyCoord(ra * u.deg, dec * u.deg,
    #                   pm_ra_cosdec=pmra * u.mas / u.yr, pm_dec=pmdec * u.mas / u.yr,
    #                   distance=d * u.kpc,
    #                   frame="icrs")
    #
    # coords_gal = coords.galactic
    # mu_l = coords_gal.pm_l_cosb.value / np.cos(coords_gal.b.rad)
    # mu_b = coords_gal.pm_b.value
    # my_mu_l, my_mu_b = galactic_proper_motion(ra, dec, pmra, pmdec, dt=1)
    # for i in range(len(mu_l)):
    #     print(f"{mu_l[i]: 9.7f} {my_mu_l[i]: 9.7f}, {mu_b[i]:9.7f} {my_mu_b[i]: 9.7f}")

    # results = cal_Galactic_PM(105.6, 34.3, 3.215, -4.367, dt=1)
    results = galactocentric_cartesian_velocity(299.590294829041, 35.2015787651136,
                                                -3.81238517562444, -6.30989323963554,
                                                2.25, -5.1, print_results=True)
    print(results)


if __name__ == "__main__":
    main()
