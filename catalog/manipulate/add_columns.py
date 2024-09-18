import pandas as pd
import astropy.units as u
from astropy.coordinates import SkyCoord


def add_galactic_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    coords = SkyCoord(df["ra"], df["dec"], frame="icrs", unit="deg")

    coords_gal = coords.galactic
    df["l"] = coords_gal.l.value
    df["b"] = coords_gal.b.value

    return df


def add_hex_equatorial_coordinates(df: pd.DataFrame, sort: bool = False) -> pd.DataFrame:
    coords = SkyCoord(df["ra"], df["dec"], frame="icrs", unit="deg")

    df["ra_hex"] = coords.ra.to_string(unit=u.hourangle, sep=":", precision=3, pad=True)
    df["dec_hex"] = coords.dec.to_string(unit="deg", precision=2, sep=":", alwayssign=True, pad=True)

    if sort:
        df = df.sort_values(by="ra")

    return df


def add_erass_iauname(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add IAUNAME based on the X-ray coordinates of eRASS
    N.B.: the IAUNAME rendered this way may not be consistent with those in eRASS.
    It's better to use the original IAUNAMEs to reduce confusion.
    """

    coords = SkyCoord(df["ra_erass"], df["dec_erass"], frame="icrs", unit="deg")
    ra_hex = coords.ra.to_string(unit=u.hourangle, sep="", precision=1, pad=True)
    dec_hex = coords.dec.to_string(unit="deg", precision=0, sep="", alwayssign=True, pad=True)

    iauname = [f"1eRASS J{ra_str}{dec_str}" for ra_str, dec_str in zip(ra_hex, dec_hex)]
    df["iauname"] = iauname

    return df
