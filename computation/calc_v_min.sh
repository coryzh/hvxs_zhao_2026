#!/bin/bash

FILE_IN="../../results/combined/catalogues/gaia_astrometry_catalogues/gaia_astrometry_stars_only.csv"
OUT_FILE="../../results/combined/catalogues/gaia_astrometry_catalogues/space_velocities.csv"

python3 calc_v_min.py --in_cat_path "$FILE_IN" --out_file "$OUT_FILE" --method "scipy" --survey_name "concat" --batch_size 200