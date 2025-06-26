import config
import pandas as pd


def main() -> None:
    df_c = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR / "control_sample"
        / "control_sample_stage_10.csv"
    )

    df_c_neighbours = pd.read_csv(
        config.RESULTS_CATALOGUE_DIR / "control_sample"
        / "control_sample_stage_10_gaia_neighbours_15arcsec.csv"
    )

    # Only keeps neighbours within 2 sigma of the X-ray positions
    _filter_2sigma_neigbours = (
        df_c_neighbours["ang_dist"] / df_c_neighbours["pos_x_err"] <= 2
    )
    df_c_neighbours_filtered = df_c_neighbours[_filter_2sigma_neigbours]

    # And do the same for the control sample:
    _filter_control_2sigma = (
        df_c["sep_x_g"] / df_c["pos_x_err"] <= 2
    )
    df_c_filtered = df_c[_filter_control_2sigma]

    # Count the number of neighbours within 2sigma:
    df_c_neighbour_counts = df_c_neighbours_filtered.value_counts(
        subset=["ID_x"]
    ).reset_index()

    # Now, left join with the original control sample
    df_merged = pd.merge(
        df_c_filtered, df_c_neighbour_counts, on="ID_x", how="left"
    )

    df_merged = df_merged.rename(columns={'count': 'n_neighbours'})

    # Finally, remove rows that have more than 1 Gaia sources within 2 sigma:
    _filter_merged = df_merged["n_neighbours"] > 1
    # n_sources = df_merged[_filter_merged].shape[0]
    df_merged_filtered = df_merged[~_filter_merged]
    print(f"{df_merged_filtered.shape[0]} sources kept.")
    df_merged_filtered.to_csv(
        config.RESULTS_CATALOGUE_DIR / "control_sample"
        / "control_sample_1cpt_2sigma.csv", index=False
    )


if __name__ == "__main__":
    main()
