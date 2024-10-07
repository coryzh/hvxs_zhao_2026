import pandas as pd
import config
from log.loggers import VerboseLogger

column_map_csc = {"flux_aper_b": "f_x", "flux_aper_b_sym_err": "f_x_err", "lum_aper_b": "lum_x",
                  "lum_aper_err_b": "lum_x_err",
                  "ra_csc": "ra_x", "dec_csc": "dec_x", "CSC21P_name": "ID_x", "Sep_GAIA21P_CSC21P": "sep_x_g"}

column_map_xmm = {"iauname": "ID_x", "sc_ra": "ra_x", "sc_dec": "dec_x", "angDist": "sep_x_g",
                  "sc_ep_8_flux": "f_x", "sc_ep_8_flux_err": "f_x_err", "sc_ep_lum_8": "lum_x",
                  "sc_ep_lum_8_err": "lum_x_err", "sc_poserr": "pos_x_err"}

column_map_erass = {"ra_erass": "ra_x", "dec_erass": "dec_x", "DETUID": "ID_x",
                    "F_X": "f_x", "e_F_X": "f_x_err", "L_X": "lum_x", "e_L_X": "lum_x_err",
                    "Separation_GAIADR3_ERASS": "sep_x_g", "pos_err_erass": "pos_x_err"}

column_map_swift = {"RA": "ra_x", "Decl": "dec_x", "IAUName": "ID_x",
                    "PowFlux_cen": "f_x", "PowFlux_cen_err": "f_x_err", "PowLum": "lum_x", "PowLum_err": "lum_x_err",
                    "angDist": "sep_x_g", "Err90": "pos_x_err"}

column_map_dict = {"csc": column_map_csc, "xmm": column_map_xmm, "erass": column_map_erass, "swift": column_map_swift}

common_columns = [
    "ID_x", "source_id", "ra_x", "dec_x", "pos_x_err", "ra", "dec", "sep_x_g", "ruwe", "gamma_min",
    "parallax", "parallax_error", "pmra", "pmra_error", "pmdec", "pmdec_error", "dist_med", "e_dist", "E_dist",
    "vpec_min_med", "e_vpec_min", "E_vpec_min", "distance_inference",
    "phot_g_mean_mag", "phot_rp_mean_mag", "phot_bp_mean_mag",
    "f_x", "f_x_err", "lum_x", "lum_x_err", "fx_fg", "from"
]


def combine_catalogs(vpec_lim: float = 150., mode: str = "lolim", verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    logger.log(f"Loading the high-velocity source catalogues.\n")

    catalogue_names = ["csc", "erass", "xmm", "swift"]
    # overlap_ids = None
    df_all = pd.DataFrame(columns=common_columns)
    for _name in catalogue_names:
        df_dir = config.RESULTS_CATALOGUE_DIR / f"{_name}_gaia_vpec.csv"
        df = pd.read_csv(df_dir)

        logger.log(f"Catalogues loaded.\n")
        logger.log(f"Shapes:\n"
                   f"{_name.upper()}: {df.shape}\n")

        if mode == "lolim":
            _filter_vpec = df.vpec_min_med - df.e_vpec_min >= vpec_lim

        elif mode == "med":
            _filter_vpec = df.vpec_min_med >= vpec_lim

        else:
            _filter_vpec = df.index >= 0
            print(f"{mode} is not a valid option. Choose from ['med', 'lolim'].")

        logger.log(f"Selecting sources that have vpec_{mode} >= {vpec_lim} km/s for {_name} ...")
        df_selected = df[_filter_vpec]
        logger.log(f"{_filter_vpec.sum()} sources selected.")

        df_selected["from"] = _name
        logger.log(f"Assigned {_name} to 'from' column ...")

        if _name == "csc":
            logger.log(f"Adding X-ray positional uncertainty column for {_name} ...")
            df_selected["pos_x_err"] = df_selected[["err_ellipse_r0", "err_ellipse_r1"]].max(axis=1)

        logger.log(f"Remapping column names for the {_name.upper()} catalogue ...")
        df_selected = df_selected.rename(columns=column_map_dict[_name])
        logger.log(f"Column names remapped for {_name.upper()}. \n")

        source_id = set(df_selected.source_id)
        if overlap_ids is None:
            overlap_ids = source_id

        logger.log(f"Concatenating the {_name} DataFrame to the combined DataFrame")
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
    logger.log(f"Checking for overlapping Gaia source_ids ...")
    if overlap_ids:
        print(f"Overlapping source_id's: {overlap_ids}")

    else:
        print(f"No overlapping source_id found.\n")

    # %%
    # Assign labels ("csc", "xmm", "erass") to the sources
    # df_csc["from"] = "csc"
    # df_xmm["from"] = "xmm"
    # df_erass["from"] = "erass"
    #
    # df_csc = df_csc.rename(columns=column_map_csc)
    # df_csc["pos_x_err"] = df_csc[["err_ellipse_r0", "err_ellipse_r1"]].max(axis=1)
    # logger.log(f"CSC columns remapped.")
    #
    # df_xmm = df_xmm.rename(columns=column_map_xmm)
    # logger.log(f"XMM columns remapped.")
    # df_erass = df_erass.rename(columns=column_map_erass)
    # logger.log(f"eRASS columns remapped.\n")

    # df_all = pd.DataFrame(columns=common_columns)
    # for df in [df_csc, df_xmm, df_erass]:
    #     df_sub = df[common_columns]
    #     df_all = pd.concat([df_sub, df_all], ignore_index=True)

    df_all = df_all.drop_duplicates()

    # Derived columns
    logger.log(f"Adding derived columns ...")
    df_all["bp_rp"] = df_all.phot_bp_mean_mag - df_all.phot_rp_mean_mag
    logger.log(f"Bp-Rp colour: 'bp_rp' added.\n")

    df_all["f_g"] = df_all.f_x / df_all.fx_fg
    df_all["fx_fg_err"] = df_all["f_x_err"] / df_all["f_g"]
    logger.log(f"Uncertainty on fx_fg: 'fx_fg_err' added.\n")

    logger.log(f"Saving the combined catalogue ...")
    out_file = config.RESULTS_CATALOGUE_DIR / "high-v_sources" / f"combined_vpec_{mode}_gt_{vpec_lim}.csv"
    df_all.to_csv(out_file, index=False)
    logger.log(f"Catalogue saved to {out_file}.")


if __name__ == "__main__":
    combine_catalogs(verbose=True)
