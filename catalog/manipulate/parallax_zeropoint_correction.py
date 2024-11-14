import pandas as pd
from data_schema import Gaia as G
from zero_point import zpt
from log.loggers import VerboseLogger


def correct_zp(df: pd.DataFrame, verbose: bool = False) -> pd.DataFrame:
    """
    Correct the parallax for zero-point offset. The corrected parallax column is named as "parallax_corr", it contains
    the corrected parallax values when available, otherwise the original parallax values are used.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to be corrected for zero-point offset.

    verbose : bool
        If True, print message to the screen.

    Returns
    -------
    df : pd.DataFrame
        The dataframe containing the corrected parallax, which is named as "parallax_corr".
    """
    zpt.load_tables()
    logger = VerboseLogger(verbose=verbose)

    logger.log(f"Catalogue loaded.\n")
    zero_point = df.apply(zpt.zpt_wrapper, axis=1)

    df[G.parallax_corr] = df[G.parallax] - zero_point
    has_valid_parallax_corr = ~df[G.parallax_corr].isna()
    df[G.parallax_corr] = df[G.parallax_corr].fillna(df["parallax"])
    df[G.has_valid_parallax_corr] = has_valid_parallax_corr

    logger.log(f"{sum(~has_valid_parallax_corr)} rows have NA parallax_corr, but they have valid parallaxes,"
               f" so the parallax_corr is replaced with parallax values for these rows and are flagged by "
               f"has_valid_parallax_corr.\n")

    return df
