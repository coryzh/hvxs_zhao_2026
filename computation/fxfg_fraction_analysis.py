import config
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple
from plot.plot_settings import DIST_INFERENCE_COLOR_DICT


def fraction(df: pd.DataFrame, bin_on: str = "dist_med") -> Tuple[np.ndarray, np.ndarray]:
    bin_data = df[bin_on]

    bins = np.linspace(bin_data.sort_values(ascending=True, ignore_index=True)[1], bin_data.max(), 50)
    _filter = (df["fx_fg"] - df["fx_fg_err"] >= np.power(10, df["bp_rp"] - 3.5))
    df_filtered = df[_filter]

    frac = np.zeros(len(bins))
    for i, val in enumerate(bins):
        count_df = (df[bin_on] <= val).sum()
        count_df_filtered = (df_filtered[bin_on] <= val).sum()
        frac[i] = count_df_filtered / count_df
    # hist = np.histogram(df[bin_on], bins=bins, cumulative=)
    # hist_filtered = np.histogram(df_filtered[bin_on], bins=bins)
    # print(hist[0], hist_filtered[0])
    print(bins, frac)
    # frac = hist[0] / hist_filtered[0]

    return bins, frac


def plot_fraction(df: pd.DataFrame, bin_on: str = "dist_med") -> None:

    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    bins, frac = fraction(df, bin_on=bin_on)
    ax.plot(bins, frac, marker="o", mfc="r", mec="k", ms=5, color="k")

    ax.set_xlabel("$d$ (kpc)")
    ax.set_ylabel(r"Fraction high-$F_X/F_G$ sources ($\leq d$)")
    # for key, color in DIST_INFERENCE_COLOR_DICT.items():
    #     df_filtered = df[df["distance_inference"] == key]
    #     bins, frac = fraction(df_filtered, bin_on=bin_on)
    #     ax.plot(bins, frac, marker="o", mfc=color, mec="k", ms=5)
    #     # ax.step(bins, frac, where="post", color=color, label=key)

    out_root = config.RESULTS_FIGURES_DIR / "frac_of_high_ratio_sources"
    if not out_root.exists():
        out_root.mkdir()

    out_file = out_root / f"frac_vs_{bin_on}.pdf"
    plt.savefig(out_file)


def main() -> None:
    in_file = (config.RESULTS_CATALOGUE_DIR / "high-v_sources"
               / "combined_vpec_med_gt_0_unique.csv")
    df = pd.read_csv(in_file)
    _filter = (df["distance_inference"] != "fixed_at_1")
    df = df[_filter]
    plot_fraction(df, bin_on="dist_med")


if __name__ == "__main__":
    main()
