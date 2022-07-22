import folium
import geopandas
import numpy

import lplm_io as lpio

from lplm_utils import format_date

def get_date_labels(xds):
    return [(format_date(d), d) for d in xds.sortby("date").date.values]

def build_map(gdf: geopandas.GeoDataFrame, date: numpy.datetime64) -> folium.Map:
    """Builds a Folium map with segment layer and SAR image for the given date""" 
    fol_map = gdf.explore(style_kwds={"fill": False, "weight": 1})
    img_path = lpio.get_jpg(date)
    bounds_gdf = gdf.to_crs("EPSG:4326").total_bounds
    bounds_fol = [[bounds_gdf[3], bounds_gdf[2]], [bounds_gdf[1], bounds_gdf[0]]]
    sar_overlay = folium.raster_layers.ImageOverlay(
        name=f"SAR for {date}",
        image=str(img_path),
        z_index=1,
        bounds=bounds_fol)
    sar_overlay.add_to(fol_map)
    folium.LayerControl().add_to(fol_map)
    return fol_map