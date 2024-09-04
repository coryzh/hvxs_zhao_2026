import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import config
import seaborn as sns
from matplotlib.ticker import ScalarFormatter

colors = sns.color_palette("hls", 3)
lum_x_grid = 10 ** np.arange(30.0, 35.0, 1.0)
color_dict = {
    "csc": colors[0], "xmm": colors[1], "erass": colors[2]
}

label_dict = {
    "csc": "CSC", "xmm": "4XMM", "erass": "eRASS"
}


def make_figure() -> None:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_gt_200.csv")
    for key, val in color_dict.items():
        _filter = df["from"] == key
        df_filtered = df[_filter]

        x = df_filtered["vpec_min_med"] - df_filtered["e_vpec_min"]
        y = df_filtered["lum_x"]

        ax.scatter(x, y, s=70, fc=color_dict[key], ec="k", marker="o", label=label_dict[key], alpha=0.8)

    for i in range(1, len(lum_x_grid)):
        _filter_lum_x = (df["lum_x"] >= lum_x_grid[i - 1]) & (df["lum_x"] <= lum_x_grid[i])
        df = df.dropna(subset=["lum_x_err"])
        df_filtered_lum_x = df[_filter_lum_x]
        mean_lx_err = np.median(df_filtered_lum_x.lum_x_err.values)
        x = 1050
        y = 0.5 * (lum_x_grid[i - 1] + lum_x_grid[i])
        ax.errorbar(x=x, y=y, xerr=0, yerr=mean_lx_err, ls="none", ecolor="k",
                    lw=1.5, marker="s", mfc="k", mec="k", capsize=5.0)

    ax.set_yscale("log")
    ax.set_xscale("log")
    ax.set_xlabel(r"1 σ lower limit on $v_\mathrm{pec, min}\,(\mathrm{km~s^{-1}}$)")
    ax.set_ylabel(r"$L_X\,(\mathrm{erg~s^{-1}})$")

    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    ax.set_xticks([200, 300, 400, 600, 800, 1000])

    # plt.legend(loc="lower right")
    plt.savefig(config.RESULTS_FIGURES_DIR / "lx_vs_vpec_min_lolim.pdf")


if __name__ == "__main__":
    make_figure()
