import config
from catalog.for_revision import (
    clean_simbad_types, clean_cluster_members, clean_smc_and_lmc_members,
    clean_gaia_fedility
)
from typing import Literal


def run_subsequent_cleaning(
        opt: Literal["hvxs", "control", "gold"]
) -> None:
    in_file = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / f"{opt}.csv"
    )

    in_file_simbad = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "simbad"
        / f"{opt}_simbad.csv"
    )

    df = clean_simbad_types.clean(
        in_file=in_file,
        in_file_simbad=in_file_simbad,
        out_file=None
    )

    df = clean_cluster_members.clean(df)

    df = clean_smc_and_lmc_members.clean(
        prob_thresh=0.01, opt="smc", df=df
    )

    df = clean_smc_and_lmc_members.clean(
        prob_thresh=0.002, opt="lmc", df=df
    )

    df = clean_gaia_fedility.clean(df)


if __name__ == "__main__":
    run_subsequent_cleaning()
