from pathlib import Path

SURVEY_NAME = "combined"
SURVEY_NAMES_SHORT = ["csc", "xmm", "erass", "swift"]
SURVEY_ID_IDENTIFIERS = {
    "2CXO": "csc",
    "4XMM": "xmm",
    "1eRASS": "erass",
    "2SXPS": "swift"
}

SURVEY_SKY_AREA = {
    "csc": 730.0,
    "xmm": 1383.0,
    "erass": 20626.4,
    "swift": 3790.0
}
# Path to the root of the project
ROOT_DIR = Path(__file__).parent.parent

# Log directory
LOG_DIR = ROOT_DIR / "logs"

# Path to the data directory
DATA_DIR = ROOT_DIR / "data" / SURVEY_NAME

# Path to the raw data
DATA_CATALOGUES = DATA_DIR / "catalogues"
DATA_DIR_MISC = DATA_DIR / "misc"
DATA_DIR_RAW = DATA_DIR / "raw"
DATA_DIR_INTERMEDIATE = DATA_DIR / "intermediate"
DATA_DIR_PROCESSED = DATA_DIR / "processed"

# Path to results directory
RESULTS_DIR = ROOT_DIR / "results" / SURVEY_NAME
RESULTS_CATALOGUE_DIR = RESULTS_DIR / "catalogues"
RESULTS_LATEX_TABLE_DIR = RESULTS_DIR / "latex_tables"
RESULTS_FIGURES_DIR = RESULTS_DIR / "figures"
RESULTS_GALACTIC_ORBITS = RESULTS_DIR / "galactic_orbits"
RESULTS_DISTANCES_FROM_CLUSTERS = RESULTS_DIR / "distances_from_clusters"
RESULTS_PLANE_CROSSINGS = RESULTS_DIR / "plane_crossings"
RESULTS_PHOTOMETRY_DIR = RESULTS_DIR / "photometry"
RESULTS_HIGHLIGHTS = RESULTS_DIR / "highlights"


# MISC
GOOGLE_SHEET_CREDENTIALS_JSON = (
    ROOT_DIR / "steady-petal-476013-r9-b6b15714949e.json"
)


def make_dir() -> None:
    for name, value in globals().items():
        if isinstance(value, Path):
            if not value.exists():
                value.mkdir(parents=True)
                print(f"Directory {value} created.")


if __name__ == "__main__":
    make_dir()
