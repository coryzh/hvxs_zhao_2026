# import pandas as pd
# import config
# from astropy.coordinates import SkyCoord
# from constants import gal_cen
# from pathlib import Path
# import astropy.units as u


# def get_cartesian_coordinates(in_file: Path) -> None:
#     df = pd.read_csv(in_file)
#
#     coords = SkyCoord(df.ra.values * u.deg, df.dec.values * u.deg, distance=df.dist_med.values * u.kpc,
#                       frame="icrs")
#
#     coords_galcen = coords.transform_to(gal_cen)
#
#     x, y, z = coords_galcen.x.value, coords_galcen.y.value, coords_galcen.z.value
#
#     coords_galcen.representation_type = "cylindrical"
#     r_gc = coords_galcen.rho.value
#
#     coord_cols = ["x", "y", "z", "r_gc"]
#     coord_arrs = [x, y, z, r_gc]
#     for name, arr in zip(coord_cols, coord_arrs):
#         df[name] = arr
#
#     out_file = in_file.parent / f"{in_file.stem}.csv".replace("stage_7", "stage_8")
#
#     df.to_csv(out_file)
#
#
# def main() -> None:
#     file_hvx = config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_lolim_gt_150_unique_stage_7.csv"
#
#     file_all = config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "combined_vpec_med_gt_0_unique_stage_7.csv"
#
#     for file in [file_all, file_hvx]:
#         get_cartesian_coordinates(file)


if __name__ == "__main__":
    main()
