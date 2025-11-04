import numpy as np
import config
import pandas as pd
import matplotlib.pyplot as plt
import data_schema as ds
from plot.plot_settings import SURVEY_COLOR_DICT_X, SURVEY_NAME_DICT_X
from typing import Tuple
from scipy.stats import gaussian_kde
from log.log_config import configure_logging
from pathlib import Path
import logging

logger = logging.getLogger(__name__)
configure_logging(level=logging.INFO, app_name=Path(__file__).stem)


def _add_from_colunmn(df: pd.DataFrame) -> pd.DataFrame:
    df_copy = df.copy()
    id_x_col = ds.CombinedCatalogueSchema.ID_x
    df_copy["from"] = (
        df_copy[id_x_col]
        .astype(str)
        .str
        .split(' ')
        .str[0]
    ).map(config.SURVEY_ID_IDENTIFIERS)
    logger.info("Added 'from' column to the DataFrame.")

    return df_copy


def _load_catalogue() -> pd.DataFrame:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "nway_matched_results"
        / "xray_catalogue_concatenated_deduplicated.csv"
    )

    df = pd.read_csv(in_file)
    logger.info(
        f"Loaded deduplicated concatenated X-ray catalogue from {in_file} "
        f"with {df.shape[0]} sources."
    )

    return df


def _save_to_figure(out_file: Path) -> None:
    plt.savefig(out_file)
    logger.info(f"Saved figure to {out_file}.")


def make_figure() -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("mycustomised")
    fig, ax = plt.subplots(1, 1, figsize=(10, 10))

    return fig, ax


def axes_settings(ax: plt.Axes) -> None:
    ax.set_xlabel(r"$\delta_\mathrm{x,g} / r_\mathrm{err, x}$")
    ax.set_ylabel(r"Probability density")
    ax.set_xlim(0, None)
    ax.set_ylim(0, None)


def add_histogram(df: pd.DataFrame, ax: plt.Axes, from_catalog: str) -> None:
    # for key, val in SURVEY_COLOR_DICT.items():
    # sep_sigma_all = df["sep_x_g"] / df["pos_x_err"]
    # bins = np.linspace(sep_sigma_all.min(), sep_sigma_all.max(), 100)
    df_filtered = df[df["from"] == from_catalog]
    sep = df_filtered[ds.CombinedCatalogueSchema.sep_x_g_sigma].values

    kde = gaussian_kde(sep)
    sep_range = np.arange(0, max(sep), 0.01)

    ax.plot(
        sep_range, kde(sep_range), lw=2.0,
        color=SURVEY_COLOR_DICT_X[from_catalog],
        label=SURVEY_NAME_DICT_X[from_catalog]
    )
    logger.info(
        f"Added histogram for {from_catalog} with "
        f"{df_filtered.shape[0]} sources."
    )
    # _ = ax.hist(sep, bins=bins, density=True, histtype="step",
    # ec=SURVEY_COLOR_DICT[from_catalog],
    #             label=SURVEY_NAME_DICT[from_catalog], lw=1.5)


def make_histogram(df: pd.DataFrame) -> None:
    fig, ax = make_figure()
    for key in SURVEY_NAME_DICT_X.keys():
        add_histogram(df, ax, from_catalog=key)

    axes_settings(ax)
    plt.legend(loc="upper right")


if __name__ == "__main__":
    df = _load_catalogue()
    df = _add_from_colunmn(df)
    make_histogram(df)
    _save_to_figure(
        config.RESULTS_FIGURES_DIR / "for_revision" / "sep_x_g_histogram.pdf"
    )
