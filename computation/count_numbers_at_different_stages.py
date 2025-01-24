import pandas as pd
import config


def get_catalog_names(vpec_lim: float = 150, mode: str = "lolim") -> dict:
    catalog_names = {}
    stages = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "8a", "9"]

    for i, stage in enumerate(stages):
        key = f"stage_{stage}"
        catalog_names[key] = f"combined_vpec_{mode}_gt_{vpec_lim}_unique_{key}.csv"

    return catalog_names


def count(vpec_lim: float = 150, mode: str = "lolim") -> pd.DataFrame:
    catalog_names = get_catalog_names(vpec_lim=vpec_lim, mode=mode)

    n_sources = []
    for key, name in catalog_names.items():
        catalog_path = config.RESULTS_CATALOGUE_DIR / "high-v_sources" / name
        df = pd.read_csv(catalog_path)
        n_sources.append(df.shape[0])

    data = {"stage": catalog_names.keys(), "n_sources": n_sources}
    df = pd.DataFrame(data=data)

    return df


def main() -> None:
    df = count()
    df.to_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "source_counts.csv", index=False)
    

if __name__ == "__main__":
    main()
