import pandas as pd
import logging
import data_schema as ds
from log.log_config import configure_logging
from pathlib import Path


configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


def clean(
        df: pd.DataFrame, pos_x_err_thresh: float = 10.0, out_file: Path = None
) -> pd.DataFrame:
    logger.info(f"Catalogue loaded: {df.shape[0]} sources.")

    _filter = df[ds.CombinedCatalogueSchema.pos_x_err] < pos_x_err_thresh

    df = df[_filter].reset_index(drop=True)
    n_removed = (~_filter).sum()
    logger.info(
        f"Catalogue cleaned: removed {n_removed} sources with "
        f"pos_x_err >= {pos_x_err_thresh} arcsec."
        f" Remaining sources: {df.shape[0]}."
    )

    if out_file:
        df.to_csv(out_file, index=False)

    return df
