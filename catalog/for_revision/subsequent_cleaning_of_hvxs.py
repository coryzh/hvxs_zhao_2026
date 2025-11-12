import config
from catalog.for_revision import (
    clean_simbad_types, clean_cluster_members, clean_smc_and_lmc_members,
    clean_gaia_fedility
)


def run_subsequent_cleaning() -> None:
    in_file = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "hvxs_catalogue_vpecmin_lo_gt_200.csv"
    )

    in_file_simbad = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "simbad"
        / "hvxs_simbad.csv"
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
