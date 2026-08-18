import pandas as pd
import config
import json
import textwrap
import argparse


def _load_catalogue() -> pd.DataFrame:
    """
    Load the master X-ray source catalogue.
    """

    catalog_path = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "combined_xray_gaia_catalogue.csv"
    )

    df = pd.read_csv(catalog_path)
    print(
        f"{df.shape[0]} sources loaded from {catalog_path}."
    )
    return df


def load_query_string(scheme_key: str) -> str:
    """
    Load the query string from the configuration file.
    """

    with open("./query_string.json", "r", encoding="utf-8") as f:
        query_schemes: dict = json.load(f)

    if scheme_key not in query_schemes:
        raise ValueError(
            f"Scheme key '{scheme_key}' not found in query_string.json."
        )

    return "".join(query_schemes[scheme_key])


def select_targets(df: pd.DataFrame, query_scheme: str) -> pd.DataFrame:
    query_string = load_query_string(query_scheme)
    df = df.query(query_string)
    formatted_query_string = textwrap.fill(query_string, width=50)

    print(
        f"{df.shape[0]} sources selected for {query_scheme}.\n"
        f"The selection criteria were:\n{formatted_query_string}."
    )

    return df


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Select targets from the master catalogue based on a query scheme."
        )
    )

    parser.add_argument(
        "scheme",
        type=str,
        help="The key for the query scheme in query_string.json.",
    )
    parser.add_argument(
        "--out_path",
        type=str,
        default=None,
        help="Optional output path for the selected targets CSV file.",
    )
    args = parser.parse_args()

    df = _load_catalogue()
    selected_df = select_targets(df, args.scheme)

    if args.out_path is not None:
        selected_df.to_csv(args.out_path, index=False)
    else:
        print(
            "No output path provided. The selected targets will not be saved."
        )


if __name__ == "__main__":
    main()
