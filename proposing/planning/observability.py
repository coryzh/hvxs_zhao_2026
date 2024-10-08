import pandas as pd
from astropy.coordinates import SkyCoord
from astropy.time import Time
from astroplan import Observer, FixedTarget
from astroplan import (AltitudeConstraint, AirmassConstraint,
                       AtNightConstraint)
from astroplan import is_observable, months_observable
from log.loggers import VerboseLogger
import config
import astropy.units as u
import pytz


def check_observability(verbose: bool = False) -> None:
    logger = VerboseLogger(verbose=verbose)

    in_file = (config.RESULTS_CATALOGUE_DIR / "high-v_sources" / "palomar"
               / "sources_gmag_lt_17_fxfg_vpec_lolim_gt_150.csv")
    logger.begin()
    logger.log(f"Loading source catalogues")
    df = pd.read_csv(in_file)
    logger.log(f"{df.shape[0]} sources loaded.\n")

    observer = Observer.at_site("Palomar")
    time_range = Time(["2025-10-01 07:00:00", "2025-10-04 07:00:00"])

    target_list = [FixedTarget(coord=SkyCoord(ra=row.ra * u.deg, dec=row.dec * u.deg), name=row.ID_x)
                   for row in df.itertuples()]

    obs_constraints = [AirmassConstraint(2.0),
                       AtNightConstraint.twilight_civil(),
                       AltitudeConstraint(10 * u.deg, None)]

    logger.log(f"Checking for visibility ...")
    observable = is_observable(constraints=obs_constraints, observer=observer, targets=target_list, time_range=time_range)
    observable_months = months_observable(constraints=obs_constraints, observer=observer, targets=target_list,
                                          time_range=time_range)
    logger.log(f"Visibility checked for {df.shape[0]} targets, of which {sum(observable)} are observable with "
               f"the constraints.\n")

    df["observable"] = observable
    df["observable_months"] = observable_months

    df_observable = df[df.observable]

    out_file = in_file.parent / f"{in_file.stem}_w_observability.csv"
    out_file_observable = in_file.parent / f"{in_file.stem}_observable.csv"
    df.to_csv(out_file, index=False)
    df_observable.to_csv(out_file_observable, index=False)
    logger.log(f"Writing the updated target list to {out_file} ...")
    logger.log(f"Observable targets are saved to {out_file_observable}.")
    logger.log(f"All targets saved to {out_file}.\n")
    logger.end()


def main() -> None:
    check_observability(verbose=True)


if __name__ == "__main__":
    main()
