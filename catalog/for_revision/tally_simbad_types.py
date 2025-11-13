import config
import pandas as pd
import data_schema as ds
from pathlib import Path
from log.log_config import configure_logging
from typing import Literal
import logging


configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


main_type_dict = {
    "extractagalactic": [
        "QSO", "QSO_Candidate", "AGN", "Galaxy", "AGN_Candidate", "Seyfert1",
        "BLLac", "RadioG", "GtowardsCl", "Seyfert2", "Blazar", "LINER",
        "LensedG", "ClG", "Blazar_Candidate", "GroupG", "BrightestCG"
    ],
    "galactic": [
        "CataclyV*", "CataclyV*_Candidate", "Nova", "OrionV*", "YSO",
        "TTauri*", "SNRemnant", "**", "BYDraV*", "YSO_Candidate"
    ],
    "xrb": [
        "HighMassXBin", "LowMassXBin", "XrayBin"
    ],
    "pulsar": [
        "Pulsar", "Pulsar_Candidate"
    ],
    "xray_source": [
        "X"
    ],
    "star": [
        "Star",
    ],
    "high-pm": [
        "HighPM*",
    ]
}


def tally_simbad_types(
        df_simbad: pd.DataFrame,
        option: Literal[
            "galactic", "extragalactic", "xrb",
            "pulsar", "xray_source", "star", "high-pm"
        ]
) -> tuple[int, float]:
    main_types = main_type_dict[option]

    df_type_counts = df_simbad.value_counts(
        subset=ds.SimbadSchema.SIMBAD_MAIN_TYPE
    ).reset_index(name="counts")
    total_simbad_match = df_type_counts["counts"].sum()

    df_type_counts["fraction"] = df_type_counts["counts"] / total_simbad_match

    selected_count = df_type_counts[
        df_type_counts["main_type"].isin(main_types)
    ]["counts"].sum()
    selected_frac = selected_count / total_simbad_match

    logger.info(
        f"Total {option} SIMBAD types count: {selected_count}, "
        f"fraction: {selected_frac:.2f}"
    )

    return selected_count, selected_frac


def make_tally_table(
        df_simbad: pd.DataFrame
) -> None:
    df_tally = pd.DataFrame(columns=["category", "counts", "fraction"])

    for category in main_type_dict.keys():
        type_count, type_fraction = tally_simbad_types(
            df_simbad=df_simbad, option=category
        )

        df_tally = pd.concat(
            [
                df_tally,
                pd.DataFrame(
                    {
                        "category": [category],
                        "counts": [type_count],
                        "fraction": [type_fraction * 100.0],
                    }
                )
            ],
            ignore_index=True
        )

    out_file = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "simbad" / "hvxs_simbad_tally.csv"
    )
    df_tally.to_csv(
        out_file, index=False
    )

    logger.info(
        f"Tally table saved to {out_file}."
    )


def entry_point() -> None:
    file_simbad = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "simbad" / "hvxs_simbad.csv"
    )
    df_simbad = pd.read_csv(file_simbad)
    logger.info(f"SIMBAD data loaded: {df_simbad.shape[0]} rows.")

    make_tally_table(df_simbad=df_simbad)


if __name__ == "__main__":
    entry_point()
