import pandas as pd
from astropy.io import fits
from astropy.wcs import WCS
from regions import CircleSkyRegion
from astropy.coordinates import SkyCoord
from pathlib import Path
from astropy.visualization import simple_norm
# from astropy.units import Quantity
# from astropy.nddata import Cutout2D
from utils.finder import set_figure, set_axis
from tqdm import tqdm
import config
import matplotlib.pyplot as plt
import astropy.units as u


def make_finder(df: pd.DataFrame, detuid: str, band: str, out_file: Path = None) -> None:

    df_copy = df.copy()
    df_copy.set_index("DETUID", inplace=True)
    row = df_copy.loc[detuid]
    ra = row["ra_erass"]
    dec = row["dec_erass"]
    ra_gaia = row["ra"]
    dec_gaia = row["dec"]

    pos_err = row["pos_err_erass"] * u.arcsec
    coord = SkyCoord(ra, dec, unit="deg")
    coord_gaia = SkyCoord(ra_gaia, dec_gaia, unit="deg")

    # Load the image from the file.
    img_file = config.RESULTS_FIGURES_DIR / "high-v_sources" / "vlt_p115" / detuid / f"{detuid}_{band}.fits"
    hdul = fits.open(img_file)
    img_data = hdul[0].data

    # Set the figure and axis.
    wcs = WCS(hdul[0].header)
    fig, ax = set_figure(wcs)
    set_axis(ax)

    # Display the image.
    norm = simple_norm(img_data, "sqrt")
    ax.imshow(img_data, cmap="Greys", origin="lower", norm=norm)

    # Add the error circles.
    erass_1sigma_circle = CircleSkyRegion(center=coord, radius=pos_err)
    erass_1sigma_circle_pix = erass_1sigma_circle.to_pixel(wcs)
    erass_1sigma_circle_pix.plot(ax=ax, edgecolor='b', facecolor='none', lw=1.2)

    erass_2sigma_circle = CircleSkyRegion(center=coord, radius=2 * pos_err)
    erass_2sigma_circle_pix = erass_2sigma_circle.to_pixel(wcs)
    erass_2sigma_circle_pix.plot(ax=ax, edgecolor='b', facecolor='none', lw=1.2, ls="--")

    # Indicate the Gaia counterpart.
    ax.scatter(ra_gaia, dec_gaia, transform=ax.get_transform('icrs'), s=400, marker="o", lw=2.5,
               edgecolor="r", facecolor="none")

    if out_file is not None:
        plt.savefig(out_file)
        print(f"Finding chart saved to {out_file}")

    plt.close(fig)


def main() -> None:
    df_in = pd.read_csv(config.RESULTS_CATALOGUE_DIR /
                        "vol_limited_bhs" / "vol_limited_targets_dist_lt_1.0_lx_gt_1e+32_det_like_gt_5.0.csv")

    df_in = df_in[df_in["dec_erass"] <= -30.0]

    detuids = df_in["DETUID"].values
    bands = ["g", "r", "i", "z"]

    for detuid in tqdm(detuids):
        for band in bands:
            out_file = (config.RESULTS_FIGURES_DIR / "vol_limited_bhs" / "skymapper_finders"
                        / detuid / f"{detuid}_{band}_finder.pdf")
            make_finder(df_in, detuid, band, out_file)


if __name__ == "__main__":
    main()
