import pandas as pd
import astropy.units as u
from astropy.coordinates import SkyCoord
from pathlib import Path
from constants import gal_cen
import config


def add_galactic_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    coords = SkyCoord(df["ra"], df["dec"], frame="icrs", unit="deg")

    coords_gal = coords.galactic
    df["l"] = coords_gal.l.value
    df["b"] = coords_gal.b.value

    return df


def add_cartesian_coordinates(in_file: Path) -> None:
    df = pd.read_csv(in_file)

    coords = SkyCoord(
        df.ra_gaia.values * u.deg, df.dec_gaia.values * u.deg,
        distance=df.dist_med.values * u.kpc,
        frame="icrs"
    )

    coords_galcen = coords.transform_to(gal_cen)

    x, y, z = (coords_galcen.x.value,
               coords_galcen.y.value,
               coords_galcen.z.value)

    coords_galcen.representation_type = "cylindrical"
    r_gc = coords_galcen.rho.value

    coord_cols = ["x", "y", "z", "r_gc"]
    coord_arrs = [x, y, z, r_gc]
    for name, arr in zip(coord_cols, coord_arrs):
        df[name] = arr

    out_file = (in_file.parent
                / f"{in_file.stem}.csv".replace("stage_7", "stage_8"))

    df.to_csv(out_file, index=False)


def add_hex_equatorial_coordinates(df: pd.DataFrame,
                                   sort: bool = False) -> pd.DataFrame:

    coords = SkyCoord(df["ra"], df["dec"], frame="icrs", unit="deg")

    df["ra_hex"] = coords.ra.to_string(
        unit=u.hourangle, sep=":", precision=3, pad=True
    )
    df["dec_hex"] = coords.dec.to_string(
        unit="deg", precision=2, sep=":", alwayssign=True, pad=True
    )

    if sort:
        df = df.sort_values(by="ra")

    return df


def add_erass_iauname(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add IAUNAME based on the X-ray coordinates of eRASS
    N.B.: the IAUNAME rendered this way may not be consistent with those in
    eRASS.
    It's better to use the original IAUNAMEs to reduce confusion.
    """

    coords = SkyCoord(
        df["ra_erass"], df["dec_erass"], frame="icrs", unit="deg"
    )
    ra_hex = coords.ra.to_string(
        unit=u.hourangle, sep="", precision=1, pad=True
    )
    dec_hex = coords.dec.to_string(
        unit="deg", precision=0, sep="", alwayssign=True, pad=True
    )

    iauname = [
        f"1eRASS J{ra_str}{dec_str}"
        for ra_str, dec_str in zip(ra_hex, dec_hex)
    ]

    df["iauname"] = iauname

    return df


def main() -> None:
    in_file = (config.RESULTS_CATALOGUE_DIR
               / "control_sample"
               / "control_sample_stage_7.csv")

    add_cartesian_coordinates(in_file)
    # df.to_csv(config.RESULTS_CATALOGUE_DIR /
    #  "control_sample_simbad_cleaned.csv")


if __name__ == "__main__":
    main()
