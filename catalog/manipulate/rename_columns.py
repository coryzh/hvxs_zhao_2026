import pandas as pd
import config
import data_schema as ds
from log.loggers import VerboseLogger


def rename_distance_cols(verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    catalog_in_dir = config.RESULTS_CATALOGUE_DIR / "master_catalogs"

    logger.begin()
    for _name in config.SURVEY_NAMES_SHORT:
        logger.log(
            f"Updating distance columns for the {_name.upper()} catalogue.\n"
        )

        catalog_in = catalog_in_dir / f"{_name}_master_catalog.csv"
        df = pd.read_csv(catalog_in)

        df = df.rename(
            columns={
                ds.BailerJonesSchema.r_med_photogeo: "dist_med",
            }
        )

        df["e_dist"] = df["dist_med"] - df[ds.BailerJonesSchema.r_lo_photogeo]
        df["E_dist"] = df[ds.BailerJonesSchema.r_hi_photogeo] - df["dist_med"]

        df_cleaned = df.drop(
            columns=[
                ds.BailerJonesSchema.r_hi_photogeo,
                ds.BailerJonesSchema.r_lo_photogeo
            ]
        )

        logger.log(f"Overwritting the input {_name.upper()} catalogue ...\n")
        df_cleaned.to_csv(catalog_in, index=False)
        logger.end()


def main() -> None:
    rename_distance_cols(verbose=True)


if __name__ == "__main__":
    main()
