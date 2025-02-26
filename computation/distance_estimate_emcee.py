from utils.distances import SimpleInversion, ExponentialPriorModel
from typing import Tuple, Any
import numpy as np


def get_random_distances(parallax: float, parallax_error: float,
                         nrand: int = 1000) -> Tuple[np.ndarray[Any, np.dtype[np.float64]], str]:
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
