import config
import pandas as pd


def _add_pos_xerr_column(df: pd.DataFrame, survey_name: str) -> pd.DataFrame:
    """Add or rename the X-ray positional error column to 'pos_x_err', given
    the survey name.
    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing X-ray source information.
    survey_name : str
        The name of the survey for which to add or rename the positional error
        column.

    Returns
    -------
    pd.DataFrame
        The modified DataFrame with the positional error column added or renamed.

    Raises
    ------
    ValueError
        If the survey name is not recognized.
    """
    df_copy = df.copy()
    if survey_name == "csc":
        df_copy["pos_x_err"] = df_copy[["err_ellipse_r0", "err_ellipse_r1"]].max(axis=1)

    elif survey_name == "xmm":
        df_copy = df_copy.rename(
            columns={"sc_poserr": "pos_x_err"}
        )

    elif survey_name == "erass":
        df_copy = df_copy.rename(
            columns={"POS_ERR": "pos_x_err"}
        )

    elif survey_name == "swift":
        df_copy = df_copy.rename(
            columns={"Err90": "pos_x_err"}
        )
    else:
        raise ValueError(
            f"{survey_name} is not a valid survey name. "
            f"Choose from {list(config.SURVEY_NAMES_SHORT)}"
        )
    return df_copy
