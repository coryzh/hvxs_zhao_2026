import numpy as np
import pandas as pd

coe_dict = {
    "V": np.array([-0.01760, -0.006860, -0.1732]),
    "R": np.array([-0.003226, 0.3833, -0.1345]),
    "I": np.array([0.02085, 0.7419, -0.09631])
}


def g_to_johnson(gmag: float, bp_rp: float) -> dict:
    dict_out = {}
    for key, a in coe_dict.items():
        offset = a[0] + a[1] * bp_rp + a[2] * bp_rp ** 2
        dict_out[key] = gmag - offset

    return dict_out


def g_to_johnson_for_eso(row: pd.Series) -> str:
    dict_out = {}
    gmag = row["phot_g_mean_mag"]
    bp_rp = row["bp_rp"]
    for key, a in coe_dict.items():
        offset = a[0] + a[1] * bp_rp + a[2] * bp_rp ** 2
        dict_out[key] = gmag - offset

    str_out = ",".join([f"{key}={val:.2f}" for key, val in dict_out.items()])
    return str_out
