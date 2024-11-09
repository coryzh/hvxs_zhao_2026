import config
import pandas as pd
import astropy.units as u
from astropy.coordinates import SkyCoord


def make_prime_sample_source_table(df: pd.DataFrame) -> None:
    table_start = r"""
    \begin{table*}
    \centering
    \begin{tabular}{llcccc}
    \hline
    X-ray ID & Gaia DR3 & Separation  & \gaia\ G & d & $\vpecmin$ \\
             &          & ($\sigma$)  &          & ($\kpc$) & $(\kms)$ \\ 
    \hline
    """

    table_end = r"""
        \hline
        \caption{A sample table of sources with $\vpecmin\geq 1000\,\kms$.}
        \end{tabular}
        \label{tab:sample-table-hvxs}
    \end{table*}
        """
    row_list = []
    for i, row in df.iterrows():
        id_x_str = f"{row['ID_x']}"
        id_g_str = f"{row['source_id']}"
        sep_str = f"{row['sep_x_g'] / row['pos_x_err']:.1f} "
        gmag_str = f"{row['phot_g_mean_mag']:.2f} "
        d_str = f"${row['dist_med']:.1f}^{{+{row['E_dist']:.1f}}}_{{-{row['e_dist']:.1f}}}$"
        vpec_str = rf"${row['vpec_min_med']:.1f}^{{+{row['E_vpec_min']:.1f}}}_{{-{row['e_vpec_min']:.1f}}}$ \\"

        row_str = " & ".join([id_x_str, id_g_str, sep_str, gmag_str, d_str, vpec_str])
        row_list.append(row_str)

    rows_str = "\n".join(row_list)

    table_str = f"{table_start}{rows_str}{table_end}"

    out_file = config.RESULTS_LATEX_TABLE_DIR / "prime_sample_table" / "kept_simbad_types.txt"
    if not out_file.parent.exists():
        out_file.parent.mkdir()

    with open(out_file, "w") as f1:
        f1.write(table_str)


def main() -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR / "high-v_sources"
                     / "combined_vpec_lolim_gt_150_unique_stage_6_prime.csv")

    make_prime_sample_source_table(df)


if __name__ == "__main__":
    main()
