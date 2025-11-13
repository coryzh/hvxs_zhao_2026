import config
import pandas as pd
import data_schema as ds
from pathlib import Path
from log.loggers import VerboseLogger

extragalactic_patterns = [
    "Galaxy", "AGN", "AGN_Candidate", "Seyfert",
    "BLLac", "Blazar", "LINER", "LensedG", "ULX", "EmissionG"
]
xrb_patterns = "XBin"
regex = "|".join(extragalactic_patterns)


def count_simbad_types(in_file: Path, verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    logger.log(f"Loading catalogue at {in_file} ...\n")
    df = pd.read_csv(in_file)

    logger.log("Counting SIMBAD types ... \n")
    type_counts = df.value_counts(subset=ds.SimbadSchema.SIMBAD_MAIN_TYPE)
    total_simbad_match = type_counts.sum()
    df_type_counts = type_counts.to_frame().reset_index()
    df_type_counts["fraction"] = df_type_counts["count"] / total_simbad_match

    extragalactic_count = df_type_counts[df_type_counts["main_type"].str.contains(regex)]["count"].sum()
    extragalactic_frac = extragalactic_count / total_simbad_match
    xrb_count = df_type_counts[df_type_counts["main_type"].str.contains(xrb_patterns)]["count"].sum()
    xrb_frac = xrb_count / total_simbad_match

    extragalactic_row = {"main_type": "extragalactic_total", "count": extragalactic_count,
                         "fraction": extragalactic_frac}

    xrb_row = {"main_type": "xrb_total", "count": xrb_count, "fraction": xrb_frac}
    df_type_counts.loc[df_type_counts.shape[0]] = extragalactic_row
    df_type_counts.loc[df_type_counts.shape[0]] = xrb_row

    out_file = in_file.parent / f"{in_file.stem}_type_counts.csv"
    logger.log(f"Saving counts to {out_file}")
    df_type_counts.to_csv(out_file, index=True)  # Here, the index column has the type names.
    logger.end()


def main() -> None:
    in_file = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "simbad" / "hvxs_simbad.csv"
    )
    count_simbad_types(in_file, verbose=True)


if __name__ == "__main__":
    main()
