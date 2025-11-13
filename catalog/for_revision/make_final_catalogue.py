from sklearn import logger
import config
import pandas as pd
import argparse
from catalog.for_revision import (
    clean_simbad_types, clean_cluster_members, clean_smc_and_lmc_members,
    clean_gaia_fedility
)
from catalog.for_revision.final_touches import (
    transform_distance_columns, add_cartesian_coordinates, add_quality_bitmask
)
from typing import Literal, Dict
from pathlib import Path


def _get_file_paths(
        opt: str = Literal["hvxs", "control", "gold"]
) -> Dict[str, Path]:

    file_path_dict = {
        "base": config.RESULTS_CATALOGUES_FOR_REVISION / opt / f"{opt}.csv",
        "simbad": (
            config.RESULTS_CATALOGUES_FOR_REVISION
            / "simbad" / "simbad.csv"
        ),
        "ready": (
            config.RESULTS_CATALOGUES_FOR_REVISION / "ready_catalogues"
            / f"{opt}.csv"
        )
    }
    return file_path_dict


def run_subsequent_cleaning(
        opt: Literal["hvxs", "control", "gold"]
) -> pd.DataFrame:

    paths = _get_file_paths(opt=opt)
    in_file = paths["base"]
    in_file_simbad = paths["simbad"]

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

    return df


def final_touches_pipeline(
        df: pd.DataFrame
) -> pd.DataFrame:
    df = transform_distance_columns(df)

    df = add_cartesian_coordinates(df)

    df = add_quality_bitmask(df)

    return df


def _save_to_file(df: pd.DataFrame, opt: str) -> None:
    path_dict = _get_file_paths(opt=opt)
    out_path = path_dict["ready"]

    if not out_path.parent.exists():
        logger.info(f"Creating directory {out_path.parent} ...")
        out_path.parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(out_path, index=False)

    logger.info(f"Saved final catalogue to {out_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="make_final_catalogue",
        description=(
            "Run subsequent cleaning and final touches on the "
            "HVXS, control, or gold catalogues."
        )
    )
    parser.add_argument(
        "opt", choices=["hvxs", "control", "gold"],
        help="Option to specify which catalogue to process"
    )

    args = parser.parse_args()

    df = run_subsequent_cleaning(opt=args.opt)
    df_final = final_touches_pipeline(df)
    _save_to_file(df_final, opt=args.opt)
