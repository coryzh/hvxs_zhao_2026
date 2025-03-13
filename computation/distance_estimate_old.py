from utils.distances import SimpleInversion, ExponentialPriorModel
from typing import Tuple, Any
from catalog.manipulate.parallax_zeropoint_correction import correct_zp
import numpy as np
import pandas as pd
import data_schema as ds
import config


def estimate_distance(parallax: float, parallax_error: float, n_rand: int = 1000) -> Tuple[Any, Any, Any, Any]:
    if parallax >= 0.05 and (abs(parallax_error / parallax) <= 0.1):
        # For very large and/or well-constrained parallaxes, simple inversion is used to calculate the distance.
        comments = "simple_inversion"
        model = SimpleInversion(parallax, parallax_error)
        dist_rand = model.gaussian_sampler(n_rand)

    elif parallax > 0.05 and (abs(parallax_error / parallax) > 0.1):
        # Exponential model is used on moderate-to-small parallaxes that have relatively poorly-constrained parallaxes.
        comments = "exp_model"
        model = ExponentialPriorModel(parallax, parallax_error)
        dist_rand = model.sample_posterior(n_rand)

    elif -1 <= parallax < -0.1 and (abs(parallax_error / parallax) <= 0.2):
        # For not very negative parallaxes that are not close to 0, adopt the exponential prior model.
        comments = "exp_model"
        model = ExponentialPriorModel(parallax, parallax_error)
        dist_rand = model.sample_posterior(n_rand)

    else:
        # For parallaxes very close to 0, use a constant distance of 10 kpc.
        comments = "fixed_at_1"
        dist_rand = np.full(fill_value=1, shape=n_rand)

    dist_med = np.median(dist_rand)
    e_dist = dist_med - np.percentile(dist_rand, 16)
    E_dist = np.percentile(dist_rand, 84) - dist_med

    return dist_med, e_dist, E_dist, comments


def estimate_distances_df(row: pd.Series) -> Tuple[Any, Any, Any, Any]:
    if ds.Gaia.parallax_error not in row.index:
        raise KeyError(f"The pandas.DataFrame does not have the zeropoint corrected parallax column, which "
                       f"should be named {ds.Gaia.parallax_corr}.")

    parallax = row[ds.Gaia.parallax_corr]
    parallax_error = row[ds.Gaia.parallax_error]

    results = estimate_distance(parallax, parallax_error)

    return results


def main() -> None:
    df_co = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "known_co_binaries_full_gaia.csv")
    df_co_updated = correct_zp(df_co, verbose=True)
    df_co_updated.to_csv(config.RESULTS_CATALOGUE_DIR / "known_co_binaries_zp_corrected.csv")


if __name__ == "__main__":
    main()
