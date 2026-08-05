import pandas as pd
import config

NEPOCHS = 8


def _load_catalogue() -> pd.DataFrame:
    file_path = (
        config.RESULTS_CATALOGUE_DIR
        / "published" / "ready_catalogues" / "gold.csv"
    )

    return pd.read_csv(file_path)


def prepare_catalogue(df: pd.DataFrame) -> pd.DataFrame:
    df = df.query(
        "dec_gaia >= -76 and dec_gaia <= 11"
    )

    cols_new_names = {
        "source_id": "target name",
        "ra_gaia": "right ascension",
        "dec_gaia": "declination",
        "phot_g_mean_mag": "minimum magnitude",
        "pmra": "proper motion ra",
        "pmdec": "proper motion dec",
    }

    df = df.rename(columns=cols_new_names)

    df["target name"] = df["target name"].apply(lambda x: f"Gaia DR3 {x}")
    df["target type"] = "Candidate_XB*"
    df["equinox"] = "2000"
    df["bandpass"] = "V"
    df["maximum magnitude"] = df["minimum magnitude"]

    df["proper motion ra"] = df["proper motion ra"] / 1e3
    df["proper motion dec"] = df["proper motion dec"] / 1e3
    df["maximum lunar phase"] = 100
    df["visits"] = NEPOCHS
    df["ranking"] = "High"

    cols = [
        "target name", "target type", "right ascension", "declination",
        "equinox", "bandpass", "minimum magnitude", "maximum magnitude",
        "maximum lunar phase", "proper motion ra", "proper motion dec",
        "visits", "ranking"

    ]

    return df[cols]


def main() -> None:
    df = _load_catalogue()
    df_prepared = prepare_catalogue(df)

    out_path = (
        config.RESULTS_CATALOGUE_DIR / "salt_2026_2"
        / "target_catalogue_p1.csv"
    )
    df_prepared.to_csv(out_path, index=False)


if __name__ == "__main__":
    main()
