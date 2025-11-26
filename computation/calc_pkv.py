from computation.calc_vpec import _compute_distance
from utils.utility_functions import get_errors
from pathlib import Path
from tqdm import tqdm
from galpy.orbit import Orbit
from galpy.potential import MWPotential2014
from constants import GalacticConstants
from astropy.units import Unit
from utils.rotation_curve import v_rot
from typing import Any
from scipy.interpolate import interp1d
import time
import pandas as pd
import numpy as np
import argparse
import config


nrand: int = 5000
tt = np.linspace(0, -10, 1001) * Unit("Gyr")

const = GalacticConstants()
pkv_results = config.RESULTS_DIR / "pkv"
tqdm.pandas()
R0 = const.R0
THETA0 = const.Theta0


def integrate_orbit(row: pd.Series) -> Orbit:
    start_time = time.time()

    name = row["other_name"]
    ra = row["ra"]
    dec = row["dec"]
    pmra = row["pmra"]
    e_pmra = row["pmra_error"]
    pmdec = row["pmdec"]
    e_pmdec = row["pmdec_error"]
    v_r = row["gamma"]
    e_v_r = row["e_gamma"]
    # Initialisation of random orbits for the MC simulation
    ra_rand = np.full(shape=nrand, fill_value=ra)
    dec_rand = np.full(shape=nrand, fill_value=dec)
    pmra_rand = np.random.randn(nrand) * e_pmra + pmra
    pmdec_rand = np.random.randn(nrand) * e_pmdec + pmdec
    v_r_rand = np.random.randn(nrand) * e_v_r + v_r
    d_rand_all = _compute_distance(row)
    d_rand = np.random.choice(d_rand_all, size=nrand, replace=False)

    orbit_params = np.dstack(
        [ra_rand, dec_rand, d_rand, pmra_rand, pmdec_rand, v_r_rand]
    )
    op = Orbit(orbit_params, radec=True, ro=R0, vo=THETA0)

    # Integrating orbit
    print(f'Integrating {nrand} orbits for {name} ...')
    op.integrate(tt, MWPotential2014, method='symplec4_c')
    time_elapsed = time.time() - start_time
    print(
        f"Orbit integration for {name} completed "
        f"in {time_elapsed:.2f} seconds."
    )

    return op


def calc_vpec_t(orb: Orbit) -> Any:
    # Heliocentric Cartesian velocity components
    U1 = orb.U(tt).value
    V1 = orb.V(tt).value
    W1 = orb.W(tt).value

    # Cartesian velocity components relative to the Galactic centre
    U2 = U1 + const.U
    V2 = V1 + const.V + const.Theta0
    W2 = W1 + const.W

    # Convert to co-moving frame at the source position.
    R = orb.R(tt).value
    b = orb.bb(tt).value * (np.pi / 180)
    lon = orb.ll(tt).value * (np.pi / 180)
    Dp = orb.dist(tt).value * np.cos(b)
    sinbeta = (Dp / R) * np.sin(lon)
    cosbeta = (const.R0 - Dp * np.cos(lon)) / R

    U_s = U2 * cosbeta - V2 * sinbeta
    V_s = V2 * cosbeta + U2 * sinbeta - v_rot(R)
    W_s = W2

    vpec_t = np.sqrt(U_s ** 2 + V_s ** 2 + W_s ** 2)

    return vpec_t


def find_pkv(orb: Orbit, name: str) -> tuple:
    vpec_t = calc_vpec_t(orb)

    gal_z = orb.z(tt).value
    n_orbs = gal_z.shape[1]  # This is the number of random orbits

    pkv_all = []
    t0_all = []
    for n in range(n_orbs):  # Loop over random orbits
        z_single = gal_z[0, n, :]
        t0_list = []
        vpec_t_func = interp1d(tt.value, vpec_t[0, n, :])
        for i in range(len(tt)-1):
            if z_single[i+1] * z_single[i] <= 0:
                k = (z_single[i+1] - z_single[i]) / (tt[i+1] - tt[i])
                b = z_single[i] - k * tt[i]
                t0 = - b / k

                t0_list.append(t0.value)

        t0_all = np.concatenate((t0_list, t0_all))
        pkv_single = vpec_t_func(t0_list)
        pkv_all = np.concatenate((pkv_single, pkv_all))

    np.save(pkv_results / f"{name}_pkv_all.npy", pkv_all)
    pkv_med, pkv_loerr, pkv_uperr = get_errors(pkv_all)

    return pkv_med, pkv_loerr, pkv_uperr


def run(df: pd.DataFrame, out_file: Path) -> None:
    print(f"Catalogue loaded: {df.shape[0]} rows.")
    results = []
    for _, row in tqdm(df.iterrows(), total=df.shape[0]):
        name = row["other_name"]
        print(f"Processing {name} ...")
        orb = integrate_orbit(row)
        pkv_med, pkv_loerr, pkv_uperr = find_pkv(orb, name)
        results.append([pkv_med, pkv_loerr, pkv_uperr])

    results_df = pd.DataFrame(
        results, columns=["pkv_med", "e_pkv", "E_pkv"]
    )
    df = pd.concat([df, results_df], axis=1)
    kept_columns = results_df.columns.tolist() + ["source_id", "other_name"]

    if out_file is not None:
        df[kept_columns].to_csv(out_file, index=False)
        print(f"Results saved to {out_file}.")


def entry_point() -> None:
    parser = argparse.ArgumentParser(
        description="Calculate the peculiar kinetic velocity (PKV) "
        "of a catalogue of stars."
    )
    parser.add_argument(
        "--in_file",
        type=Path,
        required=True,
        help="Input CSV file containing the catalogue."
    )
    parser.add_argument(
        "--out_file",
        type=Path,
        required=True,
        help="Output CSV file to save the results."
    )
    args = parser.parse_args()

    df = pd.read_csv(args.in_file)
    run(df, args.out_file)


if __name__ == "__main__":
    entry_point()
