import pandas as pd
import config


def add_symmetric_flux_error_for_csc() -> pd.DataFrame:
    """Add symmetric flux error column for CSC catalogue.

    Returns
    -------
    pd.DataFrame
        DataFrame with added symmetric flux error column.
    """
    file_path = (
        config.ROOT_DIR / "results" / "csc" / "catalogues" / "nway_match"
        / "csc_confident_point_sources_poserr_rescaled.csv"
    )

    df_csc = pd.read_csv(file_path)

    # Calculate symmetric flux error
    f_x_lo_err = df_csc.eval("flux_aper_b - flux_aper_lolim_b")
    f_x_hi_err = df_csc.eval("flux_aper_hilim_b - flux_aper_b")
    df_csc["flux_aper_b_sym_err"] = (f_x_lo_err + f_x_hi_err) / 2

    return df_csc


if __name__ == "__main__":
    df_csc_updated = add_symmetric_flux_error_for_csc()
    output_path = (
        config.ROOT_DIR / "results" / "csc" / "catalogues" / "nway_match"
        / "csc_confident_point_sources_poserr_rescaled.csv"
    )
    df_csc_updated.to_csv(output_path, index=False)
