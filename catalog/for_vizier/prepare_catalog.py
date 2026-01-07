import pandas as pd
import config
from typing import Literal
from argparse import ArgumentParser


def _load_catalog(
        opt: Literal["hvxs", "control", "gold"]
) -> pd.DataFrame:
    df = pd.read_csv(
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "ready_catalogues"
        / f"{opt}.csv"
    )

    return df


def select_columns(df: pd.DataFrame) -> pd.DataFrame:
    columns = [
        "ID_x", "source_id", "ra_gaia", "dec_gaia", "ra_x", "dec_x",
        "sep_x_g", "pos_x_err", "dist_med", "e_dist", "E_dist",
        "f_x", "f_x_err", "phot_g_mean_mag", "bp_rp", "fx_fg", "fx_fg_err",
        "vpec_gamma_min_med", "e_vpec_gamma_min", "E_vpec_gamma_min",
        "vpec_min_med", "e_vpec_min", "E_vpec_min", "quality"
    ]

    df_selected = df[columns]
    return df_selected


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    column_mapping = {
        "ra_gaia": "ra", "dec_gaia": "dec",
    }

    df = df.rename(columns=column_mapping)
    return df


def sort_by_ra(df: pd.DataFrame) -> pd.DataFrame:
    df_sorted = df.sort_values(by="ra", ascending=True).reset_index(drop=True)
    return df_sorted


def _save_to_file(
        df: pd.DataFrame, opt: Literal["hvxs", "control", "gold"]
) -> None:
    out_dir = config.RESULTS_CATALOGUES_FOR_REVISION / "for_vizier"
    output_path = out_dir / f"{opt}_for_vizier.csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Catalog saved to {output_path}")


def prepare_catalog(opt: Literal["hvxs", "control", "gold"]) -> None:
    df = _load_catalog(opt)
    df = select_columns(df)
    df = rename_columns(df)
    df = sort_by_ra(df)
    _save_to_file(df, opt)


def entry_point() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--opt",
        type=str,
        choices=["hvxs", "control", "gold"],
        default="hvxs",
        help="Which catalog to prepare."
    )
    args = parser.parse_args()
    prepare_catalog(args.opt)


if __name__ == "__main__":
    entry_point()
