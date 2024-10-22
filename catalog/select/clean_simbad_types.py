import pandas as pd

import config
import data_schema as ds
import warnings

unwanted_otype_patterns = [
    'Galaxy', 'Seyfert2', 'QSO', 'AGN', 'BLLac', 'Seyfert1', 'ClG', 'QSO_Candidate', "BrightestCG",
    'AGN_Candidate', 'EmissionG', 'Blazar', 'Blazar_Candidate', 'RadioG', 'LINER', 'GtowardsCl',
    'GtowardsCl', 'GinPair', 'Seyfert', 'BrownD*_Candidate', 'YSO', 'YSO_Candidate',
    'GtowardsGroup', 'TTauri*', 'OrionV*', 'BrightestCG', 'PlanetaryNeb', 'LowSurfBrghtG',
    'HIIG', 'OH/IR*', 'Supernova', 'Supernova_Candidate', 'TTauri*_Candidate', "HIIReg",
    'InteractingG', 'SXPheV*', 'BLLac_Candidate', 'Ae*_Candidate', 'Ae*', 'CataclyV*', 'GlobCluster',
    "Nova", "XrayBin", "LowMassXBin", "HighMassXBin", "Pulsar", '**', "ULX_Candidate", "alf2CVnV*",
    "Planet_Candidate", "Cepheid", "Type2Cep", "ClassicalCep", "RSCVnV*", "LensedQ", "GravLens"
]

unwanted_otypes_patterns = [
    'G', 'Sy2', 'QSO', 'AGN', 'BLL', 'Bla', 'Bz?', 'rG', 'Sy1', 'a2*',
    'AG?', 'Q?', 'EmG', 'LIN', 'IG', 'PaG', 'Y*', 'Y*?', 'cC*', 'SN*',
    'BY*', 'RR*', 'BiC', 'RS*', 'GiG', 'GiC', 'GiP', 'SyG', 'G?', "rG",
    'BD?', 'dS*', 'H2G', 'HS*', 'WV*', 'Sy*', "SyG", 'Mi*', 'LSB', 'Y*O',
    'gD*', 'HII', 'HI', 'RNe', 'BL?', 'TT*', 'Or*', 'HH', 'TT?', 'smm', 'No*',
    'PN', 'EmO', 'ISM', 'Ce*', 'Mas', 'PoG', 'ULX', 'LeQ', 'LeG', 'err',
    'PN?', 'GNe', 'SNR', 'SR?', 'Le?', 'S*', 'SN?', 'RV?', 'Lev', 'gLe',
    'cor', 'LS?', 's?r', "WV*", "UX", "s*r", "dS*", "Gl?", "GlC", "gLS",
    "CV*", 'Psr', 'HXB', 'XB*', 'LXB', '**'
]

unwanted_name_patterns = ["Cl*", "Cl", "NGC", "LEDA"]


def _clean_df_simbad_main_type(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the main type of the sources in the input DataFrame.
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the main type of the sources.

    Returns
    -------
    df : pd.DataFrame
        The filtered DataFrame with the main type of the sources cleaned.
    """
    _filter = ~df[ds.SimbadSchema.SIMBAD_OTYPE].apply(lambda x: any(types in x for types in unwanted_otype_patterns))

    return df[_filter]


def _clean_df_simbad_secondary_types(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the catalogue based on secondary types of the sources in the input DataFrame.
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the secondary types of the sources.

    Returns
    -------
    df : pd.DataFrame
        The filtered DataFrame with the secondary types of the sources cleaned.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df.loc[:, ds.SimbadSchema.SIMBAD_OTYPES] = df[ds.SimbadSchema.SIMBAD_OTYPES].fillna('nan')
        _filter = ~df[ds.SimbadSchema.SIMBAD_OTYPES].apply(lambda x: any(types in x for types
                                                                         in unwanted_otypes_patterns))

    return df[_filter]


def _clean_df_simbad_name(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the names of the sources in the input DataFrame.
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the names of the sources.

    Returns
    -------
    df : pd.DataFrame
        The filtered DataFrame with the names of the sources cleaned.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df.loc[:, ds.SimbadSchema.SIMBAD_IDS] = df[ds.SimbadSchema.SIMBAD_IDS].fillna('nan')
        _filter = ~df[ds.SimbadSchema.SIMBAD_IDS].apply(lambda x: any(types in x for types in unwanted_name_patterns))

    return df[_filter]


def _join_w_vpec_catalogue(df: pd.DataFrame) -> pd.DataFrame:
    """
    Join the input DataFrame with the vpec catalogue.
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the types of the sources.

    Returns
    -------
    df : pd.DataFrame
        The input DataFrame joined with the vpec catalogue.
    """
    df_vpec = pd.read_csv(config.ERASS_GAIA_W_VPEC_AND_FLUX_RATIOS, dtype={"source_id": str})
    df = df[[ds.SimbadSchema.SIMBAD_ID, "DETUID", ds.SimbadSchema.SIMBAD_OTYPE, ds.SimbadSchema.SIMBAD_OTYPES,
             ds.SimbadSchema.SIMBAD_OTYPE_OPT]]

    df = pd.merge(df_vpec, df, on="DETUID", how="inner")

    return df


def main() -> None:
    print(f"Loading the VPEC catalogue ...")
    df = pd.read_csv(config.ERASS_GAIA_W_SIMBAD_TYPES, dtype={"source_id": str})
    print(f"Catalogue loaded, a total of {df.shape[0]} rows loaded.\n")

    df_filtered_1 = _clean_df_simbad_main_type(df)
    print(f"Cleaning the catalogue based on SIMBAD main types (OTYPE) ...")
    print(f"Removed {df.shape[0] - df_filtered_1.shape[0]} rows based on unwanted SIMBAD main types.\n")

    df_filtered_2 = _clean_df_simbad_secondary_types(df_filtered_1)
    print(f"Cleaning the catalogue based on SIMBAD secondary types (OTYPES) ...")
    print(f"Removed {df_filtered_1.shape[0] - df_filtered_2.shape[0]} rows based on unwanted SIMBAD secondary types.\n")

    df_filtered_3 = _clean_df_simbad_name(df_filtered_2)
    print(f"Cleaning the catalogue based on SIMBAD names ...")
    print(f"Removed {df_filtered_2.shape[0] - df_filtered_3.shape[0]} rows based on unwanted SIMBAD names.\n")

    print(f"The filtered catalogue has {df_filtered_3.shape[0]} rows.\n")
    out_file_simbad_types = config.ERASS_GAIA_SIMBAD_TYPES_CLEANED

    print(f"The 'Unknown' sources were positionally matched with SIMBAD; loading the SIMBAD types table ...\n")
    df_simbad_pos_match = pd.read_csv(config.DATA_DIR_INTERMEDIATE / "erass_gaia_simbad_types_pos_match.csv",
                                      dtype={"source_id": str})
    print(f"The further position match identified {df_simbad_pos_match.OTYPE.notna().sum()} sources.\n")

    print(f"Cleaning the pos_match types table ...\n")
    df_simbad_pos_match["OTYPE"].fillna("Unknown", inplace=True)
    df_simbad_pos_match_filtered_1 = _clean_df_simbad_main_type(df_simbad_pos_match)
    print(f"Removed {df_simbad_pos_match.shape[0] - df_simbad_pos_match_filtered_1.shape[0]} "
          f"rows based on unwanted SIMBAD main types.\n")

    df_simbad_pos_match_filtered_2 = _clean_df_simbad_secondary_types(df_simbad_pos_match_filtered_1)
    print(f"Removed {df_simbad_pos_match_filtered_1.shape[0] - df_simbad_pos_match_filtered_2.shape[0]} "
          f"rows based on unwanted SIMBAD secondary types.\n")

    df_simbad_pos_match_filtered_3 = _clean_df_simbad_name(df_simbad_pos_match_filtered_2)
    print(f"Removed {df_simbad_pos_match_filtered_2.shape[0] - df_simbad_pos_match_filtered_3.shape[0]} "
          f"rows based on unwanted SIMBAD names.\n")

    # Now, check which sources have been removed from the original SIMBAD types table
    # here, indicator=True adds a column to the merged table named "_merge" which indicates the source of each row:
    # either from the 'left', 'right', or 'both' tables.
    print(f"Comparing the cleaned (pos_matched) SIMBAD types table with the original one ...\n")
    df_simbad_pos_compare = pd.merge(df_simbad_pos_match, df_simbad_pos_match_filtered_3, on="DETUID",
                                     how="outer", indicator=True)

    # The sources that are in the original SIMBAD types table but not in the cleaned one.
    print(f"Getting a list of sources removed from the original (pos-matched) SIMBAD table ...\n")
    df_simbad_pos_removed = df_simbad_pos_compare[df_simbad_pos_compare["_merge"] == "left_only"]
    print(f"In total, {df_simbad_pos_removed.shape[0]} sources "
          f"were removed from the original (pos-matched) SIMBAD table.\n")

    # Now, remove these sources from df_filtered_3, the cleaned (name-matched) SIMBAD types table
    print(f"Now, removing these sources from the cleaned (name-matched) SIMBAD table ...\n")
    df_filtered_4 = df_filtered_3[~df_filtered_3["DETUID"].isin(df_simbad_pos_removed["DETUID"])]
    print(f"Removed {df_filtered_3.shape[0] - df_filtered_4.shape[0]} sources from the cleaned (name-matched) SIMBAD "
          f"table.\n")
    df_filtered_4.to_csv(out_file_simbad_types, index=False)
    print(f"Catalogue saved to {out_file_simbad_types}.\n")

    print(f"Using the cleaned SIMBAD type catalogue to join with the VPEC catalogue ...\n")
    df_joined = _join_w_vpec_catalogue(df_filtered_4)

    # print(f"Joining the SIMBAD-cleaned, vpec-hosting catalogue with the raw ERASS main catalogue to "
    #       f"get detection likelihoods ...\n")
    # df_w_det_likelihood = _get_detection_likelihood(df_joined)

    out_file_joined = config.ERASS_GAIA_W_VPEC_SIMBAD_TYPES_CLEANED
    df_joined.to_csv(out_file_joined, index=False)
    print(f"Catalogue saved to {out_file_joined}.\n")
    print(f"Done!")


if __name__ == "__main__":
    main()
