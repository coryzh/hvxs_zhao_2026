import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import config
import data_schema as ds
from utils.vpec_functions import cartesian_peculiar_velocity_components
from typing import Tuple, Any
from query.gaia import gaia_single_source_id_search
from log.loggers import VerboseLogger


def get_vpec(source_id: Any, v_r: float, v_r_error: float,
             verbose: bool = False, n_rand: int = 1000) -> Tuple[np.ndarray, np.ndarray]:

    logger = VerboseLogger(verbose=verbose)

    logger.begin()
    logger.log(f"Querying Gaia archive for {source_id} ...\n")
    cols = ["source_id", "ra", "dec", "pmra", "pmra_error", "pmdec", "pmdec_error"]
    results = gaia_single_source_id_search(source_id, columns=cols)
    results_df = results.to_pandas()
    row = results_df.iloc[0]

    ra_rand = np.full(fill_value=row[ds.Gaia.ra], shape=n_rand)
    dec_rand = np.full(fill_value=row[ds.Gaia.ra], shape=n_rand)
    pmra_rand = row["pmra"] + np.random.randn(n_rand) * row["pmra_error"]
    pmdec_rand = row["pmdec"] + np.random.randn(n_rand) * row["pmdec_error"]
    v_r_rand = v_r + np.random.randn(n_rand) * v_r_error

    dist_grid = np.linspace(0.1, 30, 300)
    vpec_grid = np.zeros(shape=(dist_grid.shape[0], n_rand))
    for i, dist in enumerate(dist_grid):
        vpec_grid[i, :] = cartesian_peculiar_velocity_components(ra_rand, dec_rand, pmra_rand, pmdec_rand, dist, v_r_rand)

    return dist_grid, vpec_grid


def main() -> None:
    dist_range, vpec_range = get_vpec(source_id=5852296053620905472, v_r=102, v_r_error=4, verbose=True)
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    vpec_med = np.median(vpec_range, axis=1)
    vpec_lo = np.percentile(vpec_range, 16, axis=1)
    vpec_hi = np.percentile(vpec_range, 84, axis=1)

    ax.plot(dist_range, vpec_med, lw=2.5, color="r")
    ax.fill_between(dist_range, y1=vpec_lo, y2=vpec_hi, fc="g", alpha=0.2)

    ax.set_xlabel("Distance (kpc)")
    ax.set_ylabel(r"$v_\mathrm{pec}\,\mathrm{(km~s^{-1})}$")
    ax.set_yscale("log")
    # ax.set_xscale("log")

    data = {"dist": dist_range, "vpec_med": vpec_med, "vpec_lo": vpec_lo, "vpec_hi": vpec_hi}
    df_results = pd.DataFrame(data=data)
    df_results.to_csv(config.RESULTS_CATALOGUE_DIR / "bw_cir_vpec_vs_dist.csv", index=False)

    plt.savefig(config.RESULTS_FIGURES_DIR / "bw_cir_vpec_vs_distance.pdf")


if __name__ == "__main__":
    main()
