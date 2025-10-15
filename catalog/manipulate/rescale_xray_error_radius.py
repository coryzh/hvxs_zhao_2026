import config
import pandas as pd
import warnings
import numpy as np
import argparse
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def _validator(df: pd.DataFrame, survey_name: str) -> None:
    if "pos_x_err" in df.columns:
        warnings.warn(
            "pos_x_err column already exists in the DataFrame, "
            "while positional error is expected to be in its original form if"
            "the input DataFrame is from a (relatively)-raw X-ray source "
            "catalogue. Check how it was created.",
            UserWarning
        )

    if survey_name not in config.SURVEY_NAMES_SHORT:
        raise ValueError(
            f"{survey_name} is not a valid survey name. "
            f"Choose from {list(config.SURVEY_NAMES_SHORT)}"
        )


def _clean_up(df: pd.DataFrame, survey_name: str) -> pd.DataFrame:
    """remove unnecessary columns after calculating pos_x_err"""
    df_copy = df.copy()
    if survey_name == "csc":
        df_copy = df_copy.drop(
            columns=["err_ellipse_r0", "err_ellipse_r1"]
        )
    elif survey_name == "xmm":
        df_copy = df_copy.drop(columns=["sc_poserr"])
    elif survey_name == "erass":
        df_copy = df_copy.drop(columns=["POS_ERR"])
    elif survey_name == "swift":
        df_copy = df_copy.drop(columns=["Err90"])

    return df_copy


def calibrate_pos_xerr(
        df: pd.DataFrame, survey_name: str
) -> pd.DataFrame:
    df_copy = df.copy()
    logger.debug("Validating the input DataFrame ...")
    df_copy = _validator(df_copy, survey_name)

    logger.debug(f"Rescaling positional errors for {survey_name}")
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
    df_copy = _clean_up(df_copy, survey_name)

    return df_copy


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="rescale_xray_error_radius",
        description=(
            "Rescale the X-ray positional error radius from different survey"
            " catalogues to 1-sigma"
        )
    )

    parser.add_argument(
        "infile", help="Input CSV file containing the X-ray source catalogue"
    )

    parser.add_argument(
        "--survey", required=True, choices=config.SURVEY_NAMES_SHORT,
        help=(
            "Name of the X-ray survey, must be one of csc, xmm, erass, swift"
        )
    )

    parser.add_argument(
        "--outfile", required=False,
        help="Output CSV file to save the rescaled X-ray source catalogue"
    )

    parser.add_argument(
       "-v", "--verbose", action="store_true", help="Enable logging output"
    )

    args = parser.parse_args()

    # Basic logging config
    if args.verbose:
        level = logging.DEBUG
    else:
        level = logging.INFO

    in_file_path = Path(args.infile)

    log_file_path = in_file_path.parent / f"{Path(__file__).stem}.log"
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(
                log_file_path, mode="a"
            )
        ]
    )

    df_in = pd.read_csv(in_file_path)
    logger.info(
        f"Loaded data frame from {in_file_path}: {df_in.shape[0]} rows"
    )

    logger.info("Rescaling X-ray positional errors...")
    df_out = calibrate_pos_xerr(df_in, args.survey)

    if not args.outfile:
        out_path = (
            in_file_path.parent / f"{in_file_path.stem}_poserr_rescaled.csv"
        )
    else:
        out_path = Path(args.outfile)

    logger.info(
        "Rescaled X-ray positional errors, "
        f"output DataFrame shape: {df_out.shape}"
    )
    df_out.to_csv(out_path, index=False)
    logger.info(f"Saved output to {out_path}")
