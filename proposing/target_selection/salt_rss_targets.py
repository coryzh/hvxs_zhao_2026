import config
import pandas as pd
import astropy.units as u
from log.loggers import VerboseLogger
from astropy.coordinates import SkyCoord


def select_targets(verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)
    logger.begin()

    in_file = config.RESULTS_CATALOGUE_DIR / "high-v_sources_old" / "combined_vpec_gt_200.csv"
    df = pd.read_csv(in_file)
    df["vpec_min_lolim"] = df["vpec_min_med"] - df["e_vpec_min"]

    logger.log(f"{df.shape[0]} rows loaded.\n")

    _filter_flux = df.f_x_err / df.f_x <= 0.3
    _filter_gmag = df.phot_g_mean_mag <= 16
    _filter_coord = (df.dec >= -70) & (df.dec <= 8) & (df.ra >= 30.0) & (df.ra <= 150)
    _filter_fxfg = df.fx_fg >= 1e-3
    _filter = _filter_gmag & _filter_coord & _filter_flux & _filter_fxfg

    df_filtered = df[_filter]
    logger.log(f"{sum(_filter)} rows selected.\n")

    target_coords = SkyCoord(df_filtered.ra.values, df_filtered.dec.values, frame="icrs", unit=(u.deg, u.deg))
    target_coords_hex_list = target_coords.to_string(style="hmsdms", sep=":", precision=2)
    ra_hex = [item.split(" ")[0] for item in target_coords_hex_list]
    dec_hex = [item.split(" ")[1] for item in target_coords_hex_list]
    df_filtered["RA"] = ra_hex
    df_filtered["Dec"] = dec_hex

    columns_selected = ["ID_x", "source_id", "RA", "Dec", "ra", "dec",
                        "sep_x_g", "pos_x_err",
                        "parallax", "parallax_error", "pmra", "pmra_error",
                        "pmdec", "pmdec_error",
                        "phot_g_mean_mag", "fx_fg", "vpec_min_lolim"]

    out_file = in_file.parent / "salt_2024-2" / "salt_targets_2024-2_astrometry.csv"
    df_filtered[columns_selected].to_csv(out_file)

    logger.log(f"Selected targets saved to {out_file}.\n")
    logger.end()


def main() -> None:
    select_targets(verbose=True)


if __name__ == "__main__":
    main()
