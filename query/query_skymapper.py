from skymapper import query_skymapper_image_database, get_skymapper_image_fits
import pandas as pd
import config
from pathlib import Path
from astropy.coordinates import SkyCoord
from astropy.units import Quantity
from tqdm import tqdm


def get_image_table(df: pd.DataFrame, id_x: str, size: Quantity, out_root: Path = None) -> None:
    """
    Query the SkyMapper image database for a given ERASS ID and save the image table to a CSV file.
    Parameters
    ----------
    df : pd.DataFrame
        The DataFrame containing the ERASS catalogue.

    id_x : str
        The X-ray source ID of the target.

    size : Quantity
        The size of the image to query, which should be an astropy.units.Quantity object.

    out_root : Path
        The root directory where the image table will be saved.

    Returns
    -------
    None
    """
    df_copy = df.copy()
    df_copy.set_index("ID_x", inplace=True)
    row = df_copy.loc[id_x]
    ra = row["ra_x"]
    dec = row["dec_x"]

    centre = SkyCoord(ra, dec, unit="deg")

    # print(f"Querying the SkyMapper image database for {erass_id} ...")
    table_url = query_skymapper_image_database(centre, size, filters=["g", "r", "i", "z", "y"], response_format="CSV")
    # print(table_url)
    df_img = pd.read_csv(table_url)
    # print(f"A total of {df_img.shape[0]} images returned.\n")

    out_image_table_path = out_root / id_x / f"image_table.csv"
    out_image_max_exptime_table_path = out_root / id_x / f"max_exptime_table.csv"
    if not out_image_table_path.parent.exists():
        out_image_table_path.parent.mkdir(parents=True, exist_ok=True)

    df_img.to_csv(out_image_table_path, index=False)
    max_exptime_indices = df_img.groupby("band")["exptime"].idxmax()
    df_img_max_exptime = df_img.loc[max_exptime_indices, ["unique_image_id", "band", "exptime"]]

    df_img_max_exptime.to_csv(out_image_max_exptime_table_path, index=False)
    # print(f"Image table saved to {out_image_table_path}\n")


def get_fits_image() -> None:
    for i, ids in enumerate(tqdm(erass_ids)):
        img_table_file = (config.RESULTS_FIGURES_DIR / "vol_limited_bhs" / "skymapper_finders" / ids
                          / "max_exptime_table.csv")
        df_image = pd.read_csv(img_table_file)
        unique_image_ids = df_image["unique_image_id"].values
        # print(f"Downloading the FITS images for {ids} ...")
        for unique_image_id in unique_image_ids:
            # print(f"DETUID: {ids}, coords[i]: {coords[i]}")
            hdul = get_skymapper_image_fits(coords[i], box_size, unique_image_id)
            header = hdul[0].header
            band = header["FILTER"]

            out_file = (config.RESULTS_FIGURES_DIR / "vol_limited_bhs" / "skymapper_finders" /
                        ids / f"{ids}_{band}.fits")

            hdul.writeto(out_file, overwrite=True)


def main() -> None:
    for erass_id in tqdm(erass_ids):
        get_image_table(df_in, erass_id, box_size, out_root_vol_limited_bhs)


if __name__ == "__main__":
    df_in = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "vol_limited_bhs"
                        / "vol_limited_high-fxfg_candidates_w_gal_params.csv")
    df_in = df_in[df_in["dec_erass"] <= -30.0]

    coords = SkyCoord(df_in["ra_erass"].values, df_in["dec_erass"].values, unit="deg")

    erass_ids = df_in["DETUID"].values
    box_size = Quantity(1.0, "arcmin")
    out_root_vol_limited_bhs = config.RESULTS_FIGURES_DIR / "vol_limited_bhs" / "skymapper_finders"

    # main()

    get_fits_image()
