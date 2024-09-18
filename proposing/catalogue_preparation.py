import config
import pandas as pd
from catalog.manipulate import add_columns
from log.loggers import VerboseLogger
from utils.convert_gaia_magnitudes import g_to_johnson_for_eso


def prepare_catalogue(verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    in_file = config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "vlt_p115" / "vlt_p115_targets_curated.csv"
    df = pd.read_csv(in_file)
    logger.log(f"Catalogue loaded: {df.shape[0]} sources.\n")

    out_columns = ["Name", "RA", "Dec", "System", "Mag", "pmra_arcsec", "pmdec_arcsec", "Epoch", "Plx"]
    df_out = pd.DataFrame(columns=out_columns)

    logger.log(f"Getting names ... \n")
    df_out["Name"] = df["ID_x"]

    logger.log(f"Adding columns: galactic coordinates and hexadecimal coordinates ...")
    df = add_columns.add_galactic_coordinates(df)
    df = add_columns.add_hex_equatorial_coordinates(df, sort=True)
    df_out["RA"] = df["ra_hex"]
    df_out["Dec"] = df["dec_hex"]
    logger.log(f"New columns added.\n")

    logger.log(f"Setting the System column to 'ICRS'\n")
    df_out["System"] = "ICRS"

    logger.log(f"Getting magnitudes ...\n")
    df_out["Mag"] = df.apply(g_to_johnson_for_eso, axis=1)

    logger.log(f"Getting proper motion values from the input catalogue ...\n")
    df_out["pmra_arcsec"] = df["pmra"] / 1e3
    df_out["pmdec_arcsec"] = df["pmdec"] / 1e3

    logger.log(f"Setting Epoch ... \n")
    df_out["Epoch"] = 2016

    logger.log(f"Getting parallax values from the input catalogue ...\n")
    df_out["Plx"] = df["parallax"]

    out_file = in_file.parent / "vlt_p115_targets_curated_for_eso.csv"
    df_out.round(3).to_csv(out_file, index=False)
    logger.log(f"Catalogue saved to {out_file}.\n")
    logger.end()


def main() -> None:
    prepare_catalogue(verbose=True)


if __name__ == "__main__":
    main()
