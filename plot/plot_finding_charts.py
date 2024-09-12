from query.panstarrs_images import geturl, getcolorim
import pandas as pd
import config
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from astropy.io import fits
from astropy.visualization import PercentileInterval, AsinhStretch
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
from regions import CircleSkyRegion
import astropy.units as u
import warnings
from tqdm import tqdm


def make_panstarrs_greyscale_finder(ra: float, dec: float, pos_err: float = 5.0, size: float = 240, filters: str = "g",
                                    title: str = None, ra_counterpart: float = None, dec_counterpart: float = None,
                                    out_file: Path = None) -> None:
    fitsurl = geturl(ra, dec, size, img_format="fits", filters=filters)

    if len(fitsurl) > 0:
        hdu = fits.open(fitsurl[0])
        wcs = WCS(hdu[0])
        data = hdu[0].data
        data[np.isnan(data)] = 0.0
        transform = AsinhStretch() + PercentileInterval(99.5)
        data_t = transform(data)

        plt.style.use("mycustomised")
        _fig = plt.figure(figsize=(10, 10))
        ax = plt.subplot(1, 1, 1, projection=wcs)
        ax.imshow(data_t, origin='lower', cmap='YlOrBr')

        coord = SkyCoord(ra, dec, frame='icrs', unit=(u.deg, u.deg))
        circle_region = CircleSkyRegion(center=coord, radius=pos_err * u.arcsec)
        circle_region_pix = circle_region.to_pixel(wcs)
        circle_region_pix.plot(ax=ax, edgecolor='r', facecolor='none', lw=1)

        ax.scatter(coord.ra.deg, coord.dec.deg, transform=ax.get_transform('icrs'),
                   s=50, marker='x', facecolor='r', edgecolor='r')

        ax.scatter(ra_counterpart, dec_counterpart, transform=ax.get_transform('icrs'), s=40, marker="o",
                   edgecolor="w", facecolor="g")

        ax.set_xlabel(r'$\alpha$')
        ax.set_ylabel(r'$\delta$')

        ax.set_title(title, fontsize=25)

        if out_file is not None:
            plt.savefig(out_file)
            print(f"Finding chart saved to {out_file}")

    else:
        print(f"No PanSTARRS image found for ra={ra}, dec={dec}.")


def make_panstarrs_rgb_finder(ra: float, dec: float, pos_err: float = 5.0, size: float = 240, filters: str = "gri",
                              title: str = None, ra_counterpart: float = None, dec_counterpart: float = None,
                              out_file: Path = None) -> bool:
    # Get image url for the "g" filter. This is used to (1) check if the image exists and (2) to get the WCS.
    img_urls = geturl(ra, dec, size, img_format="fits", filters="g")
    if len(img_urls) > 0:
        img = getcolorim(ra, dec, size, filters=filters, img_format="jpg")
        hdul = fits.open(img_urls[0])
        wcs = WCS(hdul[0].header)

        plt.style.use("mycustomised")
        _fig = plt.figure(figsize=(10, 10))
        ax = plt.subplot(1, 1, 1, projection=wcs)
        ax.imshow(img, origin='lower', extent=(0, size, 0, size))

        coord = SkyCoord(ra, dec, frame='icrs', unit=(u.deg, u.deg))
        circle_region_1sigma = CircleSkyRegion(center=coord, radius=pos_err * u.arcsec)
        circle_region_1sigma_pix = circle_region_1sigma.to_pixel(wcs)

        circle_region_1sigma_pix.plot(ax=ax, edgecolor='w', facecolor='none', lw=2.5)

        circle_region_2sigma = CircleSkyRegion(center=coord, radius=2 * pos_err * u.arcsec)
        circle_region_2sigma_pix = circle_region_2sigma.to_pixel(wcs)
        circle_region_2sigma_pix.plot(ax=ax, edgecolor='w', facecolor='none', lw=2.5, ls="--")

        ax.scatter(coord.ra.deg, coord.dec.deg, transform=ax.get_transform('icrs'),
                   s=50, marker='x', facecolor='r', edgecolor='r')

        ax.scatter(ra_counterpart, dec_counterpart, transform=ax.get_transform('icrs'), s=100, marker="o", lw=2.5,
                   edgecolor="cyan", facecolor="none")

        ax.set_xlabel(r'$\alpha$')
        ax.set_ylabel(r'$\delta$')

        ax.set_title(title, fontsize=25)

        if out_file is not None:
            plt.savefig(out_file)
            print(f"Finding chart saved to {out_file}")

        return True

    else:
        print(f"No enough image cutouts found.")
        return False


def main() -> None:
    warnings.filterwarnings("ignore")
    out_src_list = []
    in_file = (config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "vlt_p115_targets.csv")
    df = pd.read_csv(in_file)
    for i, row in tqdm(df.iterrows()):
        ra = row["ra_x"]
        dec = row["dec_x"]
        ra_counterpart = row["ra"]
        dec_counterpart = row["dec"]
        pos_err = row["pos_err_erass"]
        # source_id = row["source_id"]
        detuid = row["DETUID"]

        # out_root = config.RESULTS_FIGURES_DIR / "panstarrs_finders" / "runaway_sample_vpec_gt_200" / "rgb"
        out_root = config.RESULTS_FIGURES_DIR / "vol_limited_bhs" / "panstarrs_finders" / "rgb"
        out_file = out_root / f"{detuid}_panstarrs_finder_rgb.pdf"
        print(f"Making RGB finding chart for {detuid} ...")
        response = make_panstarrs_rgb_finder(ra, dec, pos_err, title=detuid, out_file=out_file,
                                             ra_counterpart=ra_counterpart, dec_counterpart=dec_counterpart)

        if response:
            out_src_list.append(row["DETUID"])

    df_src_list = pd.DataFrame(out_src_list, columns=["DETUID"])
    df_src_list.to_csv("source_list.csv", index=False)
    # make_panstarrs_greyscale_finder(ra, dec, pos_err, title=detuid, out_file=out_file,
    #                                 ra_counterpart=ra_counterpart, dec_counterpart=dec_counterpart)
    # rgb_out_file = out_root / "rgb" / f"{detuid}_panstarrs_finder_rgb.jpg"
    # im.save(rgb_out_file)
    # print(f"RGB Finding chart for {detuid} saved to {rgb_out_file}.")


if __name__ == "__main__":
    main()
