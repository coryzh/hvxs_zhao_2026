#!/bin/zsh

readonly PROJECT_ROOT=/Users/yuezhao/Desktop/local_repos/runaway_high_v_sources

readonly SURVEY_NAME=("csc" "xmm" "erass" "swift")

for name in "${SURVEY_NAME[@]}"; do
  repo_root="$PROJECT_ROOT/code_$name"
  script_dir="$repo_root/catalog/manipulate/add_columns_to_master_df.py"
  # Check if the subdirectory exists
  if [[ -d "$repo_root" ]]; then
    # Add the repository root to PYTHONPATH
    export PYTHONPATH="$repo_root:$PYTHONPATH"
    echo "Added '$repo_root' to PYTHONPATH."
    echo "Executing the python script ..."
    python "$script_dir"

  else
    echo "Warning: repository '$repo_root' does not exist."
  fi
done
