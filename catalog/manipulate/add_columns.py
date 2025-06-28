import pandas as pd
import astropy.units as u
from astropy.coordinates import SkyCoord
from pathlib import Path
from constants import gal_cen
import config
from utils.distances import FromLiterature
from utils.utility_functions import get_errors


def add_galactic_coordinates(df: pd.DataFrame) -> pd.DataFrame:
    coords = SkyCoord(df["ra"], df["dec"], frame="icrs", unit="deg")

    coords_gal = coords.galactic
    df["l"] = coords_gal.l.value
    df["b"] = coords_gal.b.value

    return df


def add_cartesian_coordinates(in_file: Path) -> None:
    df = pd.read_csv(in_file)
    df_copy = df.copy()
    duplicated_cols_to_check = ["x", "y", "z", "r_gc"]
    duplicated_cols = [
        col for col in duplicated_cols_to_check if col in df_copy.columns
    ]
    df_copy = df_copy.drop(columns=duplicated_cols)

    def get_coords(row: pd.Series):
        dist = FromLiterature(
            row['dist_med'],
            x_lo=row['dist_med'] - row['e_dist'],
            x_hi=row['dist_med'] + row['E_dist']
        )
        d_gamma = dist.fit_gamma()["distribution"]
        d_rand = d_gamma.rvs(1000)
        coords = SkyCoord(
            row['ra_gaia'] * u.deg, row['dec_gaia'] * u.deg,
            distance=d_rand * u.kpc,
            frame="icrs"
        )

        coords_galcen = coords.transform_to(gal_cen)

        x, y, z = (
            coords_galcen.x.value,
            coords_galcen.y.value,
            coords_galcen.z.value
        )

        coords_galcen.representation_type = "cylindrical"
        r_gc = coords_galcen.rho.value

        row_values = []
        for item in [x, y, z, r_gc]:
            med, uperr, loerr = get_errors(item)
            row_values.extend([med, uperr, loerr])
        return row_values

    coord_cols = [
        "x_med", "e_x", "E_x",
        "y_med", "e_y", "E_y",
        "z_med", "e_z", "E_z",
        "r_gc", "e_r_gc", "E_r_gc"
    ]

    coord_df = df_copy.apply(get_coords, axis=1, result_type='expand')
    coord_df.columns = coord_cols
    df_concat = pd.concat([df_copy, coord_df], axis=1, )

    out_file = (in_file.parent
                / f"{in_file.stem}_c.csv")

    df_concat.to_csv(out_file, index=False)


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


def add_qulity_bitmask(df: pd.DataFrame) -> pd.DataFrame:
    # cond_1 = (df["n_neighbours_2sigma"] < 2)
    cond_1 = (df["sep_x_g"] / df["pos_x_err"] <= 1)
    cond_2 = (df["parallax_corr"] / df["parallax_error"] >= 5)
    cond_3 = (
        (abs(1 / df["parallax_corr"] - df["dist_med"])
         / df["dist_med"] <= 0.2) & df["parallax_corr"] > 0
    )

    df["quality"] = (
        cond_1.astype(int) * (1 << 2) +
        cond_2.astype(int) * (1 << 1) +
        cond_3.astype(int) * (1 << 0)
    )

    return df


def main() -> None:
    in_file = (config.RESULTS_CATALOGUE_DIR
               / "ready_catalogues"
               / "control.csv")
    # df = pd.read_csv(in_file)
    add_cartesian_coordinates(in_file=in_file)
    # df = add_qulity_bitmask(df)

    # df.to_csv(
    #     config.RESULTS_CATALOGUE_DIR
    #     / "high-v_sources"
    #     / "hvxs_vpec_lo_gt_200_2sigma_one_neighbour_w_bitmask.csv"
    # )
    # print(df.value_counts(subset=["quality"]))

    # add_cartesian_coordinates(in_file)
    # df.to_csv(config.RESULTS_CATALOGUE_DIR /
    #  "control_sample_simbad_cleaned.csv")


if __name__ == "__main__":
    main()
