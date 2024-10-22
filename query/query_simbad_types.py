from astroquery.simbad import Simbad
from astropy.coordinates import SkyCoord
from tqdm import tqdm
from typing import List
import pandas as pd
import config
import numpy as np
import data_schema as ds
import astropy.units as u
import warnings

# unwanted_name_patterns = ["Cl*"]


custom_simbad = Simbad()
custom_simbad.add_votable_fields('ids', 'otypes', "otype", "otype(opt)", "typed_id", "membership")

# Select only a few columns to reduce the file size.
selected_columns = [
    "DETUID",
    "source_id",
    ds.SimbadSchema.SIMBAD_ID,
    ds.SimbadSchema.SIMBAD_IDS,
    ds.SimbadSchema.SIMBAD_OTYPE,
    ds.SimbadSchema.SIMBAD_OTYPES,
    ds.SimbadSchema.SIMBAD_OTYPE_OPT,
    "SCRIPT_NUMBER_ID"
]


def get_simbad_types_by_name(df: pd.DataFrame, block_size: int = 2000) -> pd.DataFrame:
    """
    Query Simbad for the types of the sources in the DataFrame. The input DataFrame must contain a column of Gaia
    source_id (could be some other names).

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing a column of Gaia source_id.

    block_size : int
        The number of sources to query Simbad at a time. Default is 2000.

    Returns
    -------
    df : pd.DataFrame
        Input DataFrame with an additional column "SIMBAD_OTYPE" containing the types of the sources.
    """

    df_ids = df[["DETUID", "source_id"]]
    n_block = df_ids.shape[0] // block_size
    id_blocks: List[pd.DataFrame] = np.array_split(df_ids, n_block)

    # Define an empty DataFrame to store the results
    df_simbad = pd.DataFrame(columns=selected_columns)

    for id_block in tqdm(id_blocks):
        # Query Simbad for the types of the sources
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            gaia_ids = ("Gaia DR3 " + id_block["source_id"]).to_list()
            job_block = custom_simbad.query_objects(gaia_ids)
            df_simbad_block = job_block.to_pandas()
            df_simbad_block = df_simbad_block[selected_columns[2:]]
            id_block.reset_index(drop=True, inplace=True)
            df_block = pd.concat([id_block, df_simbad_block], axis=1)
            df_simbad = pd.concat([df_block, df_simbad], axis=0, ignore_index=True)

    return df_simbad


def get_simbad_types_by_coordinates(df: pd.DataFrame, block_size: int = 2000) -> pd.DataFrame:
    """
    Query Simbad for the types of the sources in the DataFrame. The input DataFrame must contain a column of Gaia
    source_id (could be some other names).

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame; it must contain columns of equatorial coordinates, i.e., ra and dec.

    block_size : int
        The number of sources to query Simbad at a time. Default is 2000.

    Returns
    -------
    df : pd.DataFrame
        Input DataFrame with an additional column "SIMBAD_OTYPE" containing the types of the sources.
    """

    df_ids_and_coords = df[["DETUID", "source_id", "ra", "dec"]]
    n_block = df_ids_and_coords.shape[0] // block_size
    df_blocks: List[pd.DataFrame] = np.array_split(df_ids_and_coords, n_block)

    # Define an empty DataFrame to store the results
    df_simbad = pd.DataFrame(columns=selected_columns)

    for block in tqdm(df_blocks):
        # Query Simbad for the types of the sources
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            coords = SkyCoord(block["ra"].values, block["dec"].values, frame="icrs", unit=(u.deg, u.deg))
            job_block = custom_simbad.query_region(coords, radius=1.0 * u.arcsec)
            df_simbad_block = job_block.to_pandas()
            df_simbad_block = df_simbad_block[selected_columns[2:]]
            # SCRIPT_NUMBER_ID is the number (from 1) of the corresponding query array position, i.e., the nth item
            # in the input position array. SCRIPT_NUMBER_ID - 1 converts the number to the index of the DataFrame.
            idx = (df_simbad_block.SCRIPT_NUMBER_ID - 1).to_list()
            block_has_simbad_id = block.iloc[idx]
            block_has_simbad_id.reset_index(drop=True, inplace=True)
            df_block = pd.concat([block_has_simbad_id, df_simbad_block], axis=1)
            df_simbad = pd.concat([df_block, df_simbad], axis=0, ignore_index=True)

    return df_simbad


def main() -> None:
    print(f"Loading the vpec catalogue ... \n")
    # df = loader.load_vpec_catalogue()
    df = pd.read_csv(config.DATA_DIR_INTERMEDIATE / "erass_gaia_unknown_otype.csv")
    print(f"Loaded the vpec catalogue. The catalogue contains {len(df.index)} rows. \n")

    print(f"Querying Simbad for the types of the sources ... \n")
    # df = get_simbad_types_by_name(df, block_size=2000)
    df_by_coords = get_simbad_types_by_coordinates(df, block_size=2000)
    print(f"Saving the types of the sources to file ... \n")
    # out_file = config.ERASS_GAIA_W_SIMBAD_TYPES
    out_file = config.DATA_DIR_INTERMEDIATE / "erass_gaia_simbad_types_pos_match.csv"
    df_by_coords.to_csv(out_file, index=False)

    print(f"Types of the sources saved to {out_file}\n")

    print(f"Done!")


if __name__ == "__main__":
    main()
