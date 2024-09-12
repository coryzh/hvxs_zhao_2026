import pandas as pd
import config
import numpy as np
from log.loggers import VerboseLogger


def combine_catalogs(verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    logger.log(f"Loading the high-velocity source catalogues.\n")

    catalog_dir = config.RESULTS_CATALOGUE_DIR / "high-v_sources"
    df_csc = pd.read_csv(catalog_dir / "csc_vpec_gt_200.csv")
    df_xmm = pd.read_csv(catalog_dir / "xmm_vpec_gt_200.csv")
    df_erass = pd.read_csv(catalog_dir / "erass_vpec_gt_200.csv")

    logger.log(f"Catalogues loaded.\n")
    logger.log(f"Shapes:\n"
               f"CSC: {df_csc.shape}\n"
               f"XMM: {df_xmm.shape}\n"
               f"eRASS: {df_erass.shape}\n")

    logger.log(f"Checking for overlapping Gaia source_ids ...")
    # Check for overlapping source_ids
    source_id_csc = set(df_csc.source_id)
    source_id_xmm = set(df_xmm.source_id)
    source_id_erass = set(df_erass.source_id)

    overlap_ids = source_id_csc & source_id_xmm & source_id_erass
    if overlap_ids:
        print(f"Overlapping source_id's: {overlap_ids}")

    else:
        print(f"No overlapping source_id found.\n")

    logger.log(f"Assigning 'from' column values ... \n")
    # %%
    # Assign labels ("csc", "xmm", "erass") to the sources
    df_csc["from"] = "csc"
    df_xmm["from"] = "xmm"
    df_erass["from"] = "erass"

    logger.log(f"Remapping column names ....")

    column_map_csc = {"flux_aper_b": "f_x", "flux_aper_b_sym_err": "f_x_err", "lum_aper_b": "lum_x",
                      "lum_aper_err_b": "lum_x_err",
                      "ra_csc": "ra_x", "dec_csc": "dec_x", "CSC21P_name": "ID_x", "Sep_GAIA21P_CSC21P": "sep_x_g"}
    df_csc = df_csc.rename(columns=column_map_csc)
    df_csc["pos_x_err"] = df_csc[["err_ellipse_r0", "err_ellipse_r1"]].max(axis=1)
    logger.log(f"CSC columns remapped.")

    column_map_xmm = {"iauname": "ID_x", "sc_ra": "ra_x", "sc_dec": "dec_x", "angDist": "sep_x_g",
                      "sc_ep_8_flux": "f_x", "sc_ep_8_flux_err": "f_x_err", "sc_ep_lum_8": "lum_x",
                      "sc_ep_lum_8_err": "lum_x_err", "pos_x_err": "sc_poserr"}
    df_xmm = df_xmm.rename(columns=column_map_xmm)
    logger.log(f"XMM columns remapped.")

    column_map_erass = {"ra_erass": "ra_x", "dec_erass": "dec_x", "DETUID": "ID_x",
                        "F_X": "f_x", "e_F_X": "f_x_err", "L_X": "lum_x", "e_L_X": "lum_x_err",
                        "Separation_GAIADR3_ERASS": "sep_x_g", "POS_ERR": "pos_x_err"}
    df_erass = df_erass.rename(columns=column_map_erass)
    logger.log(f"eRASS columns remapped.\n")

    logger.log(f"Creating an empty DataFrame")
    common_columns = [
        "ID_x", "source_id", "ra_x", "dec_x", "ra", "dec", "sep_x_g", "ruwe", "gamma_min",
        "parallax", "parallax_error", "pmra", "pmra_error", "pmdec", "pmdec_error", "dist_med", "e_dist", "E_dist",
        "vpec_min_med", "e_vpec_min", "E_vpec_min", "distance_inference",
        "phot_g_mean_mag", "phot_rp_mean_mag", "phot_bp_mean_mag",
        "f_x", "f_x_err", "lum_x", "lum_x_err", "fx_fg", "from"
    ]
    df_all = pd.DataFrame(columns=common_columns)
    for df in [df_csc, df_xmm, df_erass]:
        df_sub = df[common_columns]
        df_all = pd.concat([df_sub, df_all], ignore_index=True)

    df_all = df_all.drop_duplicates()

    # Derived columns
    logger.log(f"Adding derived columns ...")
    df_all["bp_rp"] = df_all.phot_bp_mean_mag - df_all.phot_rp_mean_mag
    logger.log(f"Bp-Rp colour: 'bp_rp' added.\n")

    df_all["f_g"] = df_all.f_x / df_all.fx_fg
    df_all["fx_fg_err"] = df_all["f_x_err"] / df_all["f_g"]
    logger.log(f"Uncertainty on fx_fg: 'fx_fg_err' added.\n")

    logger.log(f"Saving the combined catalogue ...")
    out_file = catalog_dir / "combined_vpec_gt_200_new.csv"
    df_all.to_csv(out_file, index=False)
    logger.log(f"Catalogue saved to {out_file}.")


if __name__ == "__main__":
    combine_catalogs(verbose=True)
