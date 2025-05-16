import config
import pandas as pd
from utils.process_string import wrap_sign
# import astropy.units as u
# from astropy.coordinates import SkyCoord


def make_prime_sample_source_table(df: pd.DataFrame) -> None:
    df = df.sort_values(by="ra_x", ascending=True)
    table_start = r"""
    \begin{table*}
    \caption{A sample table of curated runaway sources (see Sect \ref{sec:prime-sample}).}
    \centering
    \begin{tabular}{llccccc}
    \hline
    X-ray ID & Gaia DR3 & Separation  & \gaia\ G & $\distance$ & $\vpecmin$ & $\vpecgammamin$ \\
             &          & ($\sigma$)  &          & ($\kpc$) & $(\kms)$ & $(\kms)$ \\
    \hline
    """

    table_end = r"""
        \hline
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
        id_x_str = wrap_sign(id_x_str)
        d_str = (
            f"${row['dist_med']:.1f}"
            f"^{{+{row['E_dist']:.1f}}}"
            f"_{{-{row['e_dist']:.1f}}}$"
        )

        vpec_str = (
            rf"${row['vpec_min_med']:.1f}"
            rf"^{{+{row['E_vpec_min']:.1f}}}"
            rf"_{{-{row['e_vpec_min']:.1f}}}$"
        )

        # vspace_str = (
        #     rf"${row['vspace_min_med']:.1f}"
        #     rf"^{{+{row['E_vspace_min']:.1f}}}"
        #     rf"_{{-{row['e_vspace_min']:.1f}}}$ \\"
        # )

        vpec_gamma_str = (
            rf"${row['vpec_gamma_min_med']:.1f}"
            rf"^{{+{row['E_vpec_gamma_min']:.1f}}}"
            rf"_{{-{row['e_vpec_gamma_min']:.1f}}}$ \\"
        )

        row_str = " & ".join(
            [
                id_x_str, id_g_str, sep_str, gmag_str, d_str,
                vpec_str, vpec_gamma_str
            ]
        )
        row_list.append(row_str)

    rows_str = "\n".join(row_list)

    table_str = f"{table_start}{rows_str}{table_end}"

    out_file = (
        config.RESULTS_LATEX_TABLE_DIR
        / "gold_sample_table"
        / "gold_sample.txt"
    )

    if not out_file.parent.exists():
        out_file.parent.mkdir()

    with open(out_file, "w") as f1:
        f1.write(table_str)


def main() -> None:
    df = pd.read_csv(config.RESULTS_CATALOGUE_DIR
                     / "prime_sample"
                     / "gold_sample_150525_curated.csv")

    make_prime_sample_source_table(df)


if __name__ == "__main__":
    main()
