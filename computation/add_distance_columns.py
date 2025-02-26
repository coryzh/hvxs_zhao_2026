"""
This script is used to add distance columns to a given pandas.DataFrame.
In my previous computation of v_min, I have forgotten to include the distance columns for some of the catalogues, so
I wrote this script to redo the MCMC sampling for distances without the need to run the whole computation script again.
"""
import pandas as pd
import config
from computation.calc_v_min import get_random_distances, get_errors
from typing import Tuple
from tqdm import tqdm


def get_distances(row: pd.Series) -> Tuple[str, float, float, float, str]:
    name: str = row["ID_x"]
    parallax = row["parallax_corr"]
    parallax_error = row["parallax_error"]

    dist_rand, comment = get_random_distances(parallax, parallax_error)
    dist_med, dist_lo_err, dist_hi_err = get_errors(arr=dist_rand)

    return name, dist_med, dist_lo_err, dist_hi_err, comment


def run_computation() -> None:
    survey_name: str = "csc"
    in_file = config.RESULTS_CATALOGUE_DIR / "v_min_catalogs" / f"{survey_name}_w_v_min.csv"
    df = pd.read_csv(in_file)
    df_sub = df.iloc[:10]
    tqdm.pandas()
    results = df_sub.progress_apply(get_distances, axis=1, result_type="expand")

    results.columns = ["ID_x", "dist_med", "e_dist", "E_dist", "distance_inference"]

    df_merged = pd.merge(df_sub, results, on="ID_x", how="left")
    
    out_file = in_file.parent / f"{in_file.stem}_w_dist.csv"
    # df_merged.to_csv(out_file, index=False)


if __name__ == "__main__":
    run_computation()
