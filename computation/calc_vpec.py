from utils.vpec_functions import cartesian_peculiar_velocity_components
from utils.distances import (
    FromLiterature, SimpleInversion, ExponentialPriorModel
)
from utils.utility_functions import get_errors
from pathlib import Path
from tqdm import tqdm
import pandas as pd
import numpy as np
import argparse

nrand: int = 10000
tqdm.pandas()


def _imputation_bailer_jones(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()

    df_copy["r_med_photogeo"] = (
        df_copy["r_med_photogeo"].fillna(df_copy["r_med_geo"])
    )

    df_copy["r_lo_photogeo"] = (
        df_copy["r_lo_photogeo"].fillna(df_copy["r_lo_geo"])
    )

    df_copy["r_hi_photogeo"] = (
        df_copy["r_hi_photogeo"].fillna(df_copy["r_hi_geo"])
    )

    mask_lo = df_copy['r_med_photogeo'] == df_copy['r_lo_photogeo']
    mask_hi = df_copy['r_med_photogeo'] == df_copy['r_hi_photogeo']

    df_copy.loc[mask_lo, 'r_med_photogeo'] = df_copy.loc[mask_lo, 'r_med_geo']
    df_copy.loc[mask_lo, 'r_lo_photogeo'] = df_copy.loc[mask_lo, 'r_lo_geo']
    df_copy.loc[mask_lo, 'r_hi_photogeo'] = df_copy.loc[mask_lo, 'r_hi_geo']

    df_copy.loc[mask_hi, 'r_med_photogeo'] = df_copy.loc[mask_hi, 'r_med_geo']
    df_copy.loc[mask_hi, 'r_lo_photogeo'] = df_copy.loc[mask_hi, 'r_lo_geo']
    df_copy.loc[mask_hi, 'r_hi_photogeo'] = df_copy.loc[mask_hi, 'r_hi_geo']

    return df_copy


def _compute_distance(
        row: pd.Series, method: str = "bailer_jones"
) -> np.ndarray:
    if method == "bailer_jones":
        r_med_photogeo = row["r_med_photogeo"]
        r_lo_photogeo = row["r_lo_photogeo"]
        r_hi_photogeo = row["r_hi_photogeo"]

        distance_model = FromLiterature(
            r_med_photogeo, r_lo_photogeo, r_hi_photogeo
        )
        results = distance_model.fit_gamma()
        gamma_dist = results["distribution"]
        dist_rand = gamma_dist.rvs(size=nrand)

        return dist_rand

    elif method == "zhao23":
        parallax = row["parallax_corr"]
        parallax_error = row["parallax_error"]

        if parallax / parallax_error >= 5.0:
            dist_model = SimpleInversion(parallax, parallax_error)
            dist_rand = dist_model.gaussian_sampler(nrand)

        else:
            distance_model = ExponentialPriorModel(
                parallax, parallax_error
            )
            dist_rand = distance_model.sampler()

        return dist_rand

    else:
        raise ValueError(f"Unknown distance method: {method}")


def _compute_vpec(row: pd.Series, method: str = "bailer_jones") -> np.ndarray:
    source_id = row["source_id"]
    ra = row["ra"]
    dec = row["dec"]
    pmra = row["pmra"]
    pmra_error = row["pmra_error"]
    pmdec = row["pmdec"]
    pmdec_error = row["pmdec_error"]
    rv = row["rv"]
    rv_error = row["rv_err"]

    dist_rand = _compute_distance(row, method=method)
    pmra_rand = np.random.normal(pmra, pmra_error, nrand)
    pmdec_rand = np.random.normal(pmdec, pmdec_error, nrand)
    rv_rand = np.random.normal(rv, rv_error, nrand)

    vpec_rand = cartesian_peculiar_velocity_components(
        ra, dec, pmra_rand, pmdec_rand, dist_rand, rv_rand
    )

    vpec_med, vpec_loerr, vpec_uperr = get_errors(vpec_rand)
    dist_med, dist_loerr, dist_uperr = get_errors(dist_rand)

    return (
        source_id,
        dist_med, dist_loerr, dist_uperr, vpec_med, vpec_loerr, vpec_uperr
    )


def run(
        df: pd.DataFrame, out_file: Path, main_id_col: str = "Name",
        method: str = "zhao23"
) -> None:
    print(f"Catalogue loaded: {df.shape[0]} rows.")

    if method == "bailer_jones":
        print(
            "Filling missing photogeometric distances with geometric "
            "distances..."
        )
        df = _imputation_bailer_jones(df)

    results = df.progress_apply(
        _compute_vpec, axis=1, result_type="expand", method=method
    )
    results.columns = [
       "source_id",
       "dist_med", "e_dist", "E_dist", "vpec_med", "e_vpec", "E_vpec"
    ]

    if main_id_col:
        kept_cols_in_original = [main_id_col, "source_id"]

    else:
        kept_cols_in_original = ["source_id"]

    df_merged = pd.merge(
        df[kept_cols_in_original], results, on="source_id", how="left"
    )

    if out_file is not None:
        print(f"Saving results to {out_file}")
        df_merged.to_csv(out_file, index=False)

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

    parser.add_argument(
        "--main_id_col", required=False, type=str, default="Name",
        help="Column name for the main identifier of the stars."
    )

    parser.add_argument(
        "--method", required=False, type=str, default="bailer_jones",
        help="Method to compute distances ('bailer_jones' or 'zhao23')."
    )
    args = parser.parse_args()

    in_file = Path(args.in_file)
    out_file = Path(args.out_file)

    df = pd.read_csv(in_file, dtype={"source_id": str})
    run(df, out_file, main_id_col=args.main_id_col, method=args.method)


if __name__ == "__main__":
    entry_point()
