import config
import pandas as pd
from astropy.coordinates import SkyCoord
from log.loggers import VerboseLogger
from tqdm import tqdm
from pathlib import Path
from astropy.io import fits
from astropy.table import Table
import numpy as np


def load_cluster_catalogue(verbose: bool = False) -> pd.DataFrame:
    logger = VerboseLogger(verbose=verbose)

    logger.begin()
    in_file = config.DATA_DIR_MISC / "hunt+23_cluster_catalogue.csv"
    df = pd.read_csv(in_file)
    logger.log(f"Cluster catalogue loaded from {in_file}\n{df.shape[0]} rows loaded.\n")

    return df


def cross_match_ids(in_file_csv: Path, verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)

    logger.begin()
    df = pd.read_csv(in_file_csv)
    logger.log(f"{df.shape[0]} sources loaded.\n")

    logger.log(f"Loading the cluster member catalogue ...")
    hdul_members = fits.open(config.DATA_DIR_MISC / "hunt+23_members_of_clusters.fits")
    data = Table(hdul_members[1].data)
    df_members = data.to_pandas()
    logger.log(f"{df_members.shape[0]} members loaded.\n")

    df_members.rename(columns={"GaiaDR3": "source_id", "Name": "cluster_name", "Prob": "cl_member_prob"}, inplace=True)

    logger.log(f"Drop duplicated Gaia IDs (Gaia IDs that have been matched to multiple clusters).\n")
    df_members = df_members.sort_values(by="cl_member_prob", ascending=False).drop_duplicates(subset="source_id",
                                                                                              keep="first")

    df_merged = pd.merge(df, df_members[["cluster_name", "source_id", "cl_member_prob"]], on="source_id", how="left")
    logger.log(f"{df_merged['cluster_name'].notna().sum()} sources are likely cluster members.\n")

    out_file = in_file_csv.parent / f"{in_file_csv.stem}_w_cl_info.csv"
    df_merged.to_csv(out_file, index=False)
    logger.log(f"Catalogue with cluster membership information saved to {out_file}.\n")

    logger.end()


def cross_match_astrometry(in_file_csv: Path, verbose: bool = False, radius_type: str = "rt") -> None:
    logger = VerboseLogger(verbose=verbose)

    logger.begin()
    df = pd.read_csv(in_file_csv)
    logger.log(f"Source catalogue loaded: {df.shape[0]} rows loaded. \n")

    df_cl = load_cluster_catalogue(verbose=verbose)
    coords_cl = SkyCoord(df_cl["RA_ICRS"], df_cl["DE_ICRS"], unit="deg")
    cl_radius = df_cl[radius_type]
    cl_dist_lo = df_cl["dist16"] / 1e3
    cl_dist_hi = df_cl["dist84"] / 1e3
    cl_pmra = df_cl["pmRA"]
    cl_pmdec = df_cl["pmDE"]
    cl_pmra_std = df_cl["e_pmRA"]
    cl_pmdec_std = df_cl["e_pmDE"]

    df["likely_in_cluster"] = False
    df["matched_clusters"] = "NA"
    df["min_sep_from_matched_clusters"] = -99.99
    logger.log(f"Cross-matching starts\n")
    for i, row in tqdm(df.iterrows()):
        coord_src = SkyCoord(row["ra"], row["dec"], frame="icrs", unit="deg")
        # dist_src = row["dist_med"]
        # e_dist_src = row["e_dist"]
        # E_dist_src = row["E_dist"]
        pmra_src = row["pmra"]
        pmdec_src = row["pmdec"]
        sep = coord_src.separation(coords_cl).deg
        cond_pos = (sep <= cl_radius)
        cond_pmra = (pmra_src >= cl_pmra - 5 * cl_pmra_std) & (pmra_src <= cl_pmra + 5 * cl_pmra_std)
        cond_pmdec = (pmdec_src >= cl_pmdec - 5 * cl_pmdec_std) & (pmdec_src <= cl_pmdec + 5 * cl_pmdec_std)
        cond = cond_pos & cond_pmra & cond_pmdec

        if any(cond):
            matched_df = df_cl[cond]
            df.loc[i, "likely_in_cluster"] = True
            matched_cluster_names = ",".join(matched_df["Name"].str.strip())
            df.loc[i, "matched_clusters"] = matched_cluster_names
            sep_from_matched_clusters = sep[np.where(sep <= cl_radius)[0]]
            df.loc[i, "min_sep_from_matched_clusters"] = sep_from_matched_clusters.min()

    logger.log(f"Finished. {df['likely_in_cluster'].sum()} sources found to be in clusters.\n")
    out_file = in_file_csv.parent / f"{in_file_csv.stem}_w_cl_info.csv"
    logger.log(f"Saving updated catalogue to {out_file}")
    df.to_csv(out_file, index=False)
    logger.log(f"File saved to {out_file}.\n")
    logger.end()


def main() -> None:
    in_file = (config.RESULTS_CATALOGUE_DIR / "high-v_sources"
               / "combined_vpec_lolim_gt_150_unique_w_simbad_high_ratio_simbad_cleaned.csv")

    # cross_match_astrometry(in_file_csv=in_file, verbose=True, radius_type="r50")
    cross_match_ids(in_file, verbose=True)


if __name__ == "__main__":
    main()
