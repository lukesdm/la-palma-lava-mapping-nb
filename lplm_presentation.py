import ipyleaflet
import geopandas
import numpy

import base64

import lplm_io as lpio

from lplm_utils import format_date

def get_date_labels(xds):
    return [(format_date(d), d) for d in xds.sortby("date").date.values]

def make_sar_layer(xds, date):
    """
    Creates a raster layer for the SAR data for the given date.

    Note: Uses data-uri format so that no files have to be served.
    This is ok for small images, like jpegs of our study area. 
    """
    bounds_4326 = xds.rio.transform_bounds("+init=epsg:4326")
    bounds_leaf = (bounds_4326[1], bounds_4326[0]), (bounds_4326[3], bounds_4326[2])
    # Use a .jpg version for presentation, due to the smaller file size.
    img_path = lpio.get_jpg(date)
    # data-uri encode
    with open(img_path, 'rb') as img_file:
        img_data = img_file.read()
    data_url = 'data:image/jpeg;base64,' + base64.b64encode(img_data).decode('utf-8')
    return ipyleaflet.ImageOverlay(
        url=data_url,
        bounds=bounds_leaf,
        name=f"SAR (gamma0) @ {format_date(date)}")