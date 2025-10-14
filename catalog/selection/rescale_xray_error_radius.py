import config
import pandas as pd
import warnings
import numpy as np


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
        The modified DataFrame with the positional error column added or
        renamed.

    Raises
    ------
    ValueError
        If the survey name is not recognized.
    """

    if "pos_x_err" in df.columns:
        warnings.warn(
            "pos_x_err column already exists in the DataFrame, "
            "while positional error is expected to be in its original form if"
            "the input DataFrame is from a (relatively)-raw X-ray source "
            "catalogue. Check how it was created.",
            UserWarning
        )
        return df

    df_copy = df.copy()
    if survey_name == "csc":
        df_copy["pos_x_err"] = (
            df_copy[["err_ellipse_r0", "err_ellipse_r1"]].max(axis=1)
        )

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


def calibrate_pos_xerr(
        df: pd.DataFrame, survey_name: str
) -> pd.DataFrame:
    df_copy = df.copy()
    df_copy = _add_pos_xerr_column(df_copy, survey_name)
    if survey_name == "csc":
        # CSC's semi-major and semi-minor axes are 95% confidence level
        # error ellipses. 1-sigma in 2D corresponds to 39.3% confidence level.
        # Here we convert to 1-sigma Mahalanobis distance.
        pos_x_err = 0.408539 * np.sqrt(
            df_copy["err_ellipse_r0"] * df_copy["err_ellipse_r1"]
        )

    elif survey_name == "xmm":
        # For XMM, For a 2-dimensional Gaussian error distribution,
        # the sc_poserr radius reflects a 63% probability that the true source
        # position lies within this radius of the measured position. 
        # This correspond to sqrt(2) * mahalanobis radius, so to convert it
        # to 1 mahalanobis radius, we divide it by sqrt(2).
        pos_x_err = (1 / np.sqrt(2)) * df_copy["sc_poserr"]

    elif survey_name == "erass":
        # eRASS positional errors are given at 1-sigma confidence level.
        # So no conversion is needed.
        pos_x_err = df_copy["POS_ERR"]

    elif survey_name == "swift":
        # Swift positional errors are given at 90% confidence level.
        # For a 2D Gaussian error distribution, the 90% confidence level
        # corresponds to a Mahalanobis distance of 2.146.
        # According to the SPXS documentation, Err90 is the 90% confidence
        # radius, radial, assuming a Rayleigh distribution.
        pos_x_err = df_copy["Err90"] / 2.146

    df_copy["pos_x_err"] = pos_x_err

    return df_copy
