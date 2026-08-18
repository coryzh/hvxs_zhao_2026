from astroquery.gaia import Gaia
from pathlib import Path
from log.log_config import configure_logging
import logging
import keyring
import getpass
import config


configure_logging(level=logging.INFO, app_name=Path(__file__).stem)
logger = logging.getLogger(Path(__file__).stem)


def _get_user_table_name(username: str, table_name: str) -> str:
    logger.info(
        f"Constructing user table name for user '{username}' "
        f"and table '{table_name}' ..."
    )
    return f"user_{username}.{table_name}"


def _render_query_str(
        username: str, table_name: str, scheme="astrometry"
) -> str:
    user_table_name = _get_user_table_name(username, table_name)

    if scheme == "astrometry":
        query = (
            "SELECT u.ID_x, u.source_id, dr3.ra, dr3.dec, \n"
            "dr3.parallax, dr3.parallax_error, \n"
            "dr3.pmra, dr3.pmra_error, dr3.pmdec, dr3.pmdec_error, \n"
            "dr3.nu_eff_used_in_astrometry, \n"
            "dr3.pseudocolour, dr3.ecl_lat, dr3.astrometric_params_solved, \n"
            "b.r_med_geo/1000 AS r_med_geo, \n"
            "b.r_lo_geo/1000 AS r_lo_geo, \n"
            "b.r_hi_geo/1000 AS r_hi_geo, \n"
            "b.r_med_photogeo/1000 AS r_med_photogeo, \n"
            "b.r_lo_photogeo/1000 AS r_lo_photogeo, \n"
            "b.r_hi_photogeo/1000 AS r_hi_photogeo \n"
            f"FROM {user_table_name} AS u \n"
            # Require a matching Gaia DR3 row that meets filters (INNER JOIN)
            "JOIN gaiadr3.gaia_source AS dr3 \n"
            "  ON u.source_id = dr3.source_id \n"
            # "  AND dr3.astrometric_params_solved IN (31, 63, 95) \n"
            # "  AND dr3.classprob_dsc_combmod_star >= 0.9 \n"
            # Distance may be missing; keep rows even if b is NULL (LEFT JOIN)
            "LEFT JOIN external.gaiaedr3_distance AS b \n"
            "  ON u.source_id = b.source_id \n"
        )
    elif scheme == "photometry":
        query = (
            "SELECT u.ID_x, u.source_id, dr3.phot_g_mean_mag, \n"
            "dr3.phot_bp_mean_mag, dr3.phot_rp_mean_mag, \n"
            "dr3.bp_rp \n"
            f"FROM {user_table_name} AS u \n"
            "JOIN gaiadr3.gaia_source AS dr3 \n"
            "  ON u.source_id = dr3.source_id \n"
            # "  AND dr3.astrometric_params_solved IN (31, 63, 95) \n"
            # "  AND dr3.classprob_dsc_combmod_star >= 0.9 \n"
        )

    elif scheme == "aen":
        query = (
            "SELECT u.ID_x, u.source_id, dr3.astrometric_excess_noise, \n"
            "dr3.astrometric_excess_noise_sig, dr3.ruwe, "
            "dr3.non_single_star\n"
            f"FROM {user_table_name} AS u \n"
            "JOIN gaiadr3.gaia_source AS dr3 \n"
            "  ON u.source_id = dr3.source_id \n"
            # "  AND dr3.astrometric_params_solved IN (31, 63, 95) \n"
            # "  AND dr3.classprob_dsc_combmod_star >= 0.9 \n"
        )

    elif scheme == "gspphot":
        query = (
            "SELECT u.ID_x, u.source_id, dr3.mh_gspphot, \n"
            "dr3.mh_gspphot_lower, dr3.mh_gspphot_upper, \n"
            "dr3.ag_gspphot, dr3.ebpminrp_gspphot, \n"
            "dr3.teff_gspphot, dr3.teff_gspphot_lower, \n"
            "dr3.teff_gspphot_upper, dr3.logg_gspphot, \n"
            "dr3.logg_gspphot_lower, dr3.logg_gspphot_upper, \n"
            "dr3.azero_gspphot, dr3.azero_gspphot_lower, \n"
            "dr3.azero_gspphot_upper, \n"
            "dr3.libname_gspphot, apparams.mg_gspphot, \n"
            "apparams.mg_gspphot_lower, apparams.mg_gspphot_upper \n"
            f"FROM {user_table_name} AS u \n"
            "JOIN gaiadr3.gaia_source AS dr3 \n"
            "  ON u.source_id = dr3.source_id \n"
            # "  AND dr3.astrometric_params_solved IN (31, 63, 95) \n"
            # "  AND dr3.classprob_dsc_combmod_star >= 0.9 \n"
            "LEFT JOIN gaiadr3.astrophysical_parameters AS apparams \n"
            "  ON u.source_id = apparams.source_id \n"
        )
    elif scheme == "lsst_non_agn_matches":
        query = (
            "SELECT u.ID_x, u.source_id, dr3.ra, dr3.dec, \n"
            "dr3.parallax, dr3.parallax_error, \n"
            "dr3.pmra, dr3.pmra_error, dr3.pmdec, dr3.pmdec_error, \n"
            "dr3.nu_eff_used_in_astrometry, \n"
            "dr3.pseudocolour, dr3.ecl_lat, dr3.astrometric_params_solved, \n"
            "b.r_med_geo/1000 AS r_med_geo, \n"
            "b.r_lo_geo/1000 AS r_lo_geo, \n"
            "b.r_hi_geo/1000 AS r_hi_geo, \n"
            "b.r_med_photogeo/1000 AS r_med_photogeo, \n"
            "b.r_lo_photogeo/1000 AS r_lo_photogeo, \n"
            "b.r_hi_photogeo/1000 AS r_hi_photogeo \n"
            f"FROM {user_table_name} AS u \n"
            # Require a matching Gaia DR3 row that meets filters (INNER JOIN)
            "JOIN gaiadr3.gaia_source AS dr3 \n"
            "  ON u.source_id = dr3.source_id \n"
            "  AND dr3.classprob_dsc_combmod_star >= 0.9 \n"
            # Distance may be missing; keep rows even if b is NULL (LEFT JOIN)
            "LEFT JOIN external.gaiaedr3_distance AS b \n"
            "  ON u.source_id = b.source_id \n"
        )

    elif scheme == "good_astrometry":
        query = (
            "SELECT u.ID_x, u.source_id, dr3.ra, dr3.dec, \n"
            "dr3.parallax, dr3.parallax_error, \n"
            "dr3.pmra, dr3.pmra_error, dr3.pmdec, dr3.pmdec_error, \n"
            "dr3.nu_eff_used_in_astrometry, \n"
            "dr3.pseudocolour, dr3.ecl_lat, dr3.astrometric_params_solved, \n"
            "dr3.astrometric_excess_noise, dr3.astrometric_excess_noise_sig,\n"
            "dr3.ruwe, dr3.non_single_star, \n"
            "dr3.phot_g_mean_mag, "
            "dr3.phot_bp_mean_mag, dr3.phot_rp_mean_mag,\n"
            "b.r_med_geo/1000 AS r_med_geo, \n"
            "b.r_lo_geo/1000 AS r_lo_geo, \n"
            "b.r_hi_geo/1000 AS r_hi_geo, \n"
            "b.r_med_photogeo/1000 AS r_med_photogeo, \n"
            "b.r_lo_photogeo/1000 AS r_lo_photogeo, \n"
            "b.r_hi_photogeo/1000 AS r_hi_photogeo \n"
            f"FROM {user_table_name} AS u \n"
            # Require a matching Gaia DR3 row that meets filters (INNER JOIN)
            "JOIN gaiadr3.gaia_source AS dr3 \n"
            "  ON u.source_id = dr3.source_id \n"
            "  AND dr3.parallax_over_error >= 5 \n"
            # Distance may be missing; keep rows even if b is NULL (LEFT JOIN)
            "LEFT JOIN external.gaiaedr3_distance AS b \n"
            "  ON u.source_id = b.source_id \n"
        )

    elif scheme == "high_aen_sources":
        """
        Query to retrieve sources with astrometric excess noise (AEN);
        more details, see Gandhi et al. 2021 MNRAS, 510, 3885
        """
        query = (
            "SELECT u.ID_x, u.source_id, dr3.ra, dr3.dec, \n"
            "dr3.parallax, dr3.parallax_error, \n"
            "dr3.pmra, dr3.pmra_error, dr3.pmdec, dr3.pmdec_error, \n"
            "dr3.nu_eff_used_in_astrometry, \n"
            "dr3.pseudocolour, dr3.ecl_lat, dr3.astrometric_params_solved, \n"
            "dr3.astrometric_excess_noise, dr3.astrometric_excess_noise_sig,\n"
            "dr3.ruwe, dr3.non_single_star, \n"
            "dr3.phot_g_mean_mag, "
            "dr3.phot_bp_mean_mag, dr3.phot_rp_mean_mag,\n"
            "b.r_med_geo/1000 AS r_med_geo, \n"
            "b.r_lo_geo/1000 AS r_lo_geo, \n"
            "b.r_hi_geo/1000 AS r_hi_geo, \n"
            "b.r_med_photogeo/1000 AS r_med_photogeo, \n"
            "b.r_lo_photogeo/1000 AS r_lo_photogeo, \n"
            "b.r_hi_photogeo/1000 AS r_hi_photogeo \n"
            f"FROM {user_table_name} AS u \n"
            # Require a matching Gaia DR3 row that meets filters (INNER JOIN)
            "JOIN gaiadr3.gaia_source AS dr3 \n"
            "  ON u.source_id = dr3.source_id \n"
            "  AND dr3.parallax >= 0.1 \n"
            "  AND dr3.parallax <= 10.0 \n"
            "  AND dr3.parallax_over_error >= 5 \n"
            "  AND dr3.visibility_periods_used >= 10 \n"
            "  AND astrometric_excess_noise >= 0.01 \n"
            "  AND dr3.astrometric_excess_noise_sig >= 2 \n"
            "  AND dr3.phot_g_mean_mag <= 20 \n"
            "  AND dr3.phot_g_mean_mag >= 13 \n"
            # Distance may be missing; keep rows even if b is NULL (LEFT JOIN)
            "LEFT JOIN external.gaiaedr3_distance AS b \n"
            "  ON u.source_id = b.source_id \n"
        )

    elif scheme == "vol_limited_sources":
        query = (
            "SELECT u.ID_x, u.source_id, dr3.ra, dr3.dec, \n"
            "dr3.parallax, dr3.parallax_error, \n"
            "dr3.pmra, dr3.pmra_error, dr3.pmdec, dr3.pmdec_error, \n"
            "dr3.nu_eff_used_in_astrometry, \n"
            "dr3.pseudocolour, dr3.ecl_lat, dr3.astrometric_params_solved, \n"
            "dr3.astrometric_excess_noise, dr3.astrometric_excess_noise_sig,\n"
            "dr3.ruwe, dr3.non_single_star, \n"
            "dr3.phot_g_mean_mag, "
            "dr3.mh_gspphot, "
            "dr3.phot_bp_mean_mag, dr3.phot_rp_mean_mag,\n"
            "b.r_med_geo/1000 AS r_med_geo, \n"
            "b.r_lo_geo/1000 AS r_lo_geo, \n"
            "b.r_hi_geo/1000 AS r_hi_geo, \n"
            "b.r_med_photogeo/1000 AS r_med_photogeo, \n"
            "b.r_lo_photogeo/1000 AS r_lo_photogeo, \n"
            "b.r_hi_photogeo/1000 AS r_hi_photogeo \n"
            f"FROM {user_table_name} AS u \n"
            # Require a matching Gaia DR3 row that meets filters (INNER JOIN)
            "JOIN gaiadr3.gaia_source AS dr3 \n"
            "  ON u.source_id = dr3.source_id \n"
            "  AND dr3.parallax_over_error >= 5 \n"
            "  AND 1./dr3.parallax <= 1 \n"
            # Distance may be missing; keep rows even if b is NULL (LEFT JOIN)
            "LEFT JOIN external.gaiaedr3_distance AS b \n"
            "  ON u.source_id = b.source_id \n"
        )
    else:
        raise ValueError(f"Unknown option '{scheme}' for query rendering.")

    logger.info(
        f"Rendered query string for scheme '{scheme}':\n{query}"
    )

    return query


def login(service: str = "gaia", username: str | None = None) -> None:
    if username is None:
        username = input("Enter Gaia Archive username: ")

    password = keyring.get_password(service, username)
    if password is None:
        password = getpass.getpass(
            prompt=f"No password found for user '{username}'. "
            f"Enter password for Gaia Archive user '{username}': "
        )
        keyring.set_password(service, username, password)

    Gaia.login(user=username, password=password)
    logger.info(f"Logged in to Gaia Archive as user '{username}'.")


def _check_table_exists(user_name: str, table_name: str) -> bool:
    user_table_name = _get_user_table_name(user_name, table_name)

    all_tables = Gaia.load_tables(only_names=True, include_shared_tables=True)
    all_table_names = [
        table.get_qualified_name() for table in all_tables
    ]

    if user_table_name in all_table_names:
        logger.info(
            f"Table '{user_table_name}' exists in Gaia Archive "
            f"under the user '{user_name}'. Skipping upload."
        )
        return True
    else:
        logger.info(
            f"Table '{user_table_name}' does not exist in Gaia Archive "
            f"under the user '{user_name}'."
        )
        return False


def upload_table(username: str, table_path: Path, table_name: str) -> None:
    Gaia.upload_table(
        upload_resource=str(table_path),
        table_name=table_name,
        format="csv"
    )
    logger.info(
        f"Table from {table_path} uploaded to Gaia Archive "
        f"as table '{table_name}' ..."
        "The table name in the archive is "
        f"{_get_user_table_name(username, table_name)}."
    )


def query_gaia(query: str, **kwargs) -> None:
    _ = Gaia.launch_job_async(query, **kwargs)

    logger.info("Query completed.")


if __name__ == "__main__":
    username = "yzhao02"
    table_name = "hvxs_xray_catalogue_concat"
    # Options: astrometry, photometry, aen, gspphot, lsst_non_agn_matches
    scheme = "gspphot"
    login(username=username, service="gaia")

    table_exists = _check_table_exists(
        user_name=username, table_name=table_name
    )
    if not table_exists:
        upload_table(
            username=username,
            table_path=(
                config.RESULTS_CATALOGUES_FOR_REVISION
                / "nway_matched_results"
                / "xray_catalogue_concatenated_further_cleaned.csv"
            ),
            table_name=table_name
        )

    query = _render_query_str(username, table_name, scheme=scheme)

    query_gaia(
        query,
        name=f"[hvxs]get_{scheme}_for_cleaned_nway_matches",
        dump_to_file=True,
        output_file=str(
            config.RESULTS_CATALOGUES_FOR_REVISION
            / "gaia"
            / f"{scheme}.csv"
        ),
        output_format="csv"
    )
