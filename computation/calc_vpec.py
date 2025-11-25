from utils.vpec_functions import cartesian_peculiar_velocity_components
from utils.distances import ExponentialPriorModel
import pandas as pd


def _calc_distance(
        df: pd.DataFrame, parallax_col: str = "parallax_corr",
        parallax_err_col: str = "parallax_error"
) -> pd.Series:
    pass
