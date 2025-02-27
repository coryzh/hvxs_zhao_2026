import pandas as pd
import config
from log.loggers import VerboseLogger
from typing import List
from pathlib import Path
import data_schema as ds


def make_master(survey_name: str = "csc", id_x_col: str = "ID_x", verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()

    nway_dir = config.ROOT_DIR / "results" / survey_name / "catalogues" / "nway_match"

    file_survey = nway_dir / f"{survey_name}_confident_point_sources.csv"
    file_astrometry = nway_dir / f"{survey_name}_gaia_nway_match_stars_only.csv"
    file_vmin = config.RESULTS_CATALOGUE_DIR / "v_min_catalogs" / f"{survey_name}_w_v_min.csv"

    essential_files = [file_survey, file_astrometry, file_vmin]
    missing_files: List[Path] = [f for f in essential_files if not f.exists()]

    if missing_files:
        missing_file_names = [f.name for f in missing_files]
        raise FileNotFoundError(
            f"Not all required files exist for {survey_name.upper()}. Missing: {', '.join(missing_file_names)}")

    else:
        logger.log("All required files found.\n")

    logger.log(f"Loading files to DataFrames ... \n")
    df_survey = pd.read_csv(file_survey)
    df_astrometry = pd.read_csv(file_astrometry)
    df_vmin = pd.read_csv(file_vmin)

    # Renamed the Gaia ra and dec columns to avoid duplicate naming.
    df_astrometry.rename(columns={"ra": "ra_gaia", "dec": "dec_gaia"}, inplace=True)

    logger.log(f"Survey frame: {file_survey.name}, Rows: {df_survey.shape[0]}, Columns: {df_survey.shape[1]}")
    logger.log(
        f"Astrometry frame: {file_astrometry.name}, Rows: {df_astrometry.shape[0]}, Columns: {df_astrometry.shape[1]}")
    logger.log(f"Kinematics frame: {file_vmin.name}, Rows: {df_vmin.shape[0]}, Columns: {df_vmin.shape[1]}\n")

    logger.log(f"Joining Gaia and kinematics (vmin) catalogues ...")

    df_merged = pd.merge(df_astrometry, df_vmin, on=ds.Gaia.source_id, how="left")
    logger.log(f"Merged DataFrame has {df_merged.shape[0]} rows and {df_merged.shape[1]} columns.\n")

    logger.log(f"Joining with the {survey_name.upper()} source catalogue ... using {id_x_col} ...")
    if id_x_col not in df_survey.columns:
        raise KeyError(f"{id_x_col} not in the columns of {file_survey.name}.")
    # Because df_astrometry already has the X-ray ID column, df_merge has both "ID_x" and id_x_col,
    # which is a duplicate. To prevent subscripted column names produced by pd.merge, ID_x is removed for now.
    # Later in the combine_catalog.py script, the id_x_col will be renamed to "ID_x".
    df_merged.drop("ID_x", axis=1, inplace=True)
    df_merged = pd.merge(df_merged, df_survey, on=id_x_col, how="left")

    logger.log(f"Merged DataFrame has {df_merged.shape[0]} rows and {df_merged.shape[1]} columns.\n")

    out_file = config.RESULTS_CATALOGUE_DIR / "master_catalogs" / f"{survey_name}_master_catalogs.csv"
    df_merged.to_csv(out_file, index=False)
    logger.log(f"Master catalogue of {survey_name.upper()} saved to {out_file}.\n")
    logger.end()


def main() -> None:
    survey_names = ["csc", "xmm", "swift", "erass"]

    for s in survey_names:
        schema = ds.SCHEMA_DICT[s]
        make_master(survey_name=s, id_x_col=schema.ID, verbose=True)


if __name__ == "__main__":
    main()
