import numpy as np
import pandas as pd
import config
from dustmaps.csfd import CSFDQuery
from astropy.coordinates import SkyCoord
from utils.gal_extinction import gal_extinction_vec
from typing import Tuple


phot_name_dict = {
    "gaia_g": "phot_g_mean_mag",
    "gaia_bp": "phot_bp_mean_mag",
    "gaia_rp": "phot_rp_mean_mag"
}

wave_dict = {
    "gaia_g": 6251.50,
    "gaia_bp": 5124.20,
    "gaia_rp": 7829.65
}


def get_reddening(df: pd.DataFrame) -> np.ndarray:
    coord = SkyCoord(df.ra, df.dec, frame="icrs", unit="deg")
    csfd = CSFDQuery()
    e_b_v = csfd(coord)

    return e_b_v


def get_extinction(df: pd.DataFrame, band: str = "gaia_g"):
    wave = wave_dict[band]
    e_b_v = get_reddening(df)
    a_lam = gal_extinction_vec(lam=wave, e_b_v=e_b_v)

    return a_lam


def extinction_correction(df: pd.DataFrame) -> pd.DataFrame:
    # mag_corr_dict = {}
    for key, val in phot_name_dict.items():
        mag_obs = df[val].values
        a_lam = get_extinction(df, band=key)
        # mag_corr_dict[f"{val}_corr"] = mag_obs - a_lam

        df[f"{val}_corr"] = mag_obs - a_lam

    return df


def main() -> None:
    in_file = config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_med_gt_0_unique.csv"
    df = pd.read_csv(in_file)

    # results = get_extinction(df, band="gaia_g")
    df_out = extinction_correction(df)
    if "stage_5" in in_file.stem:
        out_file = in_file.parent / f"{in_file.stem.replace('stage_5', 'stage_6')}.csv"

    else:
        out_file = in_file.parent / f"{in_file.stem}_stage_6.csv"

    df_out.to_csv(out_file, index=False)

    # print(df_out)


if __name__ == "__main__":
    main()
