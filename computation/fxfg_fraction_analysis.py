import config
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Tuple
from plot.plot_settings import BINNING_PARAM_LABEL_DICT
# from plot.plot_settings import DIST_INFERENCE_COLOR_DICT


def get_fraction(df: pd.DataFrame, bin_on: str = "dist_med") -> Tuple[np.ndarray, np.ndarray]:
    if "vpec" in bin_on.lower():
        print(f"Binning on {bin_on}; assuming that means 'vpec_min_lo', i.e., 1 sigma lower limit on vpec_min.")
        bin_on = "vpec_min_lo"
        df[bin_on] = df["vpec_min_med"] - df["e_vpec_min"]

    elif "dist" in bin_on.lower():
        print(f"Binning on {bin_on}; assuming that means 'dist_med'.")
        bin_on = "dist_med"

    else:
        raise ValueError(f"{bin_on} is not a valid option. It should be either v_pec or distance.")

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

    # frac = hist[0] / hist_filtered[0]

    return bins, frac


def plot_fraction(df: pd.DataFrame, bin_on: str = "dist_med") -> None:

    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(12, 10))
    bins, frac = get_fraction(df, bin_on=bin_on)

    threshold = 1e-4
    saturation_idx = np.where(np.abs(np.diff(frac)) < threshold)[0][0]
    bin_sat = bins[saturation_idx]
    frac_sat = frac[saturation_idx]
    print(f"The fraction saturates around {bin_on}={bin_sat}, at around {frac_sat:.2f}")

    ax.plot(bins, frac, marker="o", mfc="r", mec="k", ms=7, color="k")

    ax.set_xlabel(BINNING_PARAM_LABEL_DICT[bin_on])
    ax.set_ylabel(r"Cumulative fraction of high-$F_X/F_G$ sources")
    # for key, color in DIST_INFERENCE_COLOR_DICT.items():
    #     df_filtered = df[df["distance_inference"] == key]
    #     bins, frac = fraction(df_filtered, bin_on=bin_on)
    #     ax.plot(bins, frac, marker="o", mfc=color, mec="k", ms=5)
    #     # ax.step(bins, frac, where="post", color=color, label=key)

    ax.axhline(y=frac_sat, lw=1.0, dashes=(5, 3), color="r")
    ax.axvline(x=bin_sat, lw=1.0, dashes=(5, 3), color="r")

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
