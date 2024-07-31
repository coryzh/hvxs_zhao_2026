import numpy as np
import constants
from scipy.integrate import quad
from scipy.interpolate import interp1d
from scipy.stats import truncnorm

pi = np.pi
L = constants.L


class ExponentialPriorModel:
    def __init__(self, parallax, e_parallax):
        self.parallax = parallax
        self.e_parallax = e_parallax

    @staticmethod
    def prior(d):
        return 1 / (2 * L ** 3) * d ** 2 * np.exp(-d / L)

    def likelihood(self, d):
        y = (1 / (np.sqrt(2 * pi) * self.e_parallax)) * \
            np.exp(- (self.parallax - 1 / d) ** 2 / (2. * self.e_parallax ** 2))
        return y

    def posterior_unnorm(self, d):
        """
        This is the posterior distribution function (not normalized) of distances using
        the exponential prior (characterized by the scaling parameter L).
        The normalization constant is not considered here as it will be
        accounted for in the generate_distances() function.
        """

        exponent = -(d / L) - (1 / (2 * self.e_parallax ** 2)) * (self.parallax - 1 / d) ** 2

        return d ** 2 * np.exp(exponent)

    def posterior(self, d):
        """
        Description:
            Posterior of distance (normalised).

        Parameter:
            d: distance in kpc. Can be a single value or a np.ndarray.
        """
        results = quad(func=self.posterior_unnorm, a=constants.minimum_d, b=+np.inf)

        # Normalisation constant for the distance posterior is optimised for very narrow PDF. When the PDF is too
        # narrow, i.e., when sigma_parallax is very small, we estimate the integral as the area of the rectangular
        # with width of 0.01 and height equals to un-normalised PDF value at 1/parallax.
        if np.isclose(results[0], 0, rtol=1e-6):
            norm = self.posterior_unnorm(1 / self.parallax) * 0.01

        else:
            norm = results[0]
        # norm = results[0]
        return (1. / norm) * self.posterior_unnorm(d)

    def sample_posterior(self, nrand):
        dd = 1e-3
        d_grid = np.arange(dd, 100, dd)
        d_post = self.posterior(d_grid)

        cdf = np.cumsum(d_post * dd)
        inv_cdf = interp1d(cdf, d_grid, bounds_error=False, fill_value=(0, 1))

        u_rand = np.random.rand(nrand)
        d_rand = inv_cdf(u_rand)

        return d_rand


class simple_inversion:
    """
    Distances objects typically for instances that are nearby (parallax > 4) and have well constrained parallaxes
    (e_par/par<0.2).
    """

    def __init__(self, parallax, e_parallax):
        self.parallax = parallax
        self.e_parallax = e_parallax

    def gaussian_sampler(self, nrand):
        d_cen = 1 / self.parallax
        d_std = self.e_parallax / self.parallax ** 2

        my_clip_a = 0
        my_clip_b = 100

        a, b = (my_clip_a - d_cen) / d_std, (my_clip_b - d_cen) / d_std

        d_rand = truncnorm.rvs(a, b, size=nrand) * d_std + d_cen

        # counter = 0
        # d_rand = []
        # while counter < nrand:
        #     d_rand_indiv = np.random.randn(1)[0] * d_std + d_cen
        #     if d_rand_indiv > 0:
        #         d_rand.append(d_rand_indiv)
        #         counter += 1

        return np.array(d_rand)


def truncated_normal_distances(d_cen: float, d_std: float, nsim: int,
                               my_clip_a: float = 0.0, my_clip_b: float = 100.0, ) -> np.ndarray:
    a, b = (my_clip_a - d_cen) / d_std, (my_clip_b - d_cen) / d_std

    d_rand = truncnorm.rvs(a, b, size=nsim) * d_std + d_cen

    return d_rand
