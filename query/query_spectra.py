import config
import pandas as pd
import astropy.units as u
from astroquery.sdss import SDSS
# from astroquery.esasky import ESASky
from log.loggers import VerboseLogger
from astropy.coordinates import SkyCoord


def query_sdss(df: pd.DataFrame, verbose: bool = False, download_spectra: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    logger.log(f"Loading input catalogue ...")
    logger.log(f"{df.shape[0]} sources loaded.\n")
    ra = df["ra"].values
    dec = df["dec"].values

    coords = SkyCoord(ra, dec, frame="icrs", unit="deg")
    logger.log(f"Querying the SDSS archive for sources with spectroscopy matches ...")
    results = SDSS.query_region(coords, radius=5. * u.arcsec, spectro=True)
    logger.log("Done")
    logger.log(f"{len(results)} matches found.\n")

    if download_spectra:
        logger.log(f"Retrieving spectra for {len(results)} matches ...")
        hdul = SDSS.get_spectra(matches=results)

    logger.end()


def query_lamost(df: pd.DataFrame, verbose: bool = False, download_spectra: bool = False) -> None:
    coords = SkyCoord(df.ra, df.dec, frame="icrs", unit="deg")
    pass


def main() -> None:
    df_targets = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources"
                             / "vlt_p115" / "vlt_p115_targets_curated.csv")

    query_sdss(df_targets, verbose=True)


if __name__ == "__main__":
    main()
