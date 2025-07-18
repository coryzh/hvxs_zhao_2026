import config
import pandas as pd
from utils.n_agn import n_agn_r, n_agn


def estimate_tot_agn(s: float, df: pd.DataFrame) -> None:
    r_err = df["pos_x_err"] / 60.0  # in units of arcmin

    n_agn = n_agn_r(s=s, r=r_err)

    print(
        f"There are about {n_agn.sum():.1f} AGNs brighter than "
        f"{s: .2e} erg/s/cm^2"
    )


def main() -> None:
    tot_area = 1
    n_source_tot = 930203
    flux_limit = 2e-14
    agn_density = n_agn(s=flux_limit)
    agn_tot = agn_density * tot_area
    print(
        f"Expected {agn_tot:.2e} AGNs within a total area of {tot_area} deg^2,"
        f" given a flux limit of {flux_limit:.2e} erg/s/cm^2. This makes "
        f" {agn_tot / n_source_tot:.2f}% of the catalogue."
    )
    # df = pd.read_csv(
    #     config.RESULTS_CATALOGUE_DIR / "ready_catalogues"
    #     / "hvxs.csv"
    # )

    # estimate_tot_agn(s=1e-14, df=df)


if __name__ == "__main__":
    main()
