import config
import pandas as pd
from log.loggers import VerboseLogger
from astropy.io import fits
from astropy.table import Table


def clean(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    hdul_halo_ids = fits.open(
        str(
            config.DATA_DIR.parent
            / "others"
            / "catalogues"
            / "halo_sources_gaia_ids_viswanathan+23.fits.fit"
        )
    )
    data = hdul_halo_ids[1].data
    tab = Table(data)
    df_halo_ids = tab.to_pandas()

    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    logger.log(f"Catalogue loaded. {df.shape[0]} sources loaded.\n")
    logger.log(
        "Joining the loaded catalogue with the halo source_id catalogue ...\n"
    )
    df_joined = pd.merge(
        df, df_halo_ids, left_on="source_id", right_on="GaiaDR3", how="inner"
    )

    logger.log(f"{df_joined.shape[0]} found in the halo source catalogue.\n")

    logger.log("Removing likely halo sources ... \n")
    _filter = ~df["source_id"].isin(df_joined["GaiaDR3"])
    df_cleaned = df[_filter]

    logger.log(f"{df_cleaned.shape[0]} sources remained after cleaning.\n")
    logger.end()

    return df_cleaned


def main() -> None:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources" / "combined_vpec_lolim_gt_200_unique_stage_9.csv"
    )
    df = pd.read_csv(in_file)

    df_cleaned = clean(df, verbose=True)

    df_cleaned.to_csv(
        in_file.parent / f"{in_file.stem}.csv".replace("stage_9", "stage_9a")
    )


if __name__ == "__main__":
    main()
