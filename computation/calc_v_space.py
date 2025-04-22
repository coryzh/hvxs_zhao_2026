import config
import pandas as pd
import numpy as np
from tqdm import tqdm
from utils.utility_functions import (
    get_errors
)

from utils.vpec_functions import (
    cartesian_peculiar_velocity_components,
    galactocentric_cartesian_velocity
)

from computation.calc_v_min import (
    get_random_astrometry,
    get_random_distances_bailer_jones,
    imputation_bailer_jones,
    id_x_dict
)


def calc_vspace(
        df: pd.DataFrame, rv_col: str = "rv", id_col: str = "name",
        nrand: int = 1000
) -> pd.DataFrame:

    necessary_columns = {
        "ra", "dec",
        "pmra", "pmra_error",
        "pmdec", "pmdec_error",
        "r_med_photogeo", "r_lo_photogeo", "r_hi_photogeo"
    }

    if any([item not in df.columns for item in necessary_columns]):
        missing_cols = necessary_columns - set(df.columns)
        raise ValueError(
            "Not all required columns are in the input DataFrame. Missing "
            f"columns are {missing_cols}."
        )

    df_v_data = []
    for i, row in tqdm(df.iterrows()):
        astrometry_params = get_random_astrometry(
            row["ra"], row["dec"],
            row["pmra"], row["pmra_error"],
            row["pmdec"], row["pmdec_error"]
        )

        dist_rand = get_random_distances_bailer_jones(
            row["r_med_photogeo"], row["r_lo_photogeo"], row["r_hi_photogeo"],
            nrand=nrand
        )[0]

        rv_rand = np.random.randn(nrand) * row[f"{rv_col}_err"] + row[rv_col]

        args_rand = astrometry_params + (dist_rand, rv_rand)

        vspace = galactocentric_cartesian_velocity(
            *args_rand
        )[-1]

        vpec = cartesian_peculiar_velocity_components(
            *args_rand
        )

        vpec_med, e_vpec, E_vpec = get_errors(vpec)
        vspace_med, e_vspace, E_vspace = get_errors(vspace)
        row_data = [
            row[id_col],
            vpec_med, e_vpec, E_vpec, vspace_med, e_vspace, E_vspace
        ]
        df_v_data.append(row_data)
        # print(f"vspace: {vspace_med:.2f}, vpec: {vpec_med:.2f}")

    df_v = pd.DataFrame(
        data=df_v_data,
        columns=[
            id_col, "vpec_med", "e_vpec", "E_vpec",
            "vspace_med", "e_vspace", "E_vspace"
        ]
    )

    df_merged = pd.merge(df, df_v, on=id_col, how="left")

    return df_merged


def main() -> None:
    survey_name = "known_cobs"
    id_col = id_x_dict[survey_name]

    df = pd.read_csv(
        config.ROOT_DIR
        / "results" / survey_name / "catalogues"
        / f"catalog_{survey_name}_for_vpec.csv"
    )

    df = imputation_bailer_jones(df=df)

    df_out = calc_vspace(df, id_col=id_col)

    df_out.to_csv(
        config.RESULTS_CATALOGUE_DIR
        / "v_catalogs_contaminants" / f"{survey_name}_w_vpec_and_vspace.csv",
        index=False
    )


if __name__ == "__main__":
    main()
