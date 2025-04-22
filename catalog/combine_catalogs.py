import pandas as pd
import config
from log.loggers import VerboseLogger

column_map_csc = {
    "flux_aper_b": "f_x", "flux_aper_b_sym_err": "f_x_err",
    "lum_aper_b": "lum_x", "lum_aper_err_b": "lum_x_err",
    "ra_deg": "ra_x", "dec_deg": "dec_x",
    "name": "ID_x", "Separation_gaia_csc": "sep_x_g"
}

column_map_xmm = {
    "iauname": "ID_x", "sc_ra": "ra_x", "sc_dec": "dec_x",
    "Separation_gaia_xmm": "sep_x_g",
    "sc_ep_8_flux": "f_x", "sc_ep_8_flux_err": "f_x_err",
    "sc_ep_lum_8": "lum_x", "sc_ep_lum_8_err": "lum_x_err",
    "sc_poserr": "pos_x_err"
}

column_map_erass = {
    "RA": "ra_x", "DEC": "dec_x", "IAUNAME": "ID_x",
    "ML_FLUX_1": "f_x", "ML_FLUX_ERR_1": "f_x_err",
    "lum_x": "lum_x", "lum_x_err": "lum_x_err",
    "Separation_gaia_erass": "sep_x_g", "POS_ERR": "pos_x_err"
}

column_map_swift = {
    "RA": "ra_x", "Decl": "dec_x", "IAUName": "ID_x",
    "PowFlux_cen": "f_x", "PowFlux_cen_err": "f_x_err",
    "PowLum": "lum_x", "PowLum_err": "lum_x_err",
    "Separation_gaia_swift": "sep_x_g", "Err90": "pos_x_err"
}

column_map_dict = {
    "csc": column_map_csc,
    "xmm": column_map_xmm,
    "erass": column_map_erass,
    "swift": column_map_swift
}

common_columns = [
    "ID_x", "source_id",
    "ra_x", "dec_x", "pos_x_err", "ra_gaia", "dec_gaia", "sep_x_g",
    "ruwe", "astrometric_excess_noise", "astrometric_excess_noise_sig",
    "non_single_star",
    "mh_gspphot", "mh_gspphot_lower", "mh_gspphot_upper",
    "parallax", "parallax_corr", "parallax_error",
    "pmra", "pmra_error", "pmdec", "pmdec_error",
    "dist_med", "e_dist", "E_dist",
    "vpec_gamma_min_med", "e_vpec_gamma_min", "E_vpec_gamma_min",
    "vpec_min_med", "e_vpec_min", "E_vpec_min",
    "vspace_gamma_min_med", "e_vspace_gamma_min", "E_vspace_gamma_min",
    "vspace_min_med", "e_vspace_min", "E_vspace_min",
    "phot_g_mean_mag", "phot_rp_mean_mag", "phot_bp_mean_mag",
    "f_x", "f_x_err", "lum_x", "lum_x_err", "fx_fg", "from"
]


def combine_catalogs(vpec_lim: float = 0, mode: str = "lolim",
                     verbose: bool = False) -> None:

    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    logger.log("Loading the high-velocity source catalogues.\n")

    catalogue_names = ["csc", "erass", "xmm", "swift"]
    # overlap_ids = None
    df_all = pd.DataFrame(columns=common_columns)
    for _name in catalogue_names:
        cat_dir = config.RESULTS_CATALOGUE_DIR / "master_catalogs"
        cat_path = cat_dir / f"{_name}_master_catalog_w_fx_fg.csv"
        df = pd.read_csv(cat_path)

        logger.log("Catalogues loaded.\n")
        logger.log(f"Shapes:\n"
                   f"{_name.upper()}: {df.shape}\n")

        if mode == "lolim":
            _filter_vpec = df.vpec_min_med - df.e_vpec_min >= vpec_lim

        elif mode == "med":
            _filter_vpec = df.vpec_min_med >= vpec_lim

        else:
            _filter_vpec = df.index >= 0
            raise ValueError(
                f"{mode} is not a valid option. Choose from ['med', 'lolim']."
            )

        logger.log(
            f"Selecting sources that have vpec_{mode} >= {vpec_lim} km/s "
            f"for {_name} ..."
        )

        df_selected = df[_filter_vpec]
        logger.log(f"{_filter_vpec.sum()} sources selected.")

        df_selected["from"] = _name
        logger.log(f"Assigned {_name} to 'from' column ...")

        if _name == "csc":
            logger.log(
                f"Adding X-ray positional uncertainty column for {_name} ..."
            )
            df_selected["pos_x_err"] = df_selected[
                ["err_ellipse_r0", "err_ellipse_r1"]
            ].max(axis=1)

        logger.log(
            f"Remapping column names for the {_name.upper()} catalogue ..."
        )

        df_selected = df_selected.rename(columns=column_map_dict[_name])

        logger.log(f"Column names remapped for {_name.upper()}. \n")

        # source_id = set(df_selected.source_id)
        # if overlap_ids is None:
        #     overlap_ids = source_id
        #
        # else:
        #     overlap_ids &= source_id

        logger.log(
            f"Concatenating the {_name} DataFrame to the combined DataFrame"
        )
        df_selected = df_selected[common_columns]
        df_all = pd.concat([df_all, df_selected])

    # catalog_dir = config.RESULTS_CATALOGUE_DIR / "high-v_sources"
    # df_csc = pd.read_csv(catalog_dir / "csc_vpec_gt_200.csv")
    # df_xmm = pd.read_csv(catalog_dir / "xmm_vpec_gt_200.csv")
    # df_erass = pd.read_csv(catalog_dir / "erass_vpec_gt_200.csv")

    # Check for overlapping source_ids
    # source_id_csc = set(df_csc.source_id)
    # source_id_xmm = set(df_xmm.source_id)
    # source_id_erass = set(df_erass.source_id)

    # overlap_ids = source_id_csc & source_id_xmm & source_id_erass
    logger.log("Checking for overlapping Gaia source_ids ...")

    # Count the number of occurrences of unique source_ids
    id_counts = df_all["source_id"].value_counts()

    # Counts how many times each id_counts value occur.
    id_counts_summary = id_counts.value_counts().sort_index()

    logger.log("Multiple identifications summary:\n")
    logger.log(id_counts_summary)
    logger.log("Reforming the 'from' column ...")

    # Grouped by "source_id" — bringing together rows with the
    # same source_id ...
    grouped = df_all.groupby('source_id')['from']

    # Then aggregate on the groupby object; this generates a df with the
    # source_id and new from values:
    new_from_column = (grouped
                       .apply(lambda x: ', '.join(sorted(set(x))))
                       .reset_index())

    new_from_column.rename(columns={"from": "from_catalogues"}, inplace=True)
    df_all_updated = pd.merge(
        df_all, new_from_column, on="source_id", how="left"
    )
    df_all_unique = df_all_updated.drop_duplicates(
        subset="source_id", keep="first"
    )

    # Derived columns
    for df_indiv in [df_all, df_all_unique]:
        logger.log("Adding derived columns ...")
        df_indiv["bp_rp"] = (df_indiv.phot_bp_mean_mag
                             - df_indiv.phot_rp_mean_mag)

        df_indiv["f_g"] = df_indiv.f_x / df_indiv.fx_fg
        df_indiv["fx_fg_err"] = df_indiv["f_x_err"] / df_indiv["f_g"]

    logger.log("Bp-Rp colour: 'bp_rp' added.\n")
    # logger.log(f"Uncertainty on fx_fg: 'fx_fg_err' added.\n")

    logger.log("Saving the combined catalogues ...")
    logger.log("Saving the combined catalogue of all X-ray sources ...")

    out_file_name = f"combined_vpec_{mode}_gt_{vpec_lim}_all.csv"
    out_file_path = (config.RESULTS_CATALOGUE_DIR
                     / "high-v_sources" / out_file_name)

    df_all_updated.to_csv(out_file_path, index=False)
    logger.log(f"Catalogue saved to {out_file_path}.\n")
    logger.log("Saving the combined catalogue of unique X-ray sources ...")

    out_file_name = f"combined_vpec_{mode}_gt_{vpec_lim}_unique_stage_0.csv"
    out_file_path_unique = (config.RESULTS_CATALOGUE_DIR / "high-v_sources"
                            / out_file_name)

    df_all_unique.to_csv(out_file_path_unique, index=False)

    logger.log(f"Catalogue saved to {out_file_path_unique}.")


if __name__ == "__main__":
    combine_catalogs(vpec_lim=200, mode="lolim", verbose=True)
