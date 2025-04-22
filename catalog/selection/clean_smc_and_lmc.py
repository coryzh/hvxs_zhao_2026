import config
import pandas as pd
from log.loggers import VerboseLogger


def clean(
        df: pd.DataFrame, prob_thresh: float = 0.1, opt: str = "lmc",
        verbose: bool = False
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

    verbose : bool
        If True, extra information is printed.

    Returns
    -------
    df : pandas.DataFrame
        Output pandas.DataFrame object with members removed.
    """

    logger = VerboseLogger(verbose=verbose)
    logger.begin()
    df_mc = (
        pd.read_csv(config.DATA_DIR.parent
                    / "others" / "catalogues" / f"{opt.lower()}_members.csv")
    )

    logger.log(
        f"{opt.upper()} member catalogue loaded, "
        f"totalling {df_mc.shape[0]} rows.\n"
    )

    logger.log(f"Source catalogue loaded, totalling {df.shape[0]} rows.\n")

    df_merged = pd.merge(df, df_mc, on="source_id", how="left")
    n_matches = df_merged['P'].notna().sum()
    logger.log(f"Source catalogue cross-matched with {opt.upper()} catalogue, "
               f"found {n_matches} matches.\n")

    # source_ids not in the SMC or LMC catalogue have empty P values, and they
    # are considered non-members, so .isna() is combined with the threshold
    # condition.

    _filter = (df_merged["P"] <= prob_thresh) | (df_merged["P"].isna())
    n_member = df.shape[0] - _filter.sum()
    logger.log(
        f"{n_member} matches are considered {opt.upper()} "
        f"members (prob>={prob_thresh:.1e}).\n"
    )

    df_filtered = df_merged[_filter]
    logger.log(f"{df_filtered.shape[0]} sources kept.\n")

    df_filtered.drop(columns="P", inplace=True)
    logger.end()

    return df_filtered


def main() -> None:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources"
        / "combined_vpec_lolim_gt_200_unique_stage_8.csv"
    )

    df = pd.read_csv(in_file)
    df_cleaned = clean(df, prob_thresh=0.002, opt="lmc", verbose=True)
    df_cleaned = clean(df_cleaned, prob_thresh=0.016, opt="smc", verbose=True)

    out_file = in_file.with_name(in_file.name.replace("stage_8", "stage_9"))
    df_cleaned.to_csv(out_file, index=False)


if __name__ == "__main__":
    main()
