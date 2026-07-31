import pandas as pd
import config
import logging
import numpy as np
import networkx as nx
from log.log_config import configure_logging
from pathlib import Path
from scipy.spatial import cKDTree

logger = logging.getLogger(Path(__file__).stem)
configure_logging(level=logging.INFO, app_name=Path(__file__).stem)


def _concatenate_catalogues() -> pd.DataFrame:
    """Concatenate multiple X-ray catalogues into a single DataFrame.
    This DataFrame will then be used for auto-correlation to identify
    duplicate sources across different catalogues.

    Returns
    -------
    pd.DataFrame
        A DataFrame containing the concatenated X-ray catalogues.
    """
    col_remapping_dict = {
        "csc": {
            "name": "ID_x", "ra_deg": "ra_x", "dec_deg": "dec_x",
            "flux_aper_b": "f_x", "flux_aper_b_sym_err": "f_x_err",
        },
        # # Comment out for 4XMM DR14
        # "xmm": {
        #     "iauname": "ID_x", "sc_ra": "ra_x", "sc_dec": "dec_x",
        #     "sc_ep_8_flux": "f_x", "sc_ep_8_flux_err": "f_x_err",
        # },
        "xmm": {
            "IAUNAME": "ID_x", "RA": "ra_x", "DEC": "dec_x",
            "EP_FLUX": "f_x", "EP_FLUX_ERR": "f_x_err",
        },
        "swift": {
            "IAUName": "ID_x", "RA": "ra_x", "Decl": "dec_x",
            "PowFlux_cen": "f_x", "PowFlux_cen_err": "f_x_err",
        },
        "erass": {
            "IAUNAME": "ID_x", "RA": "ra_x", "DEC": "dec_x",
            "ML_FLUX_1": "f_x", "ML_FLUX_ERR_1": "f_x_err",
        }
    }

    cols_to_keep = ["ID_x", "ra_x", "dec_x", "pos_x_err", "f_x", "f_x_err"]
    logger.info("Loading and concatenating X-ray catalogues ...")
    for survey in col_remapping_dict.keys():
        file_path = (
            config.ROOT_DIR / "results" / survey
            / "catalogues" / "nway_match" /
            f"{survey}_confident_point_sources_poserr_rescaled.csv"
        )
        df = pd.read_csv(file_path)
        logger.info(
            f"Confident point sources for {survey.upper()} loaded "
            f"from {file_path}, "
            f"including {df.shape[0]} rows"
        )

        logger.info(
            f"Renaming columns for {survey.upper()} ..."
            f"Mapping: {col_remapping_dict[survey]}"
        )
        df = df.rename(
            columns=col_remapping_dict[survey]
        )
        n_duplicates = df["ID_x"].duplicated().sum()
        if n_duplicates > 0:
            logger.warning(
                f"{n_duplicates} Duplicate IDs found in {survey.upper()} "
                "catalogue! This should not happen if the catalogue is raw. "
                "Please check."
            )

        logger.info(
            f"Concatenating {survey.upper()} catalogue into a master list..."
        )
        if survey == config.SURVEY_NAMES_SHORT[0]:
            df_all = df[cols_to_keep]
        else:
            df_all = pd.concat([df_all, df[cols_to_keep]], ignore_index=True)

    logger.info(
        f"All catalogues concatenated, total rows: {df_all.shape[0]}"
    )
    return df_all


def check_overlap_ckdtree(
        df: pd.DataFrame, max_search_radius: float = None
) -> None:
    logger.info(
        "Starting auto-correlation to find overlapping sources in the input "
        f"DataFrame. The input DataFrame has {df.shape[0]} rows."
    )
    n_tot = df.shape[0]

    # Prepare the arrays for cKDTree
    coords = df[["ra_x", "dec_x"]].to_numpy()
    pos_err = df["pos_x_err"].to_numpy()
    ids = df["ID_x"].to_numpy()

    # Build the KD Tree
    if max_search_radius is None:
        max_search_radius = np.max(pos_err) * 2

    logger.info(
        f"Building a KD-Tree for {n_tot} sources ..."
        "No max search radius provided, using 2x of the maximum positional "
        f"error = {max_search_radius:.2f} arcseconds."
    )

    tree = cKDTree(coords)

    logger.info("Querying candidate neighbours using KD-Tree...")
    # Make sure r is in the same units as coords (degrees)
    neighbors = tree.query_ball_tree(tree, r=max_search_radius / 3600)

    rows = []
    logger.info(
        "Checking candidate pairs and applying per-pair positional error sum"
        " filter ..."
    )

    for i, nbrs in enumerate(neighbors):
        # Keep only j>i to avoid double counting and self-matches
        # nbrs is the list of indices of neighbors for point i
        nbrs = [j for j in nbrs if j > i]
        # If no neighbours after the above filter, continue to the next source
        if not nbrs:
            continue

        # nbrs_arr is now a numpy array of integers
        nbrs_arr = np.array(nbrs, dtype=int)

        diffs = coords[nbrs_arr] - coords[i]  # shape (m, 2)

        # np.hypot computes sqrt(x^2 + y^2) for each row
        # here we convert coord differences from degrees to arcseconds
        seps = np.hypot(diffs[:, 0], diffs[:, 1]) * 3600  # shape (m,)
        err_sums = pos_err[i] + pos_err[nbrs_arr]  # shape (m,)

        mask = seps < err_sums
        if not mask.any():
            continue

        # Append rows that pass the filter
        for j_idx, sep in zip(nbrs_arr[mask], seps[mask]):
            row = {
                "id_x_1": ids[i],
                "id_x_2": ids[j_idx],
                "sep": sep,
                "pos_x_err_1": pos_err[i],
                "pos_x_err_2": pos_err[j_idx],
            }
            rows.append(row)
    df_sep = pd.DataFrame(rows)
    n_overlap = df_sep.shape[0]

    logger.info(
        f"Found {n_overlap} overlapping pairs, which are arranged in a "
        f"DataFrame with columns: {df_sep.columns.tolist()}. "
        "ID_x_1 or ID_x_2 could contain repeated IDs, because one ID_x_1 "
        "could be neighbour of multiple ID_x_2, and vice versa."
    )

    return df_sep


def check_overlap(df: pd.DataFrame) -> None:
    logger.info(f"Input DataFrame has {df.shape[0]} rows")
    n_tot = df.shape[0]

    df_sep = pd.DataFrame(
        columns=["id_x_1", "id_x_2", "sep", "pos_x_err_1", "pos_x_err_2"]
    )

    logger.info("Checking for overlapping sources...")
    for i in range(n_tot):
        for j in range(i + 1, n_tot):
            ra_x1 = df.loc[i, "ra_x"]
            dec_x1 = df.loc[i, "dec_x"]
            ra_x2 = df.loc[j, "ra_x"]
            dec_x2 = df.loc[j, "dec_x"]
            pos_x_err_1 = df.loc[i, "pos_x_err"]
            pos_x_err_2 = df.loc[j, "pos_x_err"]
            id_x_1 = df.loc[i, "ID_x"]
            id_x_2 = df.loc[j, "ID_x"]
            sep = np.sqrt(
                (ra_x1 - ra_x2) ** 2 +
                (dec_x1 - dec_x2) ** 2
            ) * 3600

            err_sum = df.loc[i, "pos_x_err"] + df.loc[j, "pos_x_err"]
            if sep < err_sum:
                row = pd.Series(
                    {
                        "id_x_1": id_x_1,
                        "id_x_2": id_x_2,
                        "sep": sep,
                        "pos_x_err_1": pos_x_err_1,
                        "pos_x_err_2": pos_x_err_2
                    }
                )

                df_sep = pd.concat(
                    [df_sep, row.to_frame().T], ignore_index=True
                )

    n_overlap = df_sep.shape[0]
    logger.info(
        f"Found {n_overlap} overlapping pairs.",
    )


def _get_pos_x_err_lookup_dict(df_sep: pd.DataFrame) -> dict:
    """Create a mapping from source ID to positional error.

    Parameters
    ----------
    df_sep : pd.DataFrame
        DataFrame containing overlapping source pairs with their positional
        errors. The DataFrame should have columns:
        'id_x_1', 'pos_x_err_1', 'id_x_2', 'pos_x_err_2', and 'sep'.

    Returns
    -------
    dict
        Mapping from source ID to positional error.
    """
    logger.info(
        "Making a mapping dictionary for positional errors based on the input"
        " DataFrame..."
    )
    df_pos_err = pd.concat([
        df_sep[["id_x_1", "pos_x_err_1"]].rename(
            columns={"id_x_1": "id_x", "pos_x_err_1": "pos_x_err"}
        ),
        df_sep[["id_x_2", "pos_x_err_2"]].rename(
            columns={"id_x_2": "id_x", "pos_x_err_2": "pos_x_err"}
        )
    ], ignore_index=True).drop_duplicates(subset="id_x", keep="first")

    pos_x_err_mapping = dict(
        zip(df_pos_err["id_x"], df_pos_err["pos_x_err"])
    )

    logger.info(
        f"Mapping dictionary made for {len(pos_x_err_mapping)} unique sources."
    )

    return pos_x_err_mapping


def summarize_overlap(df_sep: pd.DataFrame):
    """
    Summarize overlapping sources into groups based on connected components.
    Parameters
    ----------
    df_sep : pd.DataFrame
        DataFrame containing overlapping source pairs with their positional
        errors. The DataFrame should have columns:
        'id_x_1', 'pos_x_err_1', 'id_x_2', 'pos_x_err_2', and 'sep'.

    Returns
    -------
    pd.DataFrame
        DataFrame summarizing the overlapping sources.
        Each row corresponds to a group of overlapping sources, with columns:
        - 'group_id': Unique identifier for the group.
        - 'group_size': Number of sources in the group.
        - 'member_ids': Semicolon-separated list of X-ray IDs in the group.
        - 'member_pos_errs': Semicolon-separated list of positional errors.
        - 'kept_id': Source ID with the smallest positional error in the group.
        - 'kept_pos_err': Smallest positional error in the group.
    """
    logger.info("Summarizing source overlapping source list ...")

    logger.info("Building an overlap graph using networkx...")
    graph = nx.from_pandas_edgelist(
        df_all_overlap, source="id_x_1", target="id_x_2"
    )

    components = list(nx.connected_components(graph))
    logger.info(f"Found {len(components)} connected components.")

    err_mapping = _get_pos_x_err_lookup_dict(df_sep)

    rows = []
    for gid, comp in enumerate(components):
        members = sorted(comp)

        members_pos_err_str = [
            str(err_mapping.get(m)) for m in members
        ]

        members_pos_err_num = [
            err_mapping.get(m) for m in members
        ]

        min_err_idx = int(np.argmin(members_pos_err_num))
        min_pos_err = members_pos_err_num[min_err_idx]
        min_pos_err_id = members[min_err_idx]

        row = {
            "group_id": gid,
            "group_size": len(members),
            "member_ids": ";".join(members),
            "member_pos_errs": ";".join(members_pos_err_str),
            "kept_id": min_pos_err_id,
            "kept_pos_err": min_pos_err,
        }

        rows.append(row)

    groups_df = pd.DataFrame(
        rows, columns=[
            "group_id", "group_size", "member_ids", "member_pos_errs",
            "kept_id", "kept_pos_err"
        ]
    )

    logger.info(
        f"Summarization complete. Found {groups_df.shape[0]} groups of "
        "overlapping sources. The summary DataFrame has the following "
        f"columns: {groups_df.columns.tolist()}.\n"
        f"Explanation of columns:\n"
        f" group_id: Unique identifier for the group.\n"
        f" group_size: Number of sources in the group.\n"
        f" member_ids: Semicolon-separated list of X-ray IDs in the group.\n"
        f" member_pos_errs: Semicolon-separated list of positional errors.\n"
        f" kept_id: Source ID with the smallest positional error in the "
        f"group.\n"
        f" kept_pos_err: Smallest positional error in the group."
    )
    return groups_df


def get_list_of_discarded_sources(df: pd.DataFrame) -> pd.DataFrame:
    """Get a list of discarded sources from the summary DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        Summary DataFrame containing overlapping source groups. Could be
        loaded from files or generated from `summarize_overlap` function.
        It should have at least the following columns:
        - kept_id
        - member_ids (delimited by ';')

    Returns
    -------
    pd.DataFrame
        DataFrame containing discarded X-ray IDs.
    """

    logger.info("Getting a list of discarded X-ray sources ...")
    discarded_sources = []
    for _, row in df.iterrows():
        member_ids = row["member_ids"].split(";")
        kept_id = row["kept_id"]
        discarded_sources.extend(
            [mid for mid in member_ids if mid != kept_id]
        )

    df_discarded = pd.DataFrame(
        discarded_sources, columns=["discarded_id_x"]
    )

    logger.info(
        f"From the {df.shape[0]} groups of overlapping sources, "
        f"{df_discarded.shape[0]} sources were moved to the discarded list."
    )
    return df_discarded


def remove_discarded_sources_from_concatenated_catalogue(
        df_all: pd.DataFrame, df_discarded: pd.DataFrame
) -> pd.DataFrame:
    """Remove discarded sources from the concatenated catalogue.

    Parameters
    ----------
    df_all : pd.DataFrame
        The concatenated X-ray catalogue DataFrame.
    df_discarded : pd.DataFrame
        DataFrame containing discarded X-ray IDs with column 'discarded_id_x'.

    Returns
    -------
    pd.DataFrame
        The cleaned concatenated catalogue with discarded sources removed.
    """

    # set() is used to create a set of discarded IDs for faster lookup
    logger.info(
        "Removing discarded sources from concatenated catalogue ...\n"
        f"Loaded {df_discarded.shape[0]} discarded source IDs."
    )
    discarded_ids = set(df_discarded["discarded_id_x"].tolist())
    mask = ~df_all["ID_x"].isin(discarded_ids)
    df_cleaned = df_all[mask].reset_index(drop=True)

    logger.info(
        f"Removed {df_all.shape[0] - df_cleaned.shape[0]} discarded sources.\n"
        f"Cleaned catalogue now has {df_cleaned.shape[0]} sources."
    )

    return df_cleaned


def save_to_file(out_file_path: Path, df: pd.DataFrame) -> None:
    """Save DataFrame to CSV file.

    Parameters
    ----------
    out_file_path : Path
        Path to the output CSV file.
    df : pd.DataFrame
        DataFrame to be saved.
    """
    logger.info(
        f"Saving {df.shape[0]} rows to a .csv file ..."
    )
    df.to_csv(out_file_path, index=False)
    logger.info(f"DataFrame saved to {out_file_path}.")


if __name__ == "__main__":
    df_all = _concatenate_catalogues()

    df_all_overlap = check_overlap_ckdtree(df_all)

    df_summary = summarize_overlap(df_all_overlap)

    df_discarded = get_list_of_discarded_sources(df_summary)

    df_cleaned = remove_discarded_sources_from_concatenated_catalogue(
        df_all, df_discarded
    )

    # Save the cleaned concatenated catalogue
    out_file_cleaned_xray = (
        config.RESULTS_CATALOGUES_FOR_REVISION
        / "x_ray_catalogue_deduplication"
        / "xray_catalogue_deduplicated.csv"
    )

    save_to_file(out_file_cleaned_xray, df_cleaned)
