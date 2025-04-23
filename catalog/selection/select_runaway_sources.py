import config
import pandas as pd
from potential import MW
from galpy.potential import vesc
from pathlib import Path
from astropy.units import Unit


def select_runaway(in_file: Path) -> None:
    df = pd.read_csv(in_file)

    r_gc = df["r_gc"].values * Unit("kpc")

    v_escape = vesc(MW, r_gc)

    v_space_min_lolim = df["vspace_min_med"] - df["e_vspace_min"]

    _filter = v_space_min_lolim >= v_escape.value

    df_filtered = df[_filter]

    out_file = (
        in_file.parent.parent
        / "runaway_sources"
        / f"{in_file.stem}_runaway.csv"
    )
    df_filtered.to_csv(out_file, index=False)


def main() -> None:
    in_file = (
        config.RESULTS_CATALOGUE_DIR
        / "high-v_sources"
        / "combined_vpec_lolim_gt_200_unique_stage_9.csv"
    )
    select_runaway(in_file)


if __name__ == "__main__":
    main()
