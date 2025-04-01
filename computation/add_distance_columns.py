"""
This script is used to add distance columns to a given pandas.DataFrame.
In my previous computation of v_min, I have forgotten to include the distance
columns for some of the catalogues, so I wrote this script to redo the MCMC
sampling for distances without the need to run the whole computation script
again.
"""
import pandas as pd
import config
from computation.distance_estimate_emcee import get_random_distances
from utils.utility_functions import get_errors
from typing import Tuple
from tqdm import tqdm


def get_distances(row: pd.Series) -> Tuple[str, float, float, float, str]:
    name: str = row["IAUName"]
    parallax = row["parallax_corr"]
    parallax_error = row["parallax_error"]

    dist_rand, comment = get_random_distances(parallax, parallax_error)
    dist_med, dist_lo_err, dist_hi_err = get_errors(arr=dist_rand)

    return name, dist_med, dist_lo_err, dist_hi_err, comment


def run_computation() -> None:
    survey_name: str = "swift"
    in_file_dir = (
        config.ROOT_DIR / "results" / survey_name / "catalogues" / "nway_match"
    )

    in_file_path = (
        in_file_dir / f"{survey_name}_gaia_nway_match_stars_only_for_vpec.csv"
    )

    in_file_vpec = (
        config.RESULTS_CATALOGUE_DIR
        / "v_min_catalogs"
        / f"{survey_name}_w_v_min.csv"
    )

    df = pd.read_csv(in_file_path)
    df_vpec = pd.read_csv(in_file_vpec)

    tqdm.pandas()
    results = df.progress_apply(get_distances, axis=1, result_type="expand")

    results.columns = [
        "ID_x", "dist_med", "e_dist", "E_dist", "distance_inference"
    ]

    df_merged = pd.merge(df_vpec, results, on="ID_x", how="right")

    out_file = in_file_vpec.parent / f"{in_file_vpec.stem}_w_dist.csv"

    df_merged.to_csv(out_file, index=False)
    print("Done")


if __name__ == "__main__":
    run_computation()
