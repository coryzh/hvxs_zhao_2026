import config
import pandas as pd
from pathlib import Path
import logging
from log.log_config import configure_logging
from typing import Literal

configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


def _load_extragalactic_catalogue(
        opt: Literal["lmc", "smc"] = "lmc"
) -> pd.DataFrame:

    in_file = (
        config.DATA_DIR.parent / "others"
        / "catalogues" / f"{opt.lower()}_members.csv"
    )

    df_mc = pd.read_csv(in_file)

    logger.info(
        f"{opt.upper()} member catalogue loaded, "
        f"totalling {df_mc.shape[0]} rows.\n"
    )

    return df_mc


def _merge_to_main_df(
    df: pd.DataFrame, df_mc: pd.DataFrame, opt: Literal["lmc", "smc"]
) -> pd.DataFrame:
    df_merged = pd.merge(df, df_mc, on="source_id", how="left")
    n_matches = df_merged['P'].notna().sum()
    logger.info(
        "Source catalogue cross-matched (joined) with "
        f"the {opt.upper()} catalogue on source_id, "
        f"found {n_matches} matches.\n"
    )

    return df_merged


def _clean_by_membership_probability(
        df: pd.DataFrame, prob_thresh: float, opt: str
) -> pd.DataFrame:
    _filter = (df["P"] <= prob_thresh) | (df["P"].isna())
    n_member = df.shape[0] - _filter.sum()
    logger.info(
        f"{n_member} matches are considered {opt.upper()} "
        f"members (prob>={prob_thresh:.1e}).\n"
    )

    df_filtered = df[_filter]
    logger.info(f"{df_filtered.shape[0]} sources kept.\n")

    return df_filtered


def _cleanup(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns="P")
    logger.info(
        "Clean-up: the membership probability column ('P') has been dropped."
    )

    return df


def clean(
        df: pd.DataFrame, prob_thresh: float = 0.1, opt: str = 'lmc',
        out_file: Path = None
) -> pd.DataFrame:
    """
    Used to remove members in SMC or LMC (specified by the opt argument),
    using the Jimenez-Arranz+23a, b
    DOIs: 10.1051/0004-6361/202245720, 10.1051/0004-6361/202244601

    Parameters
    ----------
    df : pandas.DataFrame
        Input DataFrame

    prob_thresh : float
        Threshold of membership probability. Sources with probability above
        this threshold will be dropped.

    opt : str
        Used to select which Magellanic cloud members to be removed, either
        'lmc' or 'smc'.

    Returns
    -------
    df : pandas.DataFrame
        Output pandas.DataFrame object with members removed.
    """

    logger.info(f"Got source catalogue, totalling {df.shape[0]} rows.\n")

    df_mc = _load_extragalactic_catalogue(opt=opt)
    df_merged = _merge_to_main_df(df, df_mc, opt=opt)
    df = _clean_by_membership_probability(
        df_merged, prob_thresh=prob_thresh, opt=opt
    )
    df = _cleanup(df)
    if out_file is not None:
        df.to_csv(out_file, index=False)
        logger.info(f"Cleaned DataFrame saved to {out_file}.\n")

    logger.info(f"Cleaned DataFrame shape: {df.shape}.\n")

    return df
