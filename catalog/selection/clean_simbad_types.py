import pandas as pd

import config
import data_schema as ds
import warnings
from log.loggers import VerboseLogger


unwanted_otype_patterns = [
    'Galaxy', 'Seyfert2', 'QSO', 'AGN', 'BLLac', 'Seyfert1', 'ClG',
    'QSO_Candidate', "BrightestCG", 'AGN_Candidate', 'EmissionG', 'Blazar',
    'Blazar_Candidate', 'RadioG', 'LINER', 'GtowardsCl', 'GtowardsCl',
    'GinPair', 'Seyfert', 'BrownD*_Candidate', 'YSO', 'YSO_Candidate',
    'GtowardsGroup', 'TTauri*', 'OrionV*', 'BrightestCG', 'PlanetaryNeb',
    'LowSurfBrghtG', 'HIIG', 'OH/IR*', 'Supernova', 'Supernova_Candidate',
    'TTauri*_Candidate', "HIIReg", 'InteractingG', 'SXPheV*',
    'BLLac_Candidate', 'Ae*_Candidate', 'Ae*', 'CataclyV*', 'GlobCluster',
    "Nova", "XrayBin", "LowMassXBin", "HighMassXBin", "Pulsar", '**',
    "ULX_Candidate", "alf2CVnV*", "Planet_Candidate", "Cepheid", "Type2Cep",
    "ClassicalCep", "RSCVnV*", "LensedQ", "GravLens", "SB*",
    "XrayBin_Candidate", "DarkNeb", "PartofCloud", "LowMassXBin_Candidate",
    "Bubble", "Association", "Outflow_Candidate", "Outflow", "Cluster*",
    "Neutron*", "RSCVnV*_Candidate", "BYDraV*_Candidate", "Ae*",
    "BlackHole_Candidate", "LensedImage", "HIshell", "LensedImage_Candidate",
    "Neutron*_Candidate"
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
    "CV*", 'Psr', 'HXB', 'XB*', 'LXB', '**',  "HX?", "OpC", "Pl", "CV?", "MoC"
]

unwanted_name_patterns = ["Cl*", "Cl", "NGC", "LEDA"]


def _clean_df_simbad_main_type(
        df: pd.DataFrame, verbose: bool = False
) -> pd.DataFrame:
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
    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    logger.log(f"{df.shape[0]} rows loaded.\n")

    _filter = (
        ~df[ds.SimbadSchema.SIMBAD_MAIN_TYPE]
        .apply(lambda x: any(types in x for types in unwanted_otype_patterns))
    )

    logger.log(
        f"{df.shape[0] - _filter.sum()} rows removed based on their "
        "main_type.\n"
    )

    logger.end()

    return df[_filter]


def _clean_df_simbad_secondary_types(
        df: pd.DataFrame, verbose: bool = False
) -> pd.DataFrame:
    """
    Clean the catalogue based on secondary types of the sources in the input
    DataFrame.
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the secondary types of the sources.

    Returns
    -------
    df : pd.DataFrame
        The filtered DataFrame with the secondary types of the sources cleaned.
    """

    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    logger.log(f"{df.shape[0]} rows loaded.\n")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        df.loc[:, ds.SimbadSchema.SIMBAD_OTYPES] = (
            df[ds.SimbadSchema.SIMBAD_OTYPES].fillna('nan')
        )
        _filter = (
            ~df[ds.SimbadSchema.SIMBAD_OTYPES]
            .apply(
                lambda x: any(types in x for types in unwanted_otypes_patterns)
            )
        )

    logger.log(
        f"{df.shape[0] - _filter.sum()} rows removed based on their "
        "secondary types.\n"
    )

    logger.end()

    return df[_filter]


def _clean_df_simbad_name(
        df: pd.DataFrame, verbose: bool = False
) -> pd.DataFrame:

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

    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    logger.log(f"{df.shape[0]} rows loaded.\n")
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        df.loc[:, ds.SimbadSchema.SIMBAD_ID] = (
            df[ds.SimbadSchema.SIMBAD_ID].fillna('nan')
        )

        _filter = (
            ~df[ds.SimbadSchema.SIMBAD_ID]
            .apply(
                lambda x: any(types in x for types in unwanted_name_patterns)
            )
        )

    logger.log(
        f"{df.shape[0] - _filter.sum()} rows removed based on their "
        "SIMBAD names.\n"
    )

    logger.end()

    return df[_filter]


def main() -> None:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "control_sample"
        / "control_sample_stage_2.csv"
    )

    df = pd.read_csv(in_file)
    df[ds.SimbadSchema.get_attribute_values()] = (
        df[ds.SimbadSchema.get_attribute_values()].fillna("")
    )

    verbose = True

    df_filtered_1 = _clean_df_simbad_main_type(df, verbose=verbose)

    df_filtered_2 = _clean_df_simbad_secondary_types(
        df_filtered_1, verbose=verbose
    )

    df_filtered_3 = _clean_df_simbad_name(df_filtered_2, verbose=verbose)

    df_filtered_3.to_csv(
        in_file.parent / f"{in_file.stem.replace('stage_2', 'stage_3')}.csv",
        index=False
    )

    print("Done!")


if __name__ == "__main__":
    main()
