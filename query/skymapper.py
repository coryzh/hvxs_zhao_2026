import pandas as pd
from astropy.coordinates import SkyCoord
from astropy.units import Quantity
from typing import List, Union
from astropy.io import fits


def query_skymapper_image_database(centre: SkyCoord, size: Quantity, filters: Union[str, List[str]],
                                   image_format: str = "image/fits", intersect: str = "CENTER", response_format: str = "HTML",
                                   verbosity: int = 0) -> str:
    filter_str = ",".join(filters) if isinstance(filters, list) else filters

    base_url = f"https://api.skymapper.nci.org.au/public/siap/dr4/query?"
    query_str = (f"POS={centre.ra.deg},{centre.dec.deg}&SIZE={size.to('deg').value:.5f}&BAND={filter_str}"
                 f"&INTERSECT={intersect}&FORMAT={image_format}&VERB={verbosity}&RESPONSEFORMAT={response_format}")

    url = f"{base_url}{query_str}"

    return url


def get_skymapper_image_fits(centre: SkyCoord, size: Quantity, unique_image_id: str) -> fits.HDUList:
    base_url = f"https://api.skymapper.nci.org.au/public/siap/dr4/get_image?"
    query_str = (f"IMAGE={unique_image_id}&SIZE={size.to('deg').value:.5f}&POS={centre.ra.deg},{centre.dec.deg}"
                 f"&FORMAT=fits")

    url = f"{base_url}{query_str}"
    hdul: fits.HDUList = fits.open(url)

    return hdul
