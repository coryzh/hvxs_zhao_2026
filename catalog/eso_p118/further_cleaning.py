import pandas as pd
import argparse
from pathlib import Path
from catalog.for_revision import (
    clean_cluster_members, clean_smc_and_lmc_members, clean_simbad_types
)


def _load_catalogue(catalogue_path: Path) -> pd.DataFrame:
    """
    Load the master X-ray source catalogue.
    """

    df = pd.read_csv(catalogue_path)
    print(
        f"{df.shape[0]} sources loaded from {catalogue_path}."
    )
    return df


def run_cleaning_pipeline(
        catalog_path: Path, simbad_path: Path
) -> pd.DataFrame:
    """
    Run the cleaning pipeline on the input DataFrame.

    Parameters:
    catalog_path (Path): Path to the master catalogue CSV file.
    simbad_path (Path): Path to the cross-matched SIMBAD information CSV file.

    Returns:
    pd.DataFrame: Cleaned DataFrame.
    """
    # Step 1: Clean cluster members
    df = _load_catalogue(catalog_path)
    df_cleaned = clean_cluster_members.clean(df)

    print(
        f"{df_cleaned.shape[0]} sources remain after cleaning cluster members."
    )

    # Step 2: Clean SMC and LMC members
    df_cleaned = clean_smc_and_lmc_members.clean(
        df_cleaned, opt="smc", prob_thresh=0.01
    )
    df_cleaned = clean_smc_and_lmc_members.clean(
        df_cleaned, opt="lmc", prob_thresh=0.002
    )

    print(
        f"{df_cleaned.shape[0]} sources remain after cleaning SMC and LMC "
        " members."
    )

    # Step 3: Clean SIMBAD types
    df_cleaned = clean_simbad_types.clean(
        catalog_path, simbad_path, out_file=None
    )

    print(
        f"{df_cleaned.shape[0]} sources remain after cleaning SIMBAD types."
    )

    return df_cleaned


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Clean the master catalogue by removing cluster members and "
            "SMC/LMC members."
        )
    )
    parser.add_argument(
        "catalogue_path",
        type=Path,
        help="Path to the master catalogue CSV file."
    )
    parser.add_argument(
        "simbad_path",
        type=Path,
        help="Path to the SIMBAD information CSV file."
    )
    parser.add_argument(
        "output_path",
        type=Path,
        help="Path to save the cleaned catalogue CSV file."
    )

    args = parser.parse_args()

    # Run the cleaning pipeline
    df_cleaned = run_cleaning_pipeline(args.catalogue_path, args.simbad_path)
    df_cleaned = df_cleaned.sort_values(
        by=["ID_x", "ra_x"], ascending=[True, True]
    )
    # Save the cleaned catalogue
    df_cleaned.to_csv(args.output_path, index=False)
    print(f"Cleaned catalogue saved to {args.output_path}.")


if __name__ == "__main__":
    main()
