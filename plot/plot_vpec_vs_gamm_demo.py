import pandas as pd

import config
import matplotlib.pyplot as plt
import numpy as np
from utils.vpec_functions import galactocentric_cartesian_velocity
from utils.distances import simple_inversion


def axes_settings(ax: plt.Axes) -> None:
    ax.set_xlabel(r"$\gamma\,(\mathrm{km~s^{-1}})$")
    ax.set_ylabel(r"$v_\mathrm{pec}\,(\mathrm{km~s^{-1}})$")
    ax.set_xlim(-200, 200)


def get_vpec(source_id: int, n_sim: int = 1000) -> dict:
    in_file = config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_lolim_gt_200.0_unique.csv"
    df = pd.read_csv(in_file, index_col="source_id")
    row = df.loc[source_id]

    pos_colnames = ["ra", "dec"]
    pm_colnames = ["pmra", "pmdec"]

    arg_dict = {}

    dist = simple_inversion(row["parallax"], row["parallax_error"])
    dist_rand = dist.gaussian_sampler(nrand=n_sim)
    arg_dict["dist"] = dist_rand

    gamma_grid = np.linspace(-200, 200, 1000)

    for par_name in pos_colnames:
        par_arr = np.full(shape=n_sim, fill_value=row[par_name])
        arg_dict[par_name] = par_arr

    for par_name in pm_colnames:
        par_val = row[par_name]
        par_err = row[f"{par_name}_error"]

        par_rand = par_val + par_err * np.random.randn(n_sim)
        arg_dict[par_name] = par_rand

    vpec = np.zeros(len(gamma_grid))
    vpec_lo = np.zeros(len(gamma_grid))
    vpec_hi = np.zeros(len(gamma_grid))

    for i, gamma in enumerate(gamma_grid):
        vpec_arr = galactocentric_cartesian_velocity(v_r=gamma, **arg_dict)
        vpec[i] = np.median(vpec_arr)
        vpec_lo[i] = np.percentile(vpec_arr, 16)
        vpec_hi[i] = np.percentile(vpec_arr, 84)

    vpec_lo_min = min(vpec_lo)
    min_idx = np.argmin(vpec_lo)
    gamma_min = gamma_grid[min_idx]
    id_x = row["ID_x"]
    # source_id = row["source_id"]
    result_dict = {"vpec": vpec, "vpec_lo": vpec_lo, "vpec_hi": vpec_hi, "gamma": gamma_grid,
                   "vpec_lo_min": vpec_lo_min, "gamma_min": gamma_min, "id_x": id_x}

    return result_dict


def make_figure(source_id: int, n_sim: int = 1000) -> None:
    vpec_dict = get_vpec(source_id, n_sim)

    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    x = vpec_dict["gamma"]
    y = vpec_dict["vpec"]
    y1 = vpec_dict["vpec_lo"]
    y2 = vpec_dict["vpec_hi"]
    x_min = vpec_dict["gamma_min"]
    y1_min = vpec_dict["vpec_lo_min"]

    ax.plot(x, y, lw=2.0, color="k")
    ax.fill_between(x, y1=y1, y2=y2, fc="g", alpha=0.4)
    ax.plot(x_min, y1_min, "ro", ms=14, mec="k", mew=1.5)
    ax.plot(x_min, min(y), marker="s", mfc="w", ms=14, mec="k", mew=1.5)

    ax.text(0.05, 0.9, s=vpec_dict["id_x"], transform=ax.transAxes, ha="left", va="bottom", fontsize=24)

    axes_settings(ax)

    plt.savefig(config.RESULTS_FIGURES_DIR / f"{source_id}_vpec_vs_gamma.pdf")


def main() -> None:
    make_figure(source_id=295373903197621504)


if __name__ == "__main__":
    main()
