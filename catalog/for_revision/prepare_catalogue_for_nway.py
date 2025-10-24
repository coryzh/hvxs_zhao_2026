import pandas as pd
from astropy.table import Table
from pathlib import Path
from astropy.io import fits
from log.log_config import configure_logging
import logging
import argparse


def prepare_table(
        in_file_csv: Path, id_col_name: str = "id",
        ra_col: str = "ra", dec_col: str = "dec",
        pos_err_col: str = "pos_err",
        sky_area: float = 2.0, data_extension_name: str = "data"
) -> None:
    # Step 1: Convert DataFrame to Astropy Table
    logger.info(f"1. Reading input CSV file: {in_file_csv} ...")
    df = pd.read_csv(in_file_csv)

    logger.info(f"Input catalogue has {df.shape[0]} rows.")

    # Step 2: Remove duplicates (you want to make sure the input catalogues to
    # NWAY has no duplicated IDs, which could render confusing results).
    n_duplicates = df.duplicated(subset=id_col_name).sum()
    logger.info(
        "2. Checking for duplicated entries based on "
        f"{id_col_name} column ..."
    )

    if n_duplicates > 0:
        logger.info(
            f"Found {n_duplicates} duplicated entries."
        )
        df = df.drop_duplicates(subset=id_col_name, keep="first")

    else:
        logger.info("No duplicated entries found. Good to go next step.")

    # Step 3: Keep only the required columns.
    cols_required = [id_col_name, ra_col, dec_col, pos_err_col]
    logger.info(f"3. Keeping only the required columns: {cols_required} ...")
    df = df[cols_required]

    # Step 4: Convert to FITS BinTableHDU.
    logger.info("4. Converting the DataFrame to FITS BinTableHDU ...")
    astropy_table = Table.from_pandas(df)
    primary_hdu = fits.PrimaryHDU()
    hdu_table = fits.BinTableHDU(astropy_table)

    # Step 5: Adding 'SKYAREA' keyword to the header.
    logger.info(
        "5. Adding 'SKYAREA' keyword to the FITS header, "
        f"using value: {sky_area} ..."
    )
    hdu_table.header["SKYAREA"] = sky_area

    # Step 6: Update the extension name
    logger.info(
        "6. Updating the data extension name to "
        f"'{data_extension_name}' ..."
    )
    hdu_table.header['EXTNAME'] = data_extension_name

    # Step 7: Creating the HDUL
    logger.info("7. Creating the FITS HDUList ...")
    hdul = fits.HDUList([primary_hdu, hdu_table])

    # Step 8: Write the table to a FITS file
    logger.info("8. Writing the FITS file ...")
    fits_file = in_file_csv.parent / f"{in_file_csv.stem}.fits"
    hdul.writeto(fits_file, overwrite=True)
    logger.info(f"FITS file saved to: {fits_file}")


if __name__ == "__main__":
    logger = logging.getLogger(Path(__file__).stem)
    configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
    parser = argparse.ArgumentParser(
        prog="prepare_catalogue_for_nway",
        description=(
            "Prepare a source catalogue CSV file for NWAY cross-matching "
            "by converting it to FITS format with required columns and "
            "header keywords."
        )
    )

    parser.add_argument(
        "infile", help="Input CSV file containing the source catalogue"
    )

    parser.add_argument(
        "--id_col", required=False, default="id",
        help="Name of the ID column in the input catalogue"
    )

    parser.add_argument(
        "--ra_col", required=False, default="ra",
        help="Name of the RA column in the input catalogue"
    )

    parser.add_argument(
        "--dec_col", required=False, default="dec",
        help="Name of the Dec column in the input catalogue"
    )

    parser.add_argument(
        "--pos_err_col", required=False, default="pos_err",
        help="Name of the positional error column in the input catalogue"
    )

    parser.add_argument(
        "--sky_area", required=False, type=float, default=2.0,
        help="Sky area covered by the catalogue in square degrees"
    )

    parser.add_argument(
        "--data_ext_name", required=False, default="data",
        help="Name of the data extension in the output FITS file"
    )

    args = parser.parse_args()
    in_file_path = Path(args.infile)

    prepare_table(
        in_file_csv=in_file_path,
        id_col_name=args.id_col,
        ra_col=args.ra_col,
        dec_col=args.dec_col,
        pos_err_col=args.pos_err_col,
        sky_area=args.sky_area,
        data_extension_name=args.data_ext_name
    )
