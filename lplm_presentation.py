import ipyleaflet
import geopandas
import numpy
from ipyleaflet import Choropleth
from branca.colormap import linear
import json

import base64

import lplm_io as lpio

from lplm_utils import format_date

def get_date_labels(xds):
    return [(format_date(d), d) for d in xds.sortby("date").date.values]

def sar_layer_name(date):
    return f"SAR (GRD, VV, gamma0) @ {format_date(date)}"

def make_sar_layer(xds, date):
    """
    Creates a raster layer for the SAR data for the given date.

    Note: Uses data-uri format so that no files have to be served.
    This is ok for small images, like jpegs of our study area. 
    """
    bounds_4326 = xds.rio.transform_bounds("epsg:4326")
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
        name=sar_layer_name(date))

def make_feature_layer(gdf, feature):
    # COULDDO: check feature exists in dataframe, pass in from dropdown
    
    # Prepare geojson input for ipyleaflet's choropleth interface.
    # Thanks to Abdishakur, https://towardsdatascience.com/ipyleaflet-interactive-mapping-in-jupyter-notebook-994f19611e79
    geojson = json.loads(gdf.loc[:, ["segment_id", "geometry"]].to_crs("EPSG:4326").to_json())
    for gjfeature in geojson["features"]:
        properties = gjfeature["properties"]
        gjfeature.update(id=properties["segment_id"])

    layer = Choropleth(
        geo_data = geojson,
        choro_data = gdf[feature].to_dict(),
        colormap=linear.viridis, # COULDDO: Parameterize
        style = { "fillOpacity": 0.5, "weight": 1.0 },
        name=f"Segment {feature}")

    return layer

def find_layers(m: ipyleaflet.Map, name: str):
    """Gets map layer(s) with the specified name"""
    layers = []
    for l in m.layers:
        if l.name == name:
            layers.append(l)
    return layers

def replace_layer(m: ipyleaflet.Map, new_layer: ipyleaflet.Layer, old_name: str = None):
    """Removes any old matching layers, and adds the new one"""
    haystack = find_layers(m, new_layer.name) if (old_name == new_layer.name or old_name is None) else [*find_layers(m, old_name), *find_layers(m, new_layer.name)]
    for l in haystack:
        m.remove(l)
    m.add_layer(new_layer)
    return None
