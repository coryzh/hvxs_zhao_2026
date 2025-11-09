import pandas as pd
import data_schema as ds
import logging
import warnings
from log.loggers import configure_logging
from pathlib import Path


configure_logging(level=logging.INFO, app_name=__name__)
logger = logging.getLogger(__name__)

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
        df: pd.DataFrame
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
    logger.info(f"Catalogue loaded: {df.shape[0]} rows loaded.\n")

    _filter = (
        ~df[ds.SimbadSchema.SIMBAD_MAIN_TYPE]
        .apply(lambda x: any(types in x for types in unwanted_otype_patterns))
    )

    logger.info(
        f"{df.shape[0] - _filter.sum()} rows removed based on their "
        "main_type.\n"
    )

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

    logger.info(f"Catalogue loaded: {df.shape[0]} rows loaded.\n")
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
    logger.info(f"Catalogue loaded: {df.shape[0]} rows loaded.\n")
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

    logger.info(
        f"{df.shape[0] - _filter.sum()} rows removed based on their "
        "SIMBAD names.\n"
    )

    return df[_filter]


def clean(
        in_file: Path, in_file_simbad: Path, out_file: Path
) -> pd.DataFrame:
    df = pd.read_csv(in_file)
    df_simbad = pd.read_csv(in_file_simbad)

    df = pd.merge(
        df, df_simbad, on=ds.CombinedCatalogueSchema.ID_x, how='left'
    )

    df = _clean_df_simbad_main_type(df)
    df = _clean_df_simbad_secondary_types(df)
    df = _clean_df_simbad_name(df)

    df.to_csv(out_file, index=False)
    logger.info(f"Cleaned catalogue saved to {out_file}")

    return df
