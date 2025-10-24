#!/bin/zsh

# Define input and output dir and the path to the script
SURVEYS=("csc" "xmm" "erass" "swift")

for SURVEY in "${SURVEYS[@]}"; do
    FILE_IN="../../../results/$SURVEY/catalogues/nway_match/${SURVEY}_confident_point_sources.csv"

    # Run the command
    python3 rescale_xray_error_radius.py "$FILE_IN" --survey "$SURVEY" --verbose
done
