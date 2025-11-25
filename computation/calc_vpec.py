from utils.vpec_functions import cartesian_peculiar_velocity_components
from utils.distances import ExponentialPriorModel, SimpleInversion
from utils.utility_functions import get_errors
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import numpy as np
import argparse

nrand: int = 10000
tqdm.pandas()


def _compute_distance(
        row: pd.Series, parallax_col: str = "parallax_corr",
        parallax_err_col: str = "parallax_error"
) -> np.ndarray:
    parallax = row[parallax_col]
    parallax_error = row[parallax_err_col]

    if (parallax / parallax_error >= 5) and (parallax >= 0):
        distance_model = SimpleInversion(parallax, parallax_error)
        dist_rand = distance_model.gaussian_sampler(nrand=nrand)
    else:
        distance_model = ExponentialPriorModel(parallax, parallax_error)
        dist_rand = distance_model.sample_posterior(
            nwalkers=4, nsteps=3000, burn_in=500
        )

    return dist_rand


def _compute_vpec(row: pd.Series) -> np.ndarray:
    ra = row["ra"]
    dec = row["dec"]
    pmra = row["pmra"]
    pmra_error = row["pmra_error"]
    pmdec = row["pmdec"]
    pmdec_error = row["pmdec_error"]
    rv = row["gamma"]
    rv_error = row["e_gamma"]

    dist_rand = _compute_distance(row)
    pmra_rand = np.random.normal(pmra, pmra_error, nrand)
    pmdec_rand = np.random.normal(pmdec, pmdec_error, nrand)
    rv_rand = np.random.normal(rv, rv_error, nrand)

    vpec_rand = cartesian_peculiar_velocity_components(
        ra, dec, pmra_rand, pmdec_rand, dist_rand, rv_rand
    )

    vpec_med, vpec_loerr, vpec_uperr = get_errors(vpec_rand)
    dist_med, dist_loerr, dist_uperr = get_errors(dist_rand)

    return dist_med, dist_loerr, dist_uperr, vpec_med, vpec_loerr, vpec_uperr


def run(df: pd.DataFrame, out_file: Path) -> None:
    print(f"Catalogue loaded: {df.shape[0]} rows.")
    results = df.progress_apply(_compute_vpec, axis=1, result_type="expand")
    results.columns = [
        "dist_med", "e_dist", "E_dist", "vpec_med", "e_vpec", "E_vpec"
    ]
    df = pd.concat([df, results], axis=1)
    kept_columns = results.columns.tolist() + ["source_id", "other_name"]

    if out_file is not None:
        print(f"Saving results to {out_file}")
        df[kept_columns].to_csv(out_file, index=False)

    print("Done.")


def entry_point():
    parser = argparse.ArgumentParser(
        description="Calculate peculiar velocities for stars in the catalogue."
    )

    parser.add_argument(
        "--in_file", required=True, type=str, help="Input catalogue file path."
    )

    parser.add_argument(
        "--out_file", required=True, type=str, help="Output file path."
    )
    args = parser.parse_args()

    in_file = Path(args.in_file)
    out_file = Path(args.out_file)

    df = pd.read_csv(in_file)
    run(df, out_file)


if __name__ == "__main__":
    entry_point()
