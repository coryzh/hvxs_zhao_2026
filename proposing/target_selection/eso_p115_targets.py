import pandas as pd
import config
from log.loggers import VerboseLogger


def select_targets(verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()

    in_file = config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_gt_200.csv"
    df = pd.read_csv(in_file)


if __name__ == "__main__":
    select_targets()
