import numpy as np
import config
import pandas as pd
from utils.vpec_functions import cartesian_peculiar_velocity_components
from utils.distances import FromLiterature
from pathlib import Path
from argparse import ArgumentParser


def get_vpec(
        catalog_path: Path, source_id: int, out_dir: Path, n_sim: int = 1000
) -> dict:
    df = pd.read_csv(catalog_path, index_col="source_id")
    df = df.rename(columns={"ra_gaia": "ra", "dec_gaia": "dec"})
    row = df.loc[source_id]

    pos_colnames = ["ra", "dec"]
    pm_colnames = ["pmra", "pmdec"]

    arg_dict = {}
    d_med = row["r_med_photogeo"]
    d_hi = row["r_hi_photogeo"]
    d_lo = row["r_lo_photogeo"]
    dist = FromLiterature(x_est=d_med, x_hi=d_hi, x_lo=d_lo, conf_level=0.68)
    # dist = SimpleInversion(row["parallax_corr"], row["parallax_error"])
    fit_results = dist.fit_gamma()
    d_gamma_dist = fit_results["distribution"]

    arg_dict["dist"] = d_gamma_dist.rvs(n_sim)

    gamma_grid = np.linspace(-1000, 1000, 10000)

    for par_name in pos_colnames:
        par_arr = np.full(shape=n_sim, fill_value=row[par_name])
        arg_dict[par_name] = par_arr

    for par_name in pm_colnames:
        par_val = row[par_name]
        par_err = row[f"{par_name}_error"]

        par_rand = par_val + par_err * np.random.randn(n_sim)
        arg_dict[par_name] = par_rand

    vpec = np.zeros(len(gamma_grid))
    vpec_lo = np.zeros(len(gamma_grid))
    vpec_hi = np.zeros(len(gamma_grid))

    for i, gamma in enumerate(gamma_grid):
        vpec_arr = cartesian_peculiar_velocity_components(
            v_r=gamma, **arg_dict
        )
        vpec[i] = np.median(vpec_arr)
        vpec_lo[i] = np.percentile(vpec_arr, 16)
        vpec_hi[i] = np.percentile(vpec_arr, 84)

    vpec_lo_min = min(vpec_lo)
    min_idx = np.argmin(vpec_lo)
    gamma_min = gamma_grid[min_idx]

    result_dict = {
        "vpec": vpec, "vpec_lo": vpec_lo, "vpec_hi": vpec_hi,
        "gamma": gamma_grid, "vpec_lo_min": vpec_lo_min,
        "gamma_min": gamma_min
    }

    out_file_name = f"{source_id}_vpec_vs_gamma.npz"

    np.savez(out_dir / out_file_name, **result_dict)

    return result_dict


if __name__ == "__main__":
    parser = ArgumentParser(
        description="Calculate vpec vs gamma for a given source_id"
    )
    parser.add_argument(
        "--catalog_path", type=Path,
        help="Path to the input catalog CSV file"
    )
    parser.add_argument(
        "--source_id", type=int, help="Gaia source_id of the target source"
    )
    parser.add_argument(
        "--out_dir", type=Path,
        help="Output directory to save results"
    )
    parser.add_argument(
        "--n_sim", type=int, default=1000,
        help="Number of simulations to run (default: 1000)"
    )

    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)

    get_vpec(
        catalog_path=args.catalog_path,
        source_id=args.source_id,
        out_dir=args.out_dir,
        n_sim=args.n_sim
    )
