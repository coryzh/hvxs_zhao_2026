
class Schema:
    @classmethod
    def get_attribute_values(cls):
        return [value for key, value in cls.__dict__.items() if not key.startswith('__')]


class Swiftidentification(Schema):
    """
    A schema class representing column names from the Swift Point Source Catalogue (2SXPS).

    Attributes:
    ----------
    _2SXPS : str
        The identifier for the 2SXPS (Swift Point Source Catalogue) column.
    IAUName : str
        The column name for the International Astronomical Union (IAU) designation of the source.
    """
    SourceID: str = "2SXPS_ID"
    IAUName: str = "IAUName"


class SwiftCoord(Schema):
    """
       A schema class representing the astrometric data columns from the Swift Point Source Catalogue (2SXPS).

       Attributes:
       ----------
       RA : str
           Corrected Right Ascension of the detection in degrees (J2000 epoch).
       Decl : str
           Corrected Declination of the detection in degrees (J2000 epoch).
       Err90 : str
           90% confidence radial position uncertainty in arcseconds (90% confidence level).
       GLON : str
           Galactic longitude of the detection in degrees.
       GLAT : str
           Galactic latitude of the detection in degrees.
       AstromType : str
           The provenance of astrometry: 0 if from the Swift star trackers, 1 if rectified with 2MASS.
    """
    RA: str = "RA"
    DE: str = "Decl"
    POS_ERR: str = "Err90"
    GLON: str = "l"
    GLAT: str = "b"
    AstromType: str = "AstromType"


class ERASSSchema(Schema):
    RA: str = "RA"
    DE: str = "DEC"
    POS_ERR: str = "POS_ERR"


class CSCSchema(Schema):
    RA: str = "ra"
    DE: str = "dec"


class XMMSchema(Schema):
    RA: str = "sc_ra"
    DE: str = "sc_dec"
    POS_ERR: str = "sc_poserr"


class SwiftFlux(Schema):
    """
    A schema class representing flux-related columns from the Swift Point Source Catalogue (2SXPS).

    Attributes:
    ----------
    PowFlux : str
        Observed flux using a power-law model (0.3–10 keV) in erg/cm²/s.
    PowFlux_pos : str
        Positive error on the observed flux using the power-law model.
    PowFlux_neg : str
        Negative error on the observed flux using the power-law model.
    PowUnabsFlux : str
        Unabsorbed flux using a power-law model (0.3–10 keV) in erg/cm²/s.
    PowUnabsFlux_pos : str
        Positive error on the unabsorbed flux using the power-law model.
    PowUnabsFlux_neg : str
        Negative error on the unabsorbed flux using the power-law model.
    APECFlux : str
        Observed flux using an APEC (Astrophysical Plasma Emission Code) model (0.3–10 keV) in erg/cm²/s.
    APECFlux_pos : str
        Positive error on the observed flux using the APEC model.
    APECFlux_neg : str
        Negative error on the observed flux using the APEC model.
    APECUnabsFlux : str
        Unabsorbed flux using an APEC model (0.3–10 keV) in erg/cm²/s.
    APECUnabsFlux_pos : str
        Positive error on the unabsorbed flux using the APEC model.
    APECUnabsFlux_neg : str
        Negative error on the unabsorbed flux using the APEC model.
    """
    PowFlux: str = "PowFlux"
    PowFlux_pos: str = "PowFlux_pos"
    PowFlux_neg: str = "PowFlux_neg"
    PowUnabsFlux: str = "PowUnabsFlux"
    PowUnabsFlux_pos: str = "PowUnabsFlux_pos"
    PowUnabsFlux_neg: str = "PowUnabsFlux_neg"
    APECFlux: str = "APECFlux"
    APECFlux_pos: str = "APECFlux_pos"
    APECFlux_neg: str = "APECFlux_neg"
    APECUnabsFlux: str = "APECUnabsFlux"
    APECUnabsFlux_pos: str = "APECUnabsFlux_pos"
    APECUnabsFlux_neg: str = "APECUnabsFlux_neg"


class SwiftFlag(Schema):
    """
    A schema class representing various warning and flag columns from the Swift Point Source Catalogue (2SXPS).

    Attributes:
    ----------
    DetFlag : str
        Detection flag indicating the status or reliability of the source detection.
    Fieldflag : str
        Field flag providing information about the observation field, such as its quality or conditions.
    OpticalLoadingWarning : str
        Flag indicating a warning for potential optical loading, where bright optical sources may affect the X-ray
        detection.
    StrayLightWarning : str
        Warning flag indicating that stray light may have impacted the detection or measurement.
    NearBrightSourceWarning : str
        Warning flag indicating proximity to a bright source, which could influence the accuracy of the detection.
    """
    DetFlag: str = "DetFlag"
    Fieldflag: str = "FieldFlag"
    OpticalLoadingWarning: str = "OpticalLoadingWarning"
    StrayLightWarning: str = "StrayLightWarning"
    NearBrightSourceWarning: str = "NearBrightSourceWarning"


class Gaia(Schema):
    """
    This class contains column names for the Gaia data schema.

    Attributes:
        random_index (str): Random index.
        ra (str): Right Ascension.
        dec (str): Declination.
        parallax (str): Parallax.
        parallax_error (str): Error in parallax.
        parallax_over_error (str): Parallax over error.
        pmra (str): Proper motion in Right Ascension.
        pmra_error (str): Error in proper motion in Right Ascension.
        pmdec (str): Proper motion in Declination.
        pmdec_error (str): Error in proper motion in Declination.
        astrometric_params_solved (str): Number of astrometric parameters solved.
        pseudocolour (str): Pseudocolour.
        pseudocolour_error (str): Error in pseudocolour.
        ipd_frac_multi_peak (str): IPD fraction of multi-peak solutions.
        ipd_frac_odd_win (str): IPD fraction of odd windows.
        ruwe (str): Renormalised Unit Weight Error.
        phot_g_mean_flux_over_error (str): Phot G mean flux over error.
        phot_g_mean_mag (str): Phot G mean magnitude.
        phot_bp_mean_flux_over_error (str): Phot BP mean flux over error.
        phot_bp_mean_mag (str): Phot BP mean magnitude.
        phot_rp_mean_flux_over_error (str): Phot RP mean flux over error.
        phot_rp_mean_mag (str): Phot RP mean magnitude.
        phot_bp_rp_excess_factor (str): Phot BP-RP excess factor.
        bp_rp (str): BP-RP colour.
        radial_velocity (str): Radial velocity.
        radial_velocity_error (str): Error in radial velocity.
        rv_nb_transits (str): Number of radial velocity transits.
        rv_expected_sig_to_noise (str): Expected signal-to-noise ratio of radial velocity.
        rv_renormalised_gof (str): Renormalised goodness of fit of radial velocity.
        rv_chisq_pvalue (str): Chi-square p-value of radial velocity.
        phot_variable_flag (str): Photometric variability flag.
        l (str): Galactic longitude.
        b (str): Galactic latitude.
        in_qso_candidates (str): In QSO candidates.
        in_galaxy_candidates (str): In galaxy candidates.
        non_single_star (str): Non-single star flag.
        has_xp_continuous (str): Has XP continuous.
        has_xp_sampled (str): Has XP sampled.
        has_rvs (str): Has RVS.
        has_epoch_photometry (str): Has epoch photometry.
        has_epoch_rv (str): Has epoch radial velocity.
        has_mcmc_gspphot (str): Has MCMC GSPPhot.
        has_mcmc_msc (str): Has MCMC MSC.
        in_andromeda_survey (str): In Andromeda survey.
        teff_gspphot (str): Effective temperature from GSPPhot.
        logg_gspphot (str): Surface gravity from GSPPhot.
        mh_gspphot (str): Metallicity from GSPPhot.
        distance_gspphot (str): Distance from GSPPhot.
        ag_gspphot (str): Extinction from GSPPhot.
        ebpminrp_gspphot (str): E(BP-RP) extinction from GSPPhot.
        source_id (str): Source identifier.
    """

    random_index: str = "random_index"
    ra: str = "ra"
    dec: str = "dec"
    parallax: str = "parallax"
    parallax_error: str = "parallax_error"
    parallax_over_error: str = "parallax_over_error"
    pmra: str = "pmra"
    pmra_error: str = "pmra_error"
    pmdec: str = "pmdec"
    pmdec_error: str = "pmdec_error"
    astrometric_params_solved: str = "astrometric_params_solved"
    pseudocolour: str = "pseudocolour"
    pseudocolour_error: str = "pseudocolour_error"
    ipd_frac_multi_peak: str = "ipd_frac_multi_peak"
    ipd_frac_odd_win: str = "ipd_frac_odd_win"
    ruwe: str = "ruwe"
    phot_g_mean_flux_over_error: str = "phot_g_mean_flux_over_error"
    phot_g_mean_mag: str = "phot_g_mean_mag"
    phot_bp_mean_flux_over_error: str = "phot_bp_mean_flux_over_error"
    phot_bp_mean_mag: str = "phot_bp_mean_mag"
    phot_rp_mean_flux_over_error: str = "phot_rp_mean_flux_over_error"
    phot_rp_mean_mag: str = "phot_rp_mean_mag"
    phot_bp_rp_excess_factor: str = "phot_bp_rp_excess_factor"
    bp_rp: str = "bp_rp"
    radial_velocity: str = "radial_velocity"
    radial_velocity_error: str = "radial_velocity_error"
    rv_nb_transits: str = "rv_nb_transits"
    rv_expected_sig_to_noise: str = "rv_expected_sig_to_noise"
    rv_renormalised_gof: str = "rv_renormalised_gof"
    rv_chisq_pvalue: str = "rv_chisq_pvalue"
    phot_variable_flag: str = "phot_variable_flag"
    l: str = "l"
    b: str = "b"
    in_qso_candidates: str = "in_qso_candidates"
    in_galaxy_candidates: str = "in_galaxy_candidates"
    non_single_star: str = "non_single_star"
    has_xp_continuous: str = "has_xp_continuous"
    has_xp_sampled: str = "has_xp_sampled"
    has_rvs: str = "has_rvs"
    has_epoch_photometry: str = "has_epoch_photometry"
    has_epoch_rv: str = "has_epoch_rv"
    has_mcmc_gspphot: str = "has_mcmc_gspphot"
    has_mcmc_msc: str = "has_mcmc_msc"
    in_andromeda_survey: str = "in_andromeda_survey"
    teff_gspphot: str = "teff_gspphot"
    logg_gspphot: str = "logg_gspphot"
    mh_gspphot: str = "mh_gspphot"
    distance_gspphot: str = "distance_gspphot"
    ag_gspphot: str = "ag_gspphot"
    ebpminrp_gspphot: str = "ebpminrp_gspphot"
    source_id: str = "source_id"
    parallax_corr: str = "parallax_corr"
    has_valid_parallax_corr: str = "has_valid_parallax_corr"
    astrometric_excess_noise: str = "astrometric_excess_noise"


class SimbadSchema(Schema):
    """Schema for the Simbad database"""
    SIMBAD_OTYPE: str = "otype"
    SIMBAD_OTYPES: str = "other_types"
    SIMBAD_MAIN_TYPE: str = "main_type"
    # SIMBAD_OTYPE_OPT: str = "OTYPE_opt"
    SIMBAD_ID: str = "main_id"
    # SIMBAD_IDS: str = "IDS"


class LX:
    def __init__(self, band: str):
        self.band = band

    @property
    def lx_colname(self) -> str:
        return f"lum_{self.band}"

    @property
    def lx_err_colname(self) -> str:
        return f"lum_{self.band}_err"

    @property
    def lx_lolim_colname(self) -> str:
        return f"lum_{self.band}_lolim"
