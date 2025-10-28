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
            "dr3.phot_g_mean_mag, dr3.nu_eff_used_in_astrometry, \n"
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
            "  AND dr3.astrometric_params_solved IN (31, 63, 95) \n"
            "  AND dr3.classprob_dsc_combmod_star >= 0.9 \n"
            # Distance may be missing; keep rows even if b is NULL (LEFT JOIN)
            "LEFT JOIN external.gaiaedr3_distance AS b \n"
            "  ON u.source_id = b.source_id \n"
        )
    elif scheme == "photometry":
        query = (
            "SELECT u.ID_x, u.source_id, dr3.phot_g_mean_mag, \n"
            "dr3.phot_bp_mean_mag, dr3.phot_rp_mean_mag, \n"
            "dr3.bp_rp, \n"
            f"FROM {user_table_name} AS u \n"
            "LEFT JOIN gaiadr3.gaia_source AS dr3 \n"
            "  ON u.source_id = dr3.source_id \n"
            "  AND dr3.astrometric_params_solved IN (31, 63, 95) \n"
            "  AND dr3.classprob_dsc_combmod_star >= 0.9 \n"
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
    user_table_name = "hvxs_xray_catalogue_concat"
    login(username=username, service="gaia")

    upload_table(
        username=username,
        table_path=(
            config.RESULTS_CATALOGUE_DIR
            / "nway_matched_results"
            / "xray_catalogue_concatenated.csv"
        ),
        table_name=user_table_name
    )

    query = _render_query_str(username, user_table_name, scheme="astrometry")

    query_gaia(
        query, dump_to_file=True,
        output_file=str(
            config.RESULTS_CATALOGUE_DIR
            / "gaia_astrometry_catalogues"
            / "gaia_astrometry_stars_only.csv"
        ),
        output_format="csv"
    )
