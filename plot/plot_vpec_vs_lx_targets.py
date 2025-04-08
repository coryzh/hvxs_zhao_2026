import config
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from matplotlib.ticker import ScalarFormatter


def make_figure(df: pd.DataFrame, out_file: Path = None) -> None:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    df_all = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources" / "combined_vpec_lolim_gt_150.0.csv"
    )

    x_all = df_all["vpec_min_med"] - df_all["e_vpec_min"]
    y_all = df_all["lum_x"]
    x_target = df["vpec_min_med"] - df["e_vpec_min"]
    y_target = df["lum_x"]

    ax.scatter(x_all, y_all, s=0.6, marker=".", fc="k", ec="k")
    ax.errorbar(
        x_target, y_target, yerr=0, marker="o", ms=8.0, mfc="limegreen",
        mec="k", ls="none", ecolor="k", capsize=3
    )

    ax.set_yscale("log")
    ax.set_xscale("log")

    ax.get_xaxis().set_major_formatter(ScalarFormatter())
    ax.set_xticks([200, 300, 400, 600, 800, 1000])

    ax.set_xlabel(
        r"$1\,\sigma$ lower limit on "
        r"$v_\mathrm{pec, min}\,(\mathrm{km~s^{-1}})$"
    )
    ax.set_ylabel(r"$L_X\,(\mathrm{erg~s^{-1}})$")

    if out_file is not None:
        plt.savefig(out_file)


def main() -> None:
    df_targets = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR / "high-v_sources"
        / "vlt_p115" / "vlt_p115_targets_curated.csv"
    )
    make_figure(
        df_targets,
        out_file=(
            config.RESULTS_FIGURES_DIR
            / "high-v_sources" / "vlt_p115" / "lx_vs_vpec_min.pdf"
        )
    )


if __name__ == "__main__":
    main()
