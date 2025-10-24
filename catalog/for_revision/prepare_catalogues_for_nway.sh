#!/bin/zsh

# Define input and output dir and the path to the script
SURVEYS=("csc" "xmm" "erass" "swift")

# Define sky areas for each survey
declare -A SKY_AREA=(
    ["csc"]=730.0
    ["xmm"]=1383.0   
    ["erass"]=20626.4
    ["swift"]=3790.0
)

for survey in "${SURVEYS[@]}"; do
    FILE_IN="../../../results/combined/catalogues/x_ray_catalogue_for_nway/xray_catalogue_${survey}.csv"

        # Run the command
        python3 prepare_catalogue_for_nway.py "$FILE_IN" \
            --id_col "ID_x" \
            --ra_col "ra_x" \
            --dec_col "dec_x" \
            --pos_err_col "pos_x_err" \
            --sky_area "${SKY_AREA[$survey]}" \
            --data_ext_name "$survey"
    done