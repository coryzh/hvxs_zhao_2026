import pandas as pd
import config
import logging
import numpy as np
import time
import networkx as nx
from log.log_config import configure_logging
from pathlib import Path
from scipy.spatial import cKDTree
# from tqdm import tqdm


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
        },
        "xmm": {
            "iauname": "ID_x", "sc_ra": "ra_x", "sc_dec": "dec_x",
        },
        "swift": {
            "IAUName": "ID_x", "RA": "ra_x", "Decl": "dec_x",
        },
        "erass": {
            "IAUNAME": "ID_x", "RA": "ra_x", "DEC": "dec_x"
        }
    }

    cols_to_keep = ["ID_x", "ra_x", "dec_x", "pos_x_err"]
    for survey in config.SURVEY_NAMES_SHORT:
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
    logger.debug(f"Input DataFrame has {df.shape[0]} rows")
    n_tot = df.shape[0]

    # Prepare the arrays for cKDTree
    coords = df[["ra_x", "dec_x"]].to_numpy()
    pos_err = df["pos_x_err"].to_numpy()
    ids = df["ID_x"].to_numpy()
    # Build the KD Tree
    logger.debug(f"Building cKDTree for {n_tot} sources ...")
    if max_search_radius is None:
        max_search_radius = np.max(pos_err) * 2

    tree = cKDTree(coords)

    logger.debug("Querying candidate neighbours using KD-Tree...")
    # Make sure r is in the same units as coords (degrees)
    neighbors = tree.query_ball_tree(tree, r=max_search_radius / 3600)

    rows = []
    logger.debug(
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

    logger.debug(
        f"Found {n_overlap} overlapping sources.",
    )

    return df_sep


def check_overlap(df: pd.DataFrame) -> None:
    logger.debug(f"Input DataFrame has {df.shape[0]} rows")
    n_tot = df.shape[0]

    df_sep = pd.DataFrame(
        columns=["id_x_1", "id_x_2", "sep", "pos_x_err_1", "pos_x_err_2"]
    )

    logger.debug("Checking for overlapping sources...")
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
    logger.debug(
        f"Found {n_overlap} overlapping pairs.",
    )


def _get_pos_x_err_lookup_dict(df_sep: pd.DataFrame) -> dict:
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

    return pos_x_err_mapping


def summarize_overlap(df_sep: pd.DataFrame):
    logger.debug("Summarizing source overlapping source list ...")

    logger.debug("Building overlap graph ...")
    graph = nx.from_pandas_edgelist(
        df_all_overlap, source="id_x_1", target="id_x_2"
    )

    components = list(nx.connected_components(graph))
    logger.debug(f"Found {len(components)} connected components.")

    logger.debug(
        "Making a mapping dictionary for positional errors based on the input"
        " DataFrame..."
    )
    err_mapping = _get_pos_x_err_lookup_dict(df_sep)

    logger.debug(
        f"Mapping dictionary made for {len(err_mapping)} unique sources."
    )

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

    return groups_df


if __name__ == "__main__":
    logger = logging.getLogger(Path(__file__).stem)
    configure_logging(level=logging.DEBUG, app_name=Path(__file__).stem)

    logger.info("Loading and concatenating X-ray catalogues ...")

    df_all = _concatenate_catalogues()
    out_file_concat_xray = (
        config.RESULTS_CATALOGUE_DIR / "x_ray_catalogue_deduplication"
        / "xray_catalogue_all_for_autocorrelation.csv"
    )
    df_all.to_csv(out_file_concat_xray, index=False)

    start_time = time.time()
    logger.info("Starting auto-correlation to find overlapping sources...")

    df_all_overlap = check_overlap_ckdtree(df_all)
    df_all_overlap.to_csv(
        out_file_concat_xray.parent / "x_ray_catalogue_overlap.csv",
        index=False
    )

    logger.info(
        f"Overlap results saved to "
        f"{out_file_concat_xray.parent / 'x_ray_catalogue_overlap.csv'}"
    )

    logger.info("Summarizing overlap results ...")
    df_summary = summarize_overlap(df_all_overlap)
    df_summary.to_csv(
        out_file_concat_xray.parent / "x_ray_catalogue_overlap_summary.csv",
        index=False
    )
    time_elapsed = time.time() - start_time
    logger.info(
        f"Auto-correlation completed in "
        f"{time_elapsed:.2f} seconds."
    )
