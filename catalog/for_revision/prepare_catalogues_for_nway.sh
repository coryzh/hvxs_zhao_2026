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
    FILE_XRAY_IN="../../../results/combined/catalogues/x_ray_catalogue_for_nway/xray_catalogue_${survey}.csv"
    FILE_GAIA_IN="../../../results/combined/catalogues/x_ray_catalogue_for_nway/${survey}_gaia_neighbours.csv"
        # Run the command
        python3 prepare_catalogue_for_nway.py "$FILE_XRAY_IN" \
            --id_col "ID_x" \
            --ra_col "ra_x" \
            --dec_col "dec_x" \
            --pos_err_col "pos_x_err" \
            --sky_area "${SKY_AREA[$survey]}" \
            --data_ext_name "$survey"

        python3 prepare_catalogue_for_nway.py "$FILE_GAIA_IN" \
            --id_col "source_id" \
            --ra_col "ra" \
            --dec_col "dec" \
            --sky_area 41253.0 \
            --data_ext_name "Gaia"
    done