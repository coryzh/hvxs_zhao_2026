import pandas as pd
import config
import astropy.units as u
from query.panstarrs_images import getcolorim


def get_image_files_for_prime_sample() -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high_v_sources"
                     / "combined_vpec_lolim_gt_150_unique_stage_9_prime.csv")

    cutout_size = 200
    for i, row in df.iterrows():
        ra = row["ra_x"]
        dec = row["dec_x"]
