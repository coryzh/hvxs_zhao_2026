import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Tuple
import numpy as np
import config


def make_figure() -> Tuple[plt.Figure, plt.Axes]:
    plt.style.use("standardcartesian")

    fig, ax = plt.subplots(1, 1, figsize=(10, 10))
    y_extent = 10
    xlim = (-4, 4)
    ylim = (-0.5, y_extent)

    ax.set_xlim(xlim)
    ax.set_ylim(ylim)

    # Move spines to the center
    ax.spines['left'].set_position('zero')
    ax.spines['bottom'].set_position('zero')
    ax.spines["left"].set_linewidth(2.0)
    ax.spines["bottom"].set_linewidth(2.0)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)

    # Add arrows using patches.Arrow
    arrow_x = patches.FancyArrowPatch((xlim[1] * 0.999, 0), (xlim[1], 0),
                                      arrowstyle='->', mutation_scale=20, lw=1.5, color='k')
    arrow_y = patches.FancyArrowPatch((0, ylim[1] * 0.999), (0, ylim[1]),
                                      arrowstyle='->', mutation_scale=20, lw=1.5, color='k')
    ax.add_patch(arrow_x)
    ax.add_patch(arrow_y)

    # Add origin label
    ax.text(0.49, -0.01, '0', ha='right', va='top', transform=ax.transAxes)

    # Add x and y axis labels
    ax.set_xlabel(r'$\varpi$', loc='right')
    ax.set_ylabel(r'$|\varpi|/\sigma_\varpi$', loc='top', rotation=0)

    ax.set_xticks([])
    ax.set_yticks([])

    return fig, ax


def paint_colors(ax: plt.Axes) -> None:
    ylim = ax.get_ylim()
    xlim = ax.get_xlim()

    simple_inversion_parallax_snr_lolimit = 5.0
    simple_inversion_parallax_lolim = 0.1
    simple_inversion_horizontal_b = np.linspace(simple_inversion_parallax_lolim, xlim[1], 100)
    simple_inversion_vertical_b = np.linspace(simple_inversion_parallax_snr_lolimit, ylim[1], 100)

    bayesian_parallax_snr_lolimit = 0.5
    bayesian_parallax_lolim = -2.0
    bayesian_horizontal_b = np.linspace(bayesian_parallax_lolim, xlim[1], 100)
    bayesian_vertical_b = np.linspace(bayesian_parallax_snr_lolimit, ylim[1], 100)

    # Plot the boundary.
    ax.plot(simple_inversion_horizontal_b,
            np.full(len(simple_inversion_horizontal_b), simple_inversion_parallax_snr_lolimit), ls="-",
            lw=1.5, color="k")
    ax.plot(np.full(len(simple_inversion_vertical_b), simple_inversion_parallax_lolim),
            simple_inversion_vertical_b, ls="-", lw=1.5, color="k")

    ax.plot(bayesian_horizontal_b,
            np.full(len(bayesian_horizontal_b), bayesian_parallax_snr_lolimit), ls="-",
            lw=1.5, color="k")
    ax.plot(np.full(len(bayesian_vertical_b), bayesian_parallax_lolim),
            bayesian_vertical_b, ls="-", lw=1.5, color="k")

    x_range_simple_inversion = np.linspace(simple_inversion_parallax_lolim, xlim[1], 100)
    x_range_bayesian = np.linspace(bayesian_parallax_lolim, xlim[1], 100)
    y_range_bayesian = np.linspace(simple_inversion_parallax_snr_lolimit, ylim[1], 100)

    x_range_fixed_distance = np.linspace(bayesian_parallax_lolim, xlim[1], 100)
    y_range_fixed_distance = np.linspace(0, ylim[1], 100)

    # Color-fill the regions.
    # Fill the simple-inversion region
    fill_alpha = 0.3
    ax.fill_between(x=x_range_simple_inversion, y1=simple_inversion_parallax_snr_lolimit, y2=ylim[1],
                    fc="green", alpha=fill_alpha, hatch='/', label="Simple inversion")

    # Fill the Bayesian region
    ax.fill_between(x=x_range_bayesian, y1=bayesian_parallax_snr_lolimit,
                    y2=simple_inversion_parallax_snr_lolimit, fc="orange", alpha=fill_alpha,
                    hatch="+", label="Bayesian")
    ax.fill_betweenx(y=y_range_bayesian, x1=bayesian_parallax_lolim, x2=simple_inversion_parallax_lolim,
                     fc="orange", alpha=fill_alpha, hatch="+")

    # Fill the fixed-distance region
    ax.fill_between(x=x_range_fixed_distance, y1=0, y2=bayesian_parallax_snr_lolimit, fc="r", alpha=fill_alpha,
                    hatch="o")
    ax.fill_betweenx(y=y_range_fixed_distance, x1=xlim[0], x2=bayesian_parallax_lolim, fc="r", alpha=fill_alpha,
                     hatch="o")


def add_annotation(ax: plt.Axes) -> None:
    pass

def plot() -> None:
    fig, ax = make_figure()
    paint_colors(ax)
    add_annotation(ax)
    plt.savefig(config.RESULTS_FIGURES_DIR / "test_dist_diagram.pdf")


if __name__ == "__main__":
    plot()
