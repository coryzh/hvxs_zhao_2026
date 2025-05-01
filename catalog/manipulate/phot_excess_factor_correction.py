import pandas as pd
from numpy.polynomial import Polynomial


def get_correction(row: pd.Series):
    bp_rp = row["bp_rp"]

    if bp_rp < 0.5:
        poly = Polynomial(
            [1.154360, 0.033772, 0.032277]
        )

    elif bp_rp < 4.0:
        poly = Polynomial(
            [1.162004, 0.011464, 0.049255, -0.005879]
        )

    else:
        poly = Polynomial(
            [1.057572, 0.140537]
        )

    return poly(bp_rp)


def correct_bp_rp_excess_factor(df: pd.DataFrame) -> pd.DataFrame:
    necessary_columns = [
        "bp_rp",
        "phot_bp_rp_excess_factor"
    ]
    missing_cols = set(necessary_columns) - set(df.columns)
    print(missing_cols)
    if missing_cols:
        raise KeyError(
            "The input pandas.DataFrame object is missing the following "
            f"columns: {missing_cols}"
        )

    df["phot_bp_rp_excess_factor_corr"] = (
       df["phot_bp_rp_excess_factor"] - df.apply(get_correction, axis=1)
    )

    return df
