import config
import pandas as pd
import logging
from log.log_config import configure_logging
from pathlib import Path

configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)

ids_to_ignore = [
    "1eRASS J062849.1-740938",
    "1eRASS J195751.0-764219",
    "1eRASS J065551.1-540917",
    "1eRASS J015650.0-261716",
    "1eRASS J212139.9-830618",
    "2SXPS J185204.3+725850",
    "2SXPS J185204.3+725850",
]


def _load_hvxs_catalogue() -> pd.DataFrame:
    file_path = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / 'ready_catalogues' / "hvxs.csv"
    )

    df = pd.read_csv(file_path)

    return df


def _select_gold_sample(df_hvxs: pd.DataFrame) -> pd.DataFrame:
    _filter_quality = (df_hvxs.quality == 7)
    _filter_ignore = ~df_hvxs["ID_x"].isin(ids_to_ignore)

    df_gold = df_hvxs[_filter_quality & _filter_ignore]
    logger.info(f"Selected {len(df_gold)} gold sample(s).")
    return df_gold


def _save_to_file(
        df: pd.DataFrame, out_file: Path
) -> None:
    out_file = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / 'ready_catalogues' / "gold.csv"
    )

    out_file.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_file, index=False)
    logger.info(f"Gold sample saved to: {out_file}")


def make_catalogue() -> None:
    df_hvxs = _load_hvxs_catalogue()
    df_gold = _select_gold_sample(df_hvxs)
    _save_to_file(df_gold, out_file=None)


if __name__ == "__main__":
    make_catalogue()
