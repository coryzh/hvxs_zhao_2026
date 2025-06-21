import config
import pandas as pd
import data_schema as ds
from catalog.manipulate.parallax_zeropoint_correction import correct_zp
from catalog.manipulate.rename_columns import rename_distance_cols


def process_catalog(survey_name: str) -> None:
    in_file_root = (
        config.RESULTS_CATALOGUE_DIR
        / "complementary_tables"
    )
    nway_dir = (
        config.ROOT_DIR
        / "results"
        / survey_name
        / "catalogues"
        / "nway_match"
    )

    file_gaia = in_file_root / f"{survey_name}_likely_stars.csv"
    file_vpec = in_file_root / f"{survey_name}_likely_stars_w_v_min.csv"
    file_xray = nway_dir / f"{survey_name}_confident_point_sources.csv"

    df_gaia = pd.read_csv(file_gaia)
    print(f"Full Gaia catalog loaded: {df_gaia.shape[0]} sources \n")
    df_vmin = pd.read_csv(file_vpec)
    print(f"vmin catalog loaded: {df_vmin.shape[0]} sources \n")
    df_xray = pd.read_csv(file_xray)
    print(f"X-ray source catalog loaded: {df_xray.shape[0]} sources")

    df_gaia_copy = df_gaia.copy()
    df_vmin_copy = df_vmin.copy()
    df_xray_copy = df_xray.copy()

    df_vmin_copy = df_vmin_copy.drop("ID_x", axis=1)
    df_gaia_copy = correct_zp(df_gaia_copy, verbose=True)
    df_gaia_copy = df_gaia_copy.rename(
        columns={"ra": "ra_gaia", "dec": "dec_gaia",
                 "l": "l_gaia", "b": "b_gaia"
        }
    )

    df_vmin_copy = df_vmin_copy.rename(columns={
        "r_med_photogeo": "dist_med"
    }
    )
    df_vmin_copy["e_dist"] = (
        df_vmin_copy["dist_med"] - df_vmin_copy["r_lo_photogeo"]
    )

    df_vmin_copy["E_dist"] = (
        df_vmin_copy["r_hi_photogeo"] - df_vmin_copy["dist_med"]
    )

    df_vmin_copy = df_vmin_copy.drop(
        columns=["r_lo_photogeo", "r_hi_photogeo"]
    )

    # Merging Gaia with vmin columns
    df_merged = pd.merge(
        df_gaia_copy, df_vmin_copy, on=ds.Gaia.source_id, how="left"
    )

    # Merging with X-ray catalog
    xray_schema = ds.SCHEMA_DICT[survey_name]
    df_merged = pd.merge(
        df_merged, df_xray_copy, on=xray_schema.ID, how="left"
    )

    out_file = in_file_root / f"{survey_name}_likely_stars_master.csv"

    df_merged.to_csv(out_file, index=False)


def main() -> None:
    survey_names = [
        "csc", "xmm", "erass", "swift"
    ]

    for survey in survey_names:
        process_catalog(survey_name=survey)


if __name__ == "__main__":
    main()
