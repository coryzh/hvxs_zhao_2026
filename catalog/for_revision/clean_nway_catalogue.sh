#!/bin/zsh


# Define input and output dir and the path to the script
SURVEYS=("csc" "xmm" "erass" "swift")

ROOT_DIR="../../../results/combined/catalogues/for_revision/nway_matched_results/"

for survey in "${SURVEYS[@]}"; do
    FILE_IN="${ROOT_DIR}/${survey}_gaia_nway_match.fits"
    FILE_OUT="${FILE_IN%.*}_clean.csv"

    # Run the command
    python3 clean_nway_catalogue.py "$FILE_IN" \
        "$survey" \
        "$FILE_OUT"
done
