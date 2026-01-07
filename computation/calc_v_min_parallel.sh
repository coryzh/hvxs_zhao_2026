#!/bin/bash

FILE_IN="../../results/combined/catalogues/for_revision/gaia/sources_to_be_recomputed.csv"
OUT_FILE="../../results/combined/catalogues/for_revision/velocity/space_velocities_sources_to_be_recomputed.csv"

python3 calc_v_min_parallel.py --in_cat_path "$FILE_IN" --out_file "$OUT_FILE" --method "scipy" --survey_name "concat" --batch_size 200 \
    --n_workers 7 --verbose True
