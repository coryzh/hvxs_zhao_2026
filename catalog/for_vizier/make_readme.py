import cdspyreadme
import config
import sys
from typing import Literal


cds_tables_maker = cdspyreadme.CDSTablesMaker()

table_descriptions = {
    "hvxs": "Catalog of High-Velocity X-ray Sources (Sect )."
            " This catalog contains X-ray sources with 1 sigma lower limit of"
            " minimum peculiar velocity greater than 200 km/s and cleaned ",
            " following the steps in Section 2.9."

    "control": "The control sample. For more details, see Section 2.11."
}

table_titles = {
    "hvxs": "High-Velocity X-ray Sources Catalogue",
    "control": "Control Sample Catalogue"
}

TABLE_AUTHOR = "Yue Zhao"
TABLE_DATE = "2026"
PUT_REF = "II/246"
ABSTRACT = (
    "We perform a comprehensive search for high-velocity X-ray sources with "
    "large X-ray/optical flux ratios (F_X/F_G), identifying candidates for "
    "interacting black hole or neutron star binaries potentially accelerated "
    "by supernova natal kicks. We cross-match X-ray points sources from a "
    "variety of catalogues (Chandra, XMM-Newton, Swift and "
    "eROSITA) with Gaia DR3. Using Gaia coordinates, parallaxes, "
    "and proper motions, we compute peculiar velocities (vpec) relative to "
    "Galactic disc rotation. Remaining agnostic about radial velocities "
    "(RVs), we vary RVs to find the minimum possible vpec values (vpec_min). "
    "Uncertainties on vpec_min are estimated via Monte Carlo resampling, "
    "and we select X-ray sources that have 1 sigma lower limits on "
    "vpec_min ≥ 200 km/s and high fxfg values. We show that this velocity "
    "threshold excludes most contaminants (e.g., cataclysmic variables and "
    "active binaries) while retaining a sensible fraction of compact object "
    "binaries, demonstrating that vpec could serve as an effective indicator "
    "for the presence of a neutron star or black hole companion. Our "
    "selection yields a sample of 2372 sources, from which we construct a "
    "gold sample of 7 sources that have relatively well-constrained "
    "astrometry and confident optical counterparts. Follow-up is necessary to "
    "confirm and characterise their high-energy emission, as well as a "
    "Galactic disc vs. halo origin."
)


def _get_table_path(opt: Literal["hvxs", "control"]) -> str:
    table_dir = config.RESULTS_CATALOGUES_FOR_REVISION / "for_vizier"
    print(
        f"Reading table from {table_dir}. Table exists: {table_dir.exists()}"
    )
    return table_dir / f"{opt}_for_vizier.csv"


def add_tables(opt: Literal["hvxs", "control"]) -> None:
    table_path = str(_get_table_path(opt))
    cds_tables_maker.addTable(table_path, description=table_descriptions[opt])
    cds_tables_maker.writeCDSTables()
    cds_tables_maker.title = table_titles[opt]
    cds_tables_maker.authors = TABLE_AUTHOR
    cds_tables_maker.date = TABLE_DATE
    cds_tables_maker.putRef = PUT_REF
    cds_tables_maker.abstract = ABSTRACT


def make_readme() -> None:
    add_tables("hvxs")
    add_tables("control")

    cds_tables_maker.makeReadMe(out=sys.stdout)


if __name__ == "__main__":
    make_readme()
