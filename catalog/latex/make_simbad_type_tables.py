import pandas as pd
import config
import data_schema as ds
from pathlib import Path


def remained_simbad_type_table(df: pd.DataFrame) -> None:
    table_start = r"""
    \begin{table*}
    \centering
    \begin{tabular}{ll|ll|ll}
    \hline
    Type & Counts & Type & Counts & Type & Counts \\
    \hline
    """

    table_end = r"""
    \hline
    \end{tabular}
\end{table*}
    """

    simbad_type_counts = df[ds.SimbadSchema.SIMBAD_MAIN_TYPE].value_counts()
    type_names, type_counts = simbad_type_counts.index, simbad_type_counts.values
    escaped_type_names = [item.replace("_", r"\_") for item in type_names]
    row_num = simbad_type_counts.shape[0] // 3
    row_str_list = []

    for row_index in range(row_num):
        # idx = 3 * row_index
        row_str_single = (fr"{escaped_type_names[row_index]} & {type_counts[row_index]}"
                          fr" & {escaped_type_names[row_index+8]} & {type_counts[row_index+8]}" 
                          fr" & {escaped_type_names[row_index+16]} & {type_counts[row_index+16]} \\")

        row_str_list.append(row_str_single)

    row_str = "\n".join(row_str_list)

    table_str = f"{table_start}{row_str}{table_end}"

    out_file = config.RESULTS_LATEX_TABLE_DIR / "kept_simbad_types" / "kept_simbad_types.txt"
    with open(out_file, "w") as f1:
        f1.write(table_str.strip())

    # return table_str


def main() -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources" /
                     "combined_vpec_lolim_gt_150_unique_w_simbad_high_ratio_simbad_cleaned_cleaned_cl_members.csv")
    remained_simbad_type_table(df)


if __name__ == "__main__":
    main()
