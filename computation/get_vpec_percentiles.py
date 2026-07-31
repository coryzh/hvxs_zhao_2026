import config
import pandas as pd
from utils.ecdf import get_ecdf
from scipy.interpolate import interp1d


def get_percentage(object_type: str, vpec_lim: float) -> float:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "v_catalogs_contaminants"
        / f"{object_type}_vpec.csv"
    )
    df = pd.read_csv(in_file)

    vpec = df["vpec_med"].values
    x, y = get_ecdf(vpec, normalised=True)

    # inverted eCDF
    ecdf_interp = interp1d(x, y, fill_value=(0.0, 1.0), bounds_error=False)
    percentage = ecdf_interp(vpec_lim)

    return percentage


def main() -> None:
    object_types = {"ab": "Active binaries", "as": "Active stars", "cv": "CVs", "yso": "YSOs"}
    df = pd.DataFrame(columns=["Object types", "40 km/s", "80 km/s", "120 km/s", "150 km/s", "200 km/s"])
    for key, val in object_types.items():
        p40 = get_percentage(key, 40.0)
        p80 = get_percentage(key, 80.0)
        p120 = get_percentage(key, 120.0)
        p150 = get_percentage(key, 150.0)
        p200 = get_percentage(key, 200.0)

        row_df = pd.DataFrame([[val, p40, p80, p120, p150, p200]], columns=df.columns)
        df = pd.concat([df, row_df], ignore_index=True)

    out_file = config.RESULTS_CATALOGUE_DIR / "contaminants_percentages.csv"
    df.to_csv(out_file, index=False)


if __name__ == "__main__":
    main()
