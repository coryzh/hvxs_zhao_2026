import numpy as np
import constants
# from scipy.integrate import quad
# from scipy.interpolate import interp1d
from scipy.stats import truncnorm, gamma
from typing import Any
from functools import partial
from scipy.optimize import minimize, Bounds
import emcee

pi = np.pi
L = constants.L


# class ExponentialPriorModel:
#     def __init__(self, parallax, e_parallax):
#         self.parallax = parallax
#         self.e_parallax = e_parallax
#
#     @staticmethod
#     def prior(d):
#         return 1 / (2 * L ** 3) * d ** 2 * np.exp(-d / L)
#
#     def likelihood(self, d):
#         y = (1 / (np.sqrt(2 * pi) * self.e_parallax)) * \
#             np.exp(- (self.parallax - 1 / d) ** 2 / (2. * self.e_parallax ** 2))
#         return y
#
#     def posterior_unnorm(self, d):
#         """
#         This is the posterior distribution function (not normalized) of distances using
#         the exponential prior (characterized by the scaling parameter L).
#         The normalization constant is not considered here as it will be
#         accounted for in the generate_distances() function.
#         """
#
#         exponent = -(d / L) - (1 / (2 * self.e_parallax ** 2)) * (self.parallax - 1 / d) ** 2
#
#         return d ** 2 * np.exp(exponent)
#
#     def posterior(self, d):
#         """
#         Description:
#             Posterior of distance (normalised).
#
#         Parameter:
#             d: distance in kpc. Can be a single value or a np.ndarray.
#         """
#         results = quad(func=self.posterior_unnorm, a=constants.minimum_d, b=+np.inf)
#
#         # Normalization constant for the distance posterior is optimised for very narrow PDF. When the PDF is too
#         # narrow, i.e., when sigma_parallax is very small, we estimate the integral as the area of the rectangular
#         # with width of 0.01 and height equals to un-normalised PDF value at 1/parallax.
#         if np.isclose(results[0], 0, rtol=1e-6):
#             norm = self.posterior_unnorm(1 / self.parallax) * 0.01
#
#         else:
#             norm = results[0]
#         # norm = results[0]
#         return (1. / norm) * self.posterior_unnorm(d)
#
#     def sample_posterior(self, nrand):
#         dd = 1e-3
#         d_grid = np.arange(dd, 100, dd)
#         d_post = self.posterior(d_grid)
#
#         cdf = np.cumsum(d_post * dd)
#         inv_cdf = interp1d(cdf, d_grid, bounds_error=False, fill_value=(0, 1))
#
#         u_rand = np.random.rand(nrand)
#         d_rand = inv_cdf(u_rand)
#
#         return d_rand


class ExponentialPriorModel:
    def __init__(self, parallax, parallax_error):
        self.parallax = parallax
        self.parallax_error = parallax_error

    @property
    def parallax_over_error(self) -> float:
        return abs(self.parallax / self.parallax_error)

    @staticmethod
    def log_prior(d: float) -> float:
        if d < 0:
            return -np.inf

        else:
            return 2 * np.log(d) - d / L

    def log_likelihood(self, d) -> float:
        if d < 0:
            return -np.inf

        else:
            return -0.5 * (self.parallax - 1 / d) ** 2 / self.parallax_error ** 2

    def log_posterior(self, d) -> float:
        return self.log_prior(d) + self.log_likelihood(d)

    def sample_posterior(self, nwalkers: int = 4, nsteps: int = 2000,
                         burn_in: int = 500) -> np.ndarray[Any, np.dtype[np.float64]]:

        initial_distances = np.abs(np.random.normal(1 / self.parallax, 0.5, size=nwalkers))

        log_prob_fn = partial(self.log_posterior)
        sampler = emcee.EnsembleSampler(nwalkers=nwalkers, ndim=1, log_prob_fn=log_prob_fn)

        _run = sampler.run_mcmc(initial_distances[:, None], nsteps=nsteps, progress=False)

        samples = sampler.get_chain(discard=burn_in, flat=True)[:, 0]

        return samples


class SimpleInversion:
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


class FromLiterature:
    def __init__(self, x_est, x_lo, x_hi, conf_level: float = 0.68):
        self.x_est = x_est
        self.x_lo = x_lo
        self.x_hi = x_hi
        self.conf_leve = conf_level

        if x_lo >= x_hi:
            raise ValueError(f"Lower limit (x_lo) must be less than the upper limit (x_hi).")

        if conf_level< 0 or conf_level > 1:
            raise ValueError(f"Confidence level must be a number between 0 and 1.")

    @property
    def x_loerr(self) -> float:
        return self.x_est - self.x_lo

    @property
    def x_uperr(self) -> float:
        return self.x_hi - self.x_est

    @property
    def sigma_0(self) -> float:
        """Averaged error, which could be used as an initial guess for fitting a skewed distribution."""
        return 0.5 * (self.x_loerr + self.x_uperr)

    @property
    def _sigma_min(self) -> float:
        return min(self.x_loerr, self.x_loerr)

    def fit_gamma(self) -> dict:
        """Fit the literature nominal values to a gamma distribution."""

        def get_gamma_distribution(sigma_x) -> dict:
            alpha = ((2 * sigma_x + self.x_est ** 2 + np.sqrt(4 * sigma_x * self.x_est ** 2 + self.x_est ** 4))
                     / (2 * sigma_x))
            theta = self.x_est / (alpha - 1)
            x_gamma = gamma(a=alpha, scale=theta)

            return dict(alpha=alpha, theta=theta, distribution=x_gamma)

        def difference(sigma_x) -> float:
            _re = get_gamma_distribution(sigma_x)
            x_gamma = _re["distribution"]

            x_lo_model = x_gamma.ppf((1 - self.conf_leve) / 2)
            x_hi_model = x_gamma.ppf((1 + self.conf_leve) / 2)

            diff = np.sqrt((self.x_lo - x_lo_model) ** 2 + (self.x_hi - x_hi_model) ** 2)

            return diff

        results = minimize(difference, x0=self.sigma_0, bounds=Bounds(self._sigma_min / 2))

        return get_gamma_distribution(results.x[0])


def truncated_normal_distances(d_cen: float, d_std: float, nsim: int,
                               my_clip_a: float = 0.0, my_clip_b: float = 100.0, ) -> np.ndarray:
    a, b = (my_clip_a - d_cen) / d_std, (my_clip_b - d_cen) / d_std

    d_rand = truncnorm.rvs(a, b, size=nsim) * d_std + d_cen

    return d_rand
