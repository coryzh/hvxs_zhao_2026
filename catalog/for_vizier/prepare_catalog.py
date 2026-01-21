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
        "ID_x", "source_id", "ra_x", "dec_x", "ra_gaia", "dec_gaia",
        "sep_x_g", "pos_x_err", "dist_med", "e_dist", "E_dist",
        "f_x", "f_x_err", "phot_g_mean_mag", "bp_rp", "fx_fg", "fx_fg_err",
        "vpec_gamma_min_med", "e_vpec_gamma_min", "E_vpec_gamma_min",
        "vpec_min_med", "e_vpec_min", "E_vpec_min", "quality"
    ]

    df_selected = df[columns]
    return df_selected


def sort_by_ra(df: pd.DataFrame) -> pd.DataFrame:
    df_sorted = df.sort_values(
        by="ra_gaia", ascending=True
    ).reset_index(drop=True)
    return df_sorted


def reformat_columns(df: pd.DataFrame) -> pd.DataFrame:
    format_dict = {
        "ra": "{:.11f}", "dec": "{:.11f}",
        "ra_x": "{:.8f}", "dec_x": "{:.8f}",
        "sep_x_g": "{:.3e}", "pos_x_err": "{:.2f}",
        "dist_med": "{:.2e}", "e_dist": "{:.2e}", "E_dist": "{:.2e}",
        "f_x": "{:.3e}", "f_x_err": "{:.3e}",
        "fx_fg": "{:.3e}", "fx_fg_err": "{:.3e}",
        "vpec_gamma_min_med": "{:.3f}", "e_vpec_gamma_min": "{:.3f}",
        "E_vpec_gamma_min": "{:.3f}",
        "vpec_min_med": "{:.3f}",
        "e_vpec_min": "{:.3f}", "E_vpec_min": "{:.3f}"
    }

    for col, fmt in format_dict.items():
        if col in df.columns:
            df[col] = df[col].map(lambda x: fmt.format(x))

    return df


def rename_columns(df: pd.DataFrame) -> pd.DataFrame:
    column_mapping = {
        "ID_x": "Name", "ra_x": "RAdeg", "dec_x": "DEdeg",
        "ra_gaia": "RAdeg_Gaia", "dec_gaia": "DEdeg_Gaia",
        "sep_x_g": "Sep", "pos_x_err": "PosErr",
        "phot_g_mean_mag": "Gmag", "bp_rp": "BP_RP",
        "dist_med": "dist",
        "vpec_gamma_min_med": "gamma_min",
        "e_vpec_gamma_min": "e_gamma_min",
        "E_vpec_gamma_min": "E_gamma_min",
        "vpec_min_med": "vpec_min",
        "f_x": "Fx", "f_x_err": "e_Fx",
        "fx_fg": "Fx_Fg", "fx_fg_err": "e_Fx_Fg",
    }

    df = df.rename(columns=column_mapping)
    return df


def _save_to_file(
        df: pd.DataFrame, opt: Literal["hvxs", "control", "gold"]
) -> None:
    out_dir = config.RESULTS_CATALOGUES_FOR_REVISION / "for_vizier"
    output_path = out_dir / f"{opt}.csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Catalog saved to {output_path}")


def prepare_catalog(opt: Literal["hvxs", "control", "gold"]) -> None:
    df = _load_catalog(opt)
    df = select_columns(df)
    df = sort_by_ra(df)
    df = reformat_columns(df)
    df = rename_columns(df)
    _save_to_file(df, opt)


def entry_point() -> None:
    parser = ArgumentParser()
    parser.add_argument(
        "--opt",
        type=str,
        choices=["hvxs", "control"],
        default="hvxs",
        help="Which catalog to prepare."
    )
    args = parser.parse_args()
    prepare_catalog(args.opt)


if __name__ == "__main__":
    entry_point()
