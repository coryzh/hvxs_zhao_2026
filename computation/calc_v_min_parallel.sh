#!/bin/bash

FILE_IN="../../results/combined/catalogues/for_revision/gaia/gaia_astrometry_60000_to_end.csv"
OUT_FILE="../../results/combined/catalogues/for_revision/gaia/space_velocities_60000_to_end.csv"

python3 calc_v_min_parallel.py --in_cat_path "$FILE_IN" --out_file "$OUT_FILE" --method "scipy" --survey_name "concat" --batch_size 200 \
    --n_workers 7 --verbose True