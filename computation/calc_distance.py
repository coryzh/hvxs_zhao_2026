from utils.distances import ExponentialPriorModel
from utils.utility_functions import get_errors
from typing import Tuple
from tqdm import tqdm
import pandas as pd
import argparse


def _get_distance(
        row: pd.Series
) -> Tuple[float, float, float]:
    parallax = row["parallax_corr"]
    parallax_error = row["parallax_error"]

    dist_model = ExponentialPriorModel(
        parallax=parallax, parallax_error=parallax_error
    )

    d_rand = dist_model.sample_posterior()
    d_med, d_lo, d_hi = get_errors(d_rand)

    return d_med, d_lo, d_hi


def compute(df: pd.DataFrame) -> pd.DataFrame:
    df = df.set_index("source_id", drop=True)
    distance_results = df.apply(_get_distance, axis=1, result_type="expand")
    distance_results.columns = [
        "dist_exp_med", "e_dist_exp", "E_dist_exp"
    ]

    return distance_results


def entry_point():
    parser = argparse.ArgumentParser(
        description="Calculate distances using exponential prior model."
    )

    parser.add_argument(
        "--in_file",
        type=str,
        required=True,
        help="Path to the input CSV file containing source data."
    )

    parser.add_argument(
        "--out_file",
        type=str,
        required=True,
        help="Path to the output CSV file to save results."
    )

    args = parser.parse_args()

    in_file = args.in_file
    out_file = args.out_file

    df = pd.read_csv(in_file)
    df_dist = compute(df)
    df_dist.to_csv(out_file, index=True)


if __name__ == "__main__":
    entry_point()
