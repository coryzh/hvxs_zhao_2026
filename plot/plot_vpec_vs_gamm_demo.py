import pandas as pd

import config
import matplotlib.pyplot as plt
import numpy as np
from utils.vpec_functions import cartesian_peculiar_velocity_components
from utils.distances import FromLiterature
from utils.process_string import wrap_sign


def axes_settings(ax: plt.Axes) -> None:
    ax.set_xlabel(r"$\gamma\,(\mathrm{km~s^{-1}})$")
    ax.set_ylabel(r"$v_\mathrm{pec}\,(\mathrm{km~s^{-1}})$")
    ax.set_xlim(-500, 500)
    ax.set_ylim(None, 900)


def get_vpec(source_id: int, n_sim: int = 1000) -> dict:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources" / "combined_vpec_lolim_gt_200_unique_stage_9.csv"
    )

    df = pd.read_csv(in_file, index_col="source_id")
    df = df.rename(columns={"ra_gaia": "ra", "dec_gaia": "dec"})
    row = df.loc[source_id]

    pos_colnames = ["ra", "dec"]
    pm_colnames = ["pmra", "pmdec"]

    arg_dict = {}
    d_med = row["dist_med"]
    d_hi = d_med + row["E_dist"]
    d_lo = d_med - row["e_dist"]
    dist = FromLiterature(x_est=d_med, x_hi=d_hi, x_lo=d_lo, conf_level=0.68)
    # dist = SimpleInversion(row["parallax_corr"], row["parallax_error"])
    fit_results = dist.fit_gamma()
    d_gamma_dist = fit_results["distribution"]

    arg_dict["dist"] = d_gamma_dist.rvs(n_sim)

    gamma_grid = np.linspace(-1000, 1000, 10000)

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
        vpec_arr = cartesian_peculiar_velocity_components(
            v_r=gamma, **arg_dict
        )
        vpec[i] = np.median(vpec_arr)
        vpec_lo[i] = np.percentile(vpec_arr, 16)
        vpec_hi[i] = np.percentile(vpec_arr, 84)

    vpec_lo_min = min(vpec_lo)
    min_idx = np.argmin(vpec_lo)
    gamma_min = gamma_grid[min_idx]
    id_x = row["ID_x"]
    # source_id = row["source_id"]
    result_dict = {
        "vpec": vpec, "vpec_lo": vpec_lo, "vpec_hi": vpec_hi,
        "gamma": gamma_grid, "vpec_lo_min": vpec_lo_min,
        "gamma_min": gamma_min, "id_x": id_x
    }

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

    id_x = wrap_sign(vpec_dict["id_x"])
    ax.text(
        0.05, 0.85, s=f"X-ray ID: {id_x}\nGaia: {source_id}",
        transform=ax.transAxes, ha="left",
        va="bottom", fontsize=24
    )

    axes_settings(ax)

    plt.savefig(
        config.RESULTS_FIGURES_DIR / "vpec_vs_gamma"
        / f"{source_id}_vpec_vs_gamma.pdf"
    )


def main() -> None:
    make_figure(source_id=5946634735330650752)


if __name__ == "__main__":
    main()
