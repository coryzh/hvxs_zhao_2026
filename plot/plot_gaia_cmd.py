import pandas as pd
from gaia_cmd_plotter.gaia_cmd_axis import GaiaCMDAxis
import matplotlib.pyplot as plt
import numpy as np

import config


def make_cmd(df: pd.DataFrame) -> None:
    plt.style.use("mycustomised")
    fig = plt.figure(figsize=(10, 10))
    ax = GaiaCMDAxis(fig)

    bp_rp = df["bp_rp"]
    dist = df["dist_med"]
    g_abs = df["phot_g_mean_mag"] - 5.0 * np.log10(dist) - 10.0

    ax.scatter(bp_rp, g_abs, marker="o", s=80, ec="k", fc="limegreen")
    out_file = config.RESULTS_FIGURES_DIR / "vlt_p115_targets_gaia_cmd.pdf"
    plt.savefig(out_file)


if __name__ == "__main__":
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "vlt_p115" /"vlt_p115_targets_curated.csv")
    make_cmd(df)
