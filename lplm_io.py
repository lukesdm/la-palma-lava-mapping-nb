import numpy
import pandas
from pathlib import Path
import rioxarray
import xarray

from lplm_utils import format_date

def load_series(data_dir="data"):
    """
    Loads a time-series of Sentinel-1 Ground-range detected (GRD) GeoTiffs. Expected name format: 'YYYY-MM-DD.tif'.
    They should have the same acquisition parameters and footprint.
    """
    img_paths = list(Path(data_dir).glob("*.tif"))
    xarrs = []
    for img_path in img_paths:
        xarr = rioxarray.open_rasterio(img_path).sel(band=1)
        xarr["date"] = pandas.to_datetime(img_path.stem)
        xarrs.append(xarr)
    return xarray.concat(xarrs, "date")

def get_jpg(date: numpy.datetime64, data_dir="data-jpg") -> Path:
    stem = format_date(date)
    path = Path(data_dir, f"{stem}.jpg")
    assert(path.exists())
    return path
