import pandas as pd
import config
import numpy as np
from astropy.coordinates import SkyCoord


def _load_master_catalogue() -> pd.DataFrame:
    file_path = (
        config.RESULTS_CATALOGUES_FOR_REVISION / "ready_catalogues"
        / "hvxs.csv"
    )
    df = pd.read_csv(file_path)
    print(f"Master catalogue loaded: {df.shape[0]} rows.")

    return df


def select(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()
    coords = SkyCoord(
        df_copy["ra_gaia"],
        df_copy["dec_gaia"],
        frame="icrs",
        unit="deg"
    )
    dist = df_copy["dist_med"]

    b = coords.galactic.b.rad
    z_abs = np.abs(
        np.sin(b) * dist
    )

    df_copy["z_abs"] = z_abs

    df_copy_selected = df_copy.query(
        "dec_gaia >= -76 and dec_gaia <= 11 and "
        "fx_fg >= 10 ** (bp_rp - 3.5) and "
        "dist_med <= 10 and "
        "phot_g_mean_mag <= 18 and "
        "astrometric_excess_noise_sig >= 2"
    )
    cols = [
        "ra_x", "dec_x", "ra_gaia", "dec_gaia", "sep_x_g_sigma", "sep_x_g",
        "vpec_min_med", "e_vpec_min", "fx_fg", "bp_rp", "phot_g_mean_mag",
        "dist_med", "f_x", "parallax", "parallax_error", "z_abs", "source_id",
        "ID_x", "astrometric_excess_noise", "astrometric_excess_noise_sig",
        "logg_gspphot"
    ]
    df_copy_selected = df_copy_selected.sort_values(
        by="ra_gaia", ascending=True
    )
    return df_copy_selected[cols]


def main():
    df_master = _load_master_catalogue()
    df_selected = select(df_master)
    print(f"Selected {df_selected.shape[0]} rows from master catalogue.")

    out_path = (
        config.RESULTS_CATALOGUE_DIR
        / "salt_2026_2" / "high_vpec.csv"
    )

    if not out_path.parent.exists():
        out_path.parent.mkdir(parents=True, exist_ok=True)

    df_selected.to_csv(out_path, index=False)
    print(f"Selected catalogue saved to {out_path}.")


if __name__ == "__main__":
    main()
