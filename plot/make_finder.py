import matplotlib.pyplot as plt
import plot.plot_settings as ps
import config
import pandas as pd
from astropy.io import fits
from typing import Any, List, Tuple
from utils.process_string import get_short_id
from astropy.wcs import WCS
from astropy.visualization import (
    LogStretch, ImageNormalize, ContrastBiasStretch
)
from astropy.visualization.wcsaxes import add_scalebar, SphericalCircle
from astropy.units import Quantity


class ImageData:
    def __init__(self, source_name: str, survey: str, band: str):
        self.source_name = source_name
        self.survey = survey
        self.band = band

    @property
    def name_short(self) -> str:
        return get_short_id(self.source_name)

    def load_image(self) -> Any:
        valid_surveys = ["panstarrs", "desi", "skymapper"]

        if self.survey not in valid_surveys:
            raise ValueError(
                f"{self.survey} is not a valid option. Choose from"
                f"{valid_surveys}."
            )

        img_file_path = (
            ps.IMAGE_DIR
            / f"{self.name_short}_{self.survey.lower()}_{self.band}.fits"
        )

        if not img_file_path.exists():
            raise FileNotFoundError(
                f"Not image file named {img_file_path.name} found in "
                f"{img_file_path.parent}."
            )

        hdul = fits.open(img_file_path)

        return hdul

    @property
    def img_wcs(self) -> WCS:
        hdul = self.load_image()

        return WCS(hdul[0].header)


def make_figure() -> Tuple[plt.Figure, List[plt.Axes]]:
    plt.style.use("mycustomised")
    fig = plt.figure(figsize=(48, 36))
    n_rows = 3
    n_cols = 4

    # fig.text(0.5, 0.08, "Right ascension", ha="center", va="center",
    #          fontsize=62)
    # fig.text(0.09, 0.5, "Declination", ha="center", va="center",
    #          rotation="vertical", fontsize=62)
    axs = []

    df = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR / "prime_sample"
        / "gold_sample_210525.csv"
    )

    for i, row in df.iterrows():
        # Initializing the ImageData object
        name = row["ID_x"]
        survey, band = row["image_from"].split(",")
        img_data = ImageData(name, survey, band)

        # Get image data and define contrast and bias
        hdul = img_data.load_image()
        data = hdul[0].data
        stretch = (
            ContrastBiasStretch(contrast=0.8, bias=0.5) + LogStretch(a=8e2)
        )
        # Create an ImageNormalize with LogStretch
        norm = ImageNormalize(
            vmin=min(data.flatten()), vmax=max(data.flatten()), stretch=stretch
        )

        # Initialize subplots.
        wcs = img_data.img_wcs
        ax = plt.subplot(n_rows, n_cols, i+1, projection=wcs)

        # Display image
        ax.imshow(data, origin="lower", cmap="gray_r", norm=norm)

        # Add scalebar
        add_scalebar(
            ax, length=Quantity(10, "arcsec"), color="r", label='10"',
            corner="bottom left", label_top=True, size_vertical=0.3,
            fontproperties=dict(size=40), width=2.0
        )

        # Add X-ray error circle
        r = SphericalCircle(
            (Quantity(row["ra_x"], "deg"), Quantity(row["dec_x"], "deg")),
            radius=Quantity(row["pos_x_err"], "arcsec"),
            edgecolor="r", facecolor="none", lw=2.0,
            transform=ax.get_transform("icrs")
        )
        ax.add_patch(r)

        # Add circle for Gaia counterpart
        g = SphericalCircle(
            (Quantity(row["ra_gaia"], "deg"),
             Quantity(row["dec_gaia"], "deg")),
            radius=Quantity(1, "arcsec"),
            edgecolor="cyan", facecolor="none", lw=2.0,
            transform=ax.get_transform("icrs")
        )
        ax.add_patch(g)
        # Add source name to the subplot
        x_max, y_max = img_data.img_wcs.array_shape

        band_and_survey_str = (
            f"{ps.SURVEY_NAME_DICT[img_data.survey]}, {img_data.band}"
        )
        ax.text(0.70 * x_max, 0.91 * y_max, img_data.name_short, fontsize=40,
                color="b")
        ax.text(0.04 * x_max, 0.91 * y_max, band_and_survey_str, fontsize=40,
                color="b")

        # Tick mark and label settings
        ax.set_xlabel("")
        ax.set_ylabel("")
        ax.tick_params(axis="x", labelbottom=False, bottom=False, top=False)
        ax.tick_params(axis="y", labelleft=False, left=False, right=False)
        axs.append(ax)
    plt.subplots_adjust(hspace=0.05, wspace=0.05)
    return fig, axs


def main() -> None:
    fig, axs = make_figure()
    plt.savefig(
        config.RESULTS_FIGURES_DIR / "finding_charts" / "combined_finders.pdf"
    )


if __name__ == "__main__":
    main()
