import pandas as pd
import logging
import config
from log.log_config import configure_logging
from typing import Dict
from pathlib import Path
from tabulate import tabulate


logger = logging.getLogger(Path(__file__).stem)
configure_logging(level=logging.INFO, app_name=Path(__file__).stem)


def _detect_surveys(df: pd.DataFrame, id_x: str = 'ID_x') -> Dict[str, str]:
    """Detect unique surveys in the DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame containing the concatenated X-ray catalogue.

    Returns
    -------
    List[str]
        A list of unique survey names.
    """

    logger.info("Detecting surveys in the concatenated X-ray catalogue ...")
    unique_id_identifiers = (
        df[id_x].dropna().astype(str)
        .str.strip()  # remove leading/trailing whitespace
        .str.split(' ').str[0]
        .unique().tolist()  # split by space
    )

    surveys = {
        identifier: (config.SURVEY_ID_IDENTIFIERS[identifier])
        for identifier in unique_id_identifiers
    }

    logger.info(
        f"Found {len(unique_id_identifiers)} unique surveys,"
        f" including: {surveys}."
    )
    return surveys


def _tally_source_counts_per_survey(
        split_dfs: Dict[str, pd.DataFrame], df: pd
) -> None:
    """Log the number of sources per survey in the split dataframes.

    Parameters
    ----------
    split_dfs : Dict[str, pd.DataFrame]
        A dictionary mapping survey names to their respective dataframes.
    df : pd.DataFrame
        The original concatenated X-ray catalogue dataframe.
    """

    summed_counts = 0
    logger.info("Tallying source counts per survey ...")

    # Prepare data for tabulation
    table_data = []
    for survey_name, survey_df in split_dfs.items():
        table_data.append([survey_name, survey_df.shape[0]])

    # Create tabulated output
    table = tabulate(
        table_data,
        headers=["Survey", "Count"],
        tablefmt="grid"
    )

    logger.info(f"Source counts per survey:\n{table}")
    for survey_name, survey_df in split_dfs.items():
        summed_counts += survey_df.shape[0]

    if summed_counts != df.shape[0]:
        logger.warning(
            f"Total summed source counts ({summed_counts}) "
            "do not match the total number of sources in original "
            "concatenated catalogue!"
        )

    else:
        logger.info(
            f"Total summed source counts ({summed_counts}) match "
            f"the total number of sources ({df.shape[0]}) in original "
            "concatenated catalogue."
        )


def save_split_catalogues(
        split_dfs: Dict[str, pd.DataFrame], output_dir: Path
) -> None:
    """Save the split catalogues to CSV files.

    Parameters
    ----------
    split_dfs : Dict[str, pd.DataFrame]
        Split dataframes per survey.

    output_dir : Path
        The directory where the split catalogues will be saved.
    """

    logger.info(f"Saving split catalogues to directory: {output_dir} ...")
    output_dir.mkdir(
        parents=True, exist_ok=True
    )

    for survey_name, survey_df in split_dfs.items():
        output_file = output_dir / f"xray_catalogue_{survey_name}.csv"
        survey_df.to_csv(output_file, index=False)
        logger.info(
            f"Saved {survey_name.upper()} catalogue to {output_file}."
        )


def split_catalogue(
        df: pd.DataFrame, id_x: str = 'ID_x'
) -> Dict[str, pd.DataFrame]:
    """Split the concatenated X-ray catalogue into
    individual dataframes per survey.

    Parameters
    ----------
    df : pd.DataFrame
        The concatenated X-ray catalogue.

    id_x : str, optional
        The name of the column containing the X-ray source IDs,
        default is 'ID_x'.

    Returns
    -------
    Dict[str, pd.DataFrame]
        A dictionary mapping survey names to their respective dataframes.
    """

    logger.info(
        "Begin to split the concatenated X-ray catalogue:\n"
        f"{df.shape[0]} rows and {df.shape[1]} columns."
    )

    split_dfs = {}
    for identifier, survey_name in surveys.items():
        split_dfs[survey_name] = df[df[id_x].str.startswith(identifier)]

    return split_dfs


if __name__ == "__main__":
    in_file = (
        config.RESULTS_CATALOGUE_DIR / "x_ray_catalogue_deduplication"
        / "xray_catalogue_deduplicated.csv"
    )

    out_dir = (
        config.RESULTS_CATALOGUE_DIR / "x_ray_catalogue_for_nway"
    )
    df = pd.read_csv(in_file)

    surveys = _detect_surveys(df)

    split_dfs = split_catalogue(df)

    _tally_source_counts_per_survey(split_dfs, df)

    save_split_catalogues(split_dfs, output_dir=out_dir)

    _ = split_catalogue(df)
