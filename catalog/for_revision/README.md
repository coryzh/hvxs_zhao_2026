# Final X-ray Source Catalogue Pipeline

This document describes the workflow currently used in `catalog/for_revision` to build the cleaned, combined X-ray and Gaia cross-match catalogue.

All paths below are given relative to the repository root. The scripts in this folder write most intermediate products under:

- `results/combined/catalogues/for_revision/`

## Scope

This pipeline covers the steps from survey-level X-ray source lists to the cleaned combined X-ray/Gaia catalogue produced after NWAY matching and post-processing.

The final file produced by the steps documented here is:

- `results/combined/catalogues/for_revision/nway_matched_results/xray_catalogue_concatenated_further_cleaned.csv`

## Surveys covered

The current workflow expects the combined catalogue to include these survey labels in the later per-survey NWAY preparation and cleaning steps:

- `csc`
- `5xmm`
- `erass`
- `swift`

One naming detail to keep in mind:

- The initial X-ray concatenation step reads the XMM-family input from `results/xmm/.../xmm_confident_point_sources_poserr_rescaled.csv`.
- Later steps split the combined catalogue by source ID prefix, so 5XMM sources are written as `5xmm` products.

## Pipeline Summary

| Step | Tool used | Main output |
| --- | --- | --- |
| 1 | `auto_correlate_xray_catalogues.py` | `x_ray_catalogue_deduplication/xray_catalogue_deduplicated.csv` |
| 2 | TOPCAT or CDS Xmatch | `x_ray_catalogue_for_nway/gaia_neighbours_10arcsec.fits` |
| 3 | `split_prematched_gaia_catalogue.py` | `x_ray_catalogue_for_nway/<survey>_gaia_neighbours.csv` |
| 4 | `split_concatenated_xray_catalogue.py` | `x_ray_catalogue_for_nway/xray_catalogue_<survey>.csv` |
| 5 | `prepare_catalogues_for_nway.sh` and `prepare_catalogue_for_nway.py` | FITS versions of the per-survey X-ray and Gaia catalogues |
| 6 | NWAY and survey runner scripts | `nway_matched_results/<survey>_gaia_nway_match.fits` |
| 7 | `clean_nway_catalogue.sh` and `clean_nway_catalogue.py` | `nway_matched_results/<survey>_gaia_nway_match_clean.csv` |
| 8 | `construct_concat_xray_catalogue.py` | `nway_matched_results/xray_catalogue_concatenated.csv` |
| 9 | `deduplicate_concatenated_nway_matches.py` | `nway_matched_results/xray_catalogue_concatenated_deduplicated.csv` |
| 10 | `further_cleaning_concatenated_nway_catalogue.py` | `nway_matched_results/xray_catalogue_concatenated_further_cleaned.csv` |

## Step-by-Step Details

### 1. Auto-correlate the X-ray catalogues

**Script**

- `auto_correlate_xray_catalogues.py`

**What it does**

- Loads the confident point-source catalogues from the survey-level results directories.
- Renames survey-specific columns to a common schema.
- Concatenates all X-ray catalogues into one table.
- Finds overlapping X-ray detections using source positions and positional uncertainties.
- For each overlapping group, keeps the source with the smallest positional error.
- Removes the discarded duplicates from the concatenated catalogue.

**Input files**

- `results/csc/catalogues/nway_match/csc_confident_point_sources_poserr_rescaled.csv`
- `results/xmm/catalogues/nway_match/xmm_confident_point_sources_poserr_rescaled.csv`
- `results/swift/catalogues/nway_match/swift_confident_point_sources_poserr_rescaled.csv`
- `results/erass/catalogues/nway_match/erass_confident_point_sources_poserr_rescaled.csv`

**Output file**

- `results/combined/catalogues/for_revision/x_ray_catalogue_deduplication/xray_catalogue_deduplicated.csv`

**Notes**

- The script creates overlap summaries in memory but only writes the final deduplicated X-ray catalogue to disk.

### 2. Broad-match the deduplicated X-ray catalogue to Gaia

**Software**

- TOPCAT or CDS Xmatch

**What it does**

- Cross-matches the deduplicated X-ray catalogue from step 1 against Gaia.
- Keeps all Gaia neighbours within a deliberately broad search radius.
- Produces the candidate-neighbour table that is later split by survey and used for decrowding.

**Input file**

- `results/combined/catalogues/for_revision/x_ray_catalogue_deduplication/xray_catalogue_deduplicated.csv`

**Output file expected by downstream scripts**

- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/gaia_neighbours_10arcsec.fits`

**Notes**

- For current application, 10 arcsec is acceptable in practice for this broad match, even if a larger radius such as 15 arcsec is conceptually used.
- The downstream script in step 3 expects the file to be named `gaia_neighbours_10arcsec.fits` and to contain at least `ID_x`, `source_id`, `ra`, and `dec`.

### 3. Split the pre-matched Gaia neighbours by survey

**Script**

- `split_prematched_gaia_catalogue.py`

**What it does**

- Reads the broad Gaia-neighbour table from step 2.
- Uses the X-ray source ID prefix to assign each row to a survey.
- Writes one Gaia-neighbour CSV per survey.

**Input file**

- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/gaia_neighbours_10arcsec.fits`

**Output files**

- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/csc_gaia_neighbours.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xmm_gaia_neighbours.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/5xmm_gaia_neighbours.csv` if 5XMM IDs are present in the input catalogue
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/erass_gaia_neighbours.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/swift_gaia_neighbours.csv`

**Columns kept in the outputs**

- `source_id`
- `ra`
- `dec`

### 4. Split the deduplicated X-ray catalogue by survey

**Script**

- `split_concatenated_xray_catalogue.py`

**What it does**

- Reads the deduplicated X-ray catalogue from step 1.
- Detects which surveys are present from the X-ray source ID prefixes.
- Writes one X-ray CSV per survey for NWAY preparation.

**Input file**

- `results/combined/catalogues/for_revision/x_ray_catalogue_deduplication/xray_catalogue_deduplicated.csv`

**Output files**

- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_csc.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_5xmm.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_erass.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_swift.csv`

### 5. Convert the per-survey catalogues to NWAY-ready FITS files

**Scripts**

- `prepare_catalogues_for_nway.sh`
- `prepare_catalogue_for_nway.py`

**What they do**

- Convert each per-survey X-ray CSV and Gaia-neighbour CSV into FITS format.
- Remove duplicate IDs before writing.
- Keep only the columns required by NWAY.
- Add the `SKYAREA` FITS header keyword.
- Set the data extension name expected by the matching workflow.

**Input files**

- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_csc.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_5xmm.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_erass.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_swift.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/csc_gaia_neighbours.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/5xmm_gaia_neighbours.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/erass_gaia_neighbours.csv`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/swift_gaia_neighbours.csv`

**Output files**

- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_csc.fits`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_5xmm.fits`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_erass.fits`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/xray_catalogue_swift.fits`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/csc_gaia_neighbours.fits`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/5xmm_gaia_neighbours.fits`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/erass_gaia_neighbours.fits`
- `results/combined/catalogues/for_revision/x_ray_catalogue_for_nway/swift_gaia_neighbours.fits`

**Important column conventions**

- X-ray inputs are written with `ID_x`, `ra_x`, `dec_x`, and `pos_x_err`.
- Gaia inputs are written with `source_id`, `ra`, and `dec`.

### 6. Run NWAY for each survey

**Software**

- NWAY
- Survey-specific runner scripts referenced in your notes

**What it does**

- Cross-matches each per-survey X-ray FITS catalogue against the corresponding Gaia-neighbour FITS catalogue.
- Produces the NWAY result tables used by the cleaning scripts in step 7.

**Input files**

- The FITS files generated in step 5 for each survey.

**Output files expected by downstream scripts**

- `results/combined/catalogues/for_revision/nway_matched_results/csc_gaia_nway_match.fits`
- `results/combined/catalogues/for_revision/nway_matched_results/5xmm_gaia_nway_match.fits`
- `results/combined/catalogues/for_revision/nway_matched_results/erass_gaia_nway_match.fits`
- `results/combined/catalogues/for_revision/nway_matched_results/swift_gaia_nway_match.fits`

**Notes**

- Your notes indicate that NWAY should be run from the separate `nway/nway` location after activating the NWAY environment.
- I could not find the survey runner `.zsh` scripts inside the current workspace snapshot, so this README documents the output filenames expected by the scripts in this folder.

### 7. Clean the NWAY outputs

**Scripts**

- `clean_nway_catalogue.sh`
- `clean_nway_catalogue.py`

**What they do**

- Load each NWAY FITS result.
- Rename NWAY output columns to the shared combined-catalogue schema.
- Keep only confident matches.
- Filter on `p_any`, `p_single`, and `match_flag`.
- Write one cleaned CSV per survey.

**Input files**

- `results/combined/catalogues/for_revision/nway_matched_results/csc_gaia_nway_match.fits`
- `results/combined/catalogues/for_revision/nway_matched_results/5xmm_gaia_nway_match.fits`
- `results/combined/catalogues/for_revision/nway_matched_results/erass_gaia_nway_match.fits`
- `results/combined/catalogues/for_revision/nway_matched_results/swift_gaia_nway_match.fits`

**Output files**

- `results/combined/catalogues/for_revision/nway_matched_results/csc_gaia_nway_match_clean.csv`
- `results/combined/catalogues/for_revision/nway_matched_results/5xmm_gaia_nway_match_clean.csv`
- `results/combined/catalogues/for_revision/nway_matched_results/erass_gaia_nway_match_clean.csv`
- `results/combined/catalogues/for_revision/nway_matched_results/swift_gaia_nway_match_clean.csv`

**Default thresholds in the shell wrapper**

- `p_single >= 0.90`
- `p_any >= 0.90`
- `match_flag == 1`

### 8. Concatenate the cleaned per-survey NWAY catalogues

**Script**

- `construct_concat_xray_catalogue.py`

**What it does**

- Loads the cleaned per-survey NWAY catalogues from step 7.
- Keeps the core X-ray, Gaia, and NWAY probability columns.
- Concatenates them into one combined X-ray/Gaia match table.

**Input files**

- `results/combined/catalogues/for_revision/nway_matched_results/csc_gaia_nway_match_clean.csv`
- `results/combined/catalogues/for_revision/nway_matched_results/5xmm_gaia_nway_match_clean.csv`
- `results/combined/catalogues/for_revision/nway_matched_results/erass_gaia_nway_match_clean.csv`
- `results/combined/catalogues/for_revision/nway_matched_results/swift_gaia_nway_match_clean.csv`

**Output file**

- `results/combined/catalogues/for_revision/nway_matched_results/xray_catalogue_concatenated.csv`

### 9. Remove Gaia IDs matched to more than one X-ray source

**Script**

- `deduplicate_concatenated_nway_matches.py`

**What it does**

- Loads the concatenated catalogue from step 8.
- Computes the normalized separation `sep_x_g / pos_x_err`.
- Sorts matches so the closest normalized X-ray/Gaia pair is kept first.
- Drops duplicate Gaia source IDs, keeping the best match.
- Saves both the cleaned catalogue and the list of dropped duplicate matches.

**Input file**

- `results/combined/catalogues/for_revision/nway_matched_results/xray_catalogue_concatenated.csv`

**Output files**

- `results/combined/catalogues/for_revision/nway_matched_results/xray_catalogue_concatenated_deduplicated.csv`
- `results/combined/catalogues/for_revision/nway_matched_results/dropped_duplicated_matches.csv`

### 10. Final cleaning of the concatenated catalogue

**Scripts**

- `further_cleaning_concatenated_nway_catalogue.py`
- `remove_poorly_localised_xray_sources.py`
- `decrowding_concatenated_nway_catalogue.py`

**What they do**

- `further_cleaning_concatenated_nway_catalogue.py` orchestrates the final cleaning.
- `remove_poorly_localised_xray_sources.py` removes sources with large X-ray positional uncertainties.
- `decrowding_concatenated_nway_catalogue.py` removes sources that are crowded by nearby Gaia neighbours.

**Input files**

- Main catalogue input:
  `results/combined/catalogues/for_revision/nway_matched_results/xray_catalogue_concatenated_deduplicated.csv`
- Gaia-neighbour table reused for the decrowding calculation:
  `results/combined/catalogues/for_revision/gaia_neighbours/gaia_neighbours_10arcsec.csv`

**Important note**

- The decrowding helper reads `gaia_neighbours_10arcsec.csv` from `results/combined/catalogues/for_revision/gaia_neighbours/`.
- This is a different path and file format from the FITS file used in steps 2 and 3, so this CSV must already exist or be generated separately before running the final cleaning step.

**Cleaning logic**

- Remove rows with `pos_x_err >= 10.0` arcsec.
- Count Gaia neighbours with `angDist / pos_x_err <= 2.0`.
- Remove sources with `n_neighbours >= 1`.

**Output file**

- `results/combined/catalogues/for_revision/nway_matched_results/xray_catalogue_concatenated_further_cleaned.csv`

**Interpretation**

- After this step, the catalogue is intended to contain one Gaia counterpart per retained X-ray source, with "crowded" and poorly localized matches removed. Keep in mind that "crowded" is in the sense of Gaia sources, i.e., an X-ray source can still be in a crowded field with most of the sources not in Gaia.

### 11. Query Gaia archive

**Script**

- `query_gaia_archive.py`

**What it does**

This step is to query the extra Gaia columns from the Gaia Archive using TAP service in astroquery. The script can be used to query the Gaia DR3 archive with different set of columns and joining schemes. I haven't integrated `argparse` into the script, so currently, the user can only manually edit the query scheme within the code. The code will login to the Gaia archive, upload the catalogue from step 10 (if it's not in the user's space), query the database, and save the retrieved table to local.

- Query `astrometry`, `photometry`, `aen`, and `gspphot` from Gaia archive.

**Input file**

- N/A

**Output files**

- `results/combined/catalogues/for_revision/gaia/astrometry.csv`
- `results/combined/catalogues/for_revision/gaia/photometry.csv`
- `results/combined/catalogues/for_revision/gaia/aen.csv`
- `results/combined/catalogues/for_revision/gaia/gspphot.csv`


## Minimal Run Order

If all prerequisite files already exist, the scripted part of the workflow can be run in this order:

```bash
python auto_correlate_xray_catalogues.py
python split_prematched_gaia_catalogue.py
python split_concatenated_xray_catalogue.py
zsh prepare_catalogues_for_nway.sh
# run NWAY externally
zsh clean_nway_catalogue.sh
python construct_concat_xray_catalogue.py
python deduplicate_concatenated_nway_matches.py
python further_cleaning_concatenated_nway_catalogue.py
```

The manual steps are:

- generating `gaia_neighbours_10arcsec.fits`
- running the NWAY survey matches