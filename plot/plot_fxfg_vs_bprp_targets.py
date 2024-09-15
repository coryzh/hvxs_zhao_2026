import matplotlib.pyplot as plt
import pandas as pd
import config
import numpy as np
from pathlib import Path
from matplotlib.ticker import ScalarFormatter


def make_figure(df: pd.DataFrame, out_file: Path = None) -> None:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    df_all = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_gt_200.csv")

    x_all = df_all["bp_rp"]
    y_all = df_all["fx_fg"]
    x_target = df["bp_rp"]
    y_target = df["fx_fg"]
    y_target_err = df["fx_fg_err"]

    ax.scatter(x_all, y_all, s=0.6, marker=".", fc="k", ec="k")
    ax.errorbar(x_target, y_target, yerr=y_target_err, marker="o", ms=8.0, mfc="limegreen", mec="k",
                ls="none", ecolor="k", capsize=3)

    ax.set_yscale("log")
    ax.get_yaxis().set_major_formatter(ScalarFormatter())
    ax.set_yticks([1e-5, 1e-4, 0.001, 0.01, 0.1, 1, 10])
    ax.set_yticklabels([r"$10^{-5}$", r"$10^{-4}$", "0.001", "0.01", "0.1", "1", "10"])

    bp_rp_min, bp_rp_max = ax.get_xlim()
    bp_rp_line = np.linspace(bp_rp_min, bp_rp_max, 100)
    fxfg_line = 10 ** (bp_rp_line - 3.5)
    ax.plot(bp_rp_line, fxfg_line, lw=1.5, color="r", dashes=(5, 8))

    ax.set_xlim(-0.8, 5.0)
    ax.set_xlabel(f"Bp$-$Rp")
    ax.set_ylabel(f"$F_X / F_G$")

    if out_file is not None:
        plt.savefig(out_file)


def main() -> None:
    df_targets = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources"
                             / "vlt_p115" / "vlt_p115_targets_w_observability.csv")
    make_figure(df_targets, out_file=config.RESULTS_FIGURES_DIR / "high-v_sources"/ "vlt_p115" / "fxfg_vs_bprp.pdf")


if __name__ == "__main__":
    main()
