import pandas as pd
import config
import numpy as np
from astropy.coordinates import SkyCoord


def _load_master_catalogue() -> pd.DataFrame:
    file_path = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "master_catalogue.csv"
    )
    df = pd.read_csv(file_path)
    print(f"Master catalogue loaded: {df.shape[0]} rows.")

    return df


def select(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()
    coords = SkyCoord(
        df_copy["ra"],
        df_copy["dec"],
        frame="icrs",
        unit="deg"
    )
    dist = df_copy["r_med_photogeo"]

    b = coords.galactic.b.rad
    z_abs = np.abs(
        np.sin(b) * dist
    )

    df_copy["z_abs"] = z_abs

    df_copy_selected = df_copy.query(
        "z_abs >= 2.0 and mh_gspphot >= 0.1 and "
        "dec >= -76 and dec <= 11 and "
        "fx_fg >= 10 ** (bp_rp - 3.5) and "
        "r_med_photogeo <= 10 and "
        "phot_g_mean_mag <= 17"
    )

    return df_copy_selected


def main():
    df_master = _load_master_catalogue()
    df_selected = select(df_master)
    print(f"Selected {df_selected.shape[0]} rows from master catalogue.")

    out_path = (
        config.RESULTS_CATALOGUE_DIR
        / "salt_2026_2" / "chemically_peculiar.csv"
    )

    if not out_path.parent.exists():
        out_path.parent.mkdir(parents=True, exist_ok=True)

    df_selected.to_csv(out_path, index=False)
    print(f"Selected catalogue saved to {out_path}.")


if __name__ == "__main__":
    main()
