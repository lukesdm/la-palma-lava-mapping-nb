from typing import Callable
import geopandas
import numpy
import pandas
import rasterio
from shapely.geometry import shape
from skimage.segmentation import slic
import xarray

## Segmentation
## ------------

def apply_segmentation(xds_grd: xarray.Dataset,
                       date: numpy.datetime64,
                       n_segments = 5000,
                       compactness = 0.1):
    """Performs SLIC0 segmentation on the image for the given date, adding a 'segment_id' variable to the dataset"""
    # Segments an image according to:
    # https://docs.dea.ga.gov.au/notebooks/Frequently_used_code/Image_segmentation.html
    #
    # For an explanation of slic params, see:
    # https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.slic

    # skimage-friendly format
    np_image = xds_grd.sel(date=date).to_numpy()

    # This seems to give OK-ish results
    np_segments = slic(np_image, n_segments=n_segments, slic_zero=True, compactness=compactness)

    xa_segments = xarray.DataArray(np_segments,
             coords=xds_grd.drop("date").coords,
             dims=['y', 'x'],
             attrs=xds_grd.attrs)

    xds_grd["segment_id"] = xa_segments

    # xarray has been modified in-place, nothing to return.
    return None

def vectorize_segments(xds_grd):
    """Create a vector layer (GeoDataFrame) from the segment raster layer"""
    # Borrowed heavily from:
    # https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/blob/main/Tools/deafrica_tools/spatial.py#L28
    xa_segments = xds_grd.segment_id.astype("int16")
    shapes = list(
        rasterio.features.shapes(xa_segments.to_numpy(), transform = xds_grd.rio.transform())
    )
    polygons = [shape(polygon) for polygon, _ in shapes]
    segment_ids = [int(segment_id) for _, segment_id in shapes]
    gdf = geopandas.GeoDataFrame(
        data={"segment_id": segment_ids},
        geometry=polygons,
        index=segment_ids,
        crs=xds_grd.rio.crs )

    # We have to sort here, otherwise subsequent bulk field additions get jumbled.
    gdf.sort_index(axis=0, inplace=True)

    return gdf

def get_segment_id(gdf, x, y, delta = 0.1):
    """
    Get segment id for the given point.

    Note:
    
    * Lookup is performed with a very small bounding box, and it's possible multiple
    segments intersect. The first match is selected.
    
    * An optional `delta` argument can be set if operating at a different scale or CRS
    """
    segment_id = gdf.cx[
        x:x + delta,
        y:y + delta
    ].iloc[0]["segment_id"]
    return segment_id


## Lava analysis and region growing
## --------------------------------

def make_similarity_func(field: str, reference_sample: geopandas.GeoDataFrame) -> Callable[[geopandas.GeoSeries], float]:
    low = reference_sample[field].quantile(0.0)
    q1 = reference_sample[field].quantile(0.25)
    q3 = reference_sample[field].quantile(0.75)
    high = reference_sample[field].quantile(1.0)

    f = lambda seg_data: numpy.interp(
        x = seg_data[field],
        xp = [low, q1, q3, high],
        fp = [0.25, 1.0, 1.0, 0.25],
        left = 0,
        right = 0 )

    return f


# Calculate lava-likeness index. Input should be a GeoSeries representing a single object
def local_lava_likeness(segment_data: geopandas.GeoSeries) -> float:
    ll = (segment_data.lava_mean_similarity + segment_data.lava_std_similarity) / 2
    return ll


def get_neighbours(gdf, segment_id):
    return gdf[gdf.touches(gdf.loc[segment_id].geometry)]


def get_neighbours_of_neighbours(gdf, segment_id):
    neighs = get_neighbours(gdf, segment_id)
    n_of_n = []
    for neighbor_segment_id, _ in neighs.iterrows():
        n_of_n.append(get_neighbours(gdf, neighbor_segment_id))

    to_exclude = [segment_id, *list(neighs.segment_id)]
    n_of_n = pandas.concat(n_of_n).drop(to_exclude)

    return geopandas.GeoDataFrame(n_of_n)


def neighbourhood_lava_likeness(gdf, segment_id) -> float:
    neighbors = get_neighbours(gdf, segment_id)
    
    # COULDDO: Consider neighbours of neighbours.
    # neighbors_of_neighbours = get_neighbours_of_neighbours(gdf, segment_id)
    
    return (
        0.5 * gdf.loc[segment_id]["local_lava_likeness"] + 
        0.5 * neighbors["local_lava_likeness"].sum() / len(neighbors) )


def get_unvisited_neighbors(gdf, segment_id, group_id):
    all_neighbors = gdf[gdf.touches(gdf.loc[segment_id].geometry)]
    new_neighbors = all_neighbors[gdf.group != group_id]
    return new_neighbors


# COULDDO: Parameterize this. But, have to also consider the weighting of the components. 
LL_THRESHOLD = 0.5

def lava_likeness_overall(gdf, start_segment_id):
    """
    Final lava-likeness calculation. Grows a region using the starting segment as a seed,
    taking into account the local and neighbourhood lava-likenesses, and whether combined
    they exceed a preset threshold.
    """
    gdf["neighbourhood_lava_likeness"] = gdf["local_lava_likeness"]
    gdf["group"] = gdf.segment_id
    gdf.at[start_segment_id, "neighbourhood_lava_likeness"] = 1.0
    to_visit = [start_segment_id]
    while len(to_visit) > 0:
        current_segment_id = to_visit.pop()
        neighs = get_unvisited_neighbors(gdf, current_segment_id, start_segment_id)
        for neigh_seg_id, _ in neighs.iterrows():
            ll = neighbourhood_lava_likeness(gdf, neigh_seg_id)
            if ll > LL_THRESHOLD:
                gdf.at[neigh_seg_id, "neighbourhood_lava_likeness"] = 1.0
                gdf.at[neigh_seg_id, "group"] = start_segment_id
                to_visit.append(neigh_seg_id)

    
def extract_lava_region(gdf, start_segment_id):
    return gdf[gdf["group"] == start_segment_id].dissolve()


def segment_stats(xds_grd):
    """
    Calculate segment pixel statistics: mean; standard deviation.

    Note:
      * These are calculated for all dates, effectively using a single segmentation result as a mask layer,
        i.e., same segment, different day.
      * This would be impractical for larger datasets, where subsetting would be appropriate.
    """
    
    # Available stat/aggregate functions are listed here:
    # https://xarray.pydata.org/en/v0.11.3/generated/xarray.core.groupby.DataArrayGroupBy.html
    segments = xds_grd.groupby('segment_id')
    means = segments.mean()
    stds = segments.std()
    return xarray.Dataset({"mean": means, "std":stds})


def enrich_stats(gdf, xds_segstats, date):
    """Enrich the GeoDataFrame with the segment stats"""

    gdf["mean"] = xds_segstats.sel(date=date)["mean"]
    gdf["std"] = xds_segstats.sel(date=date)["std"]

    # gdf was modified in-place, so nothing to return.
    return None

def enrich_lava_likeness(gdf, reference_sample):
    """
    Enrich the GeoDataFrame with the derived lavalikeness metrics, based on the given reference sample.

    The sample should be from known lava flow.
    """

    lava_mean_similarity = make_similarity_func("mean", reference_sample)
    lava_std_similarity = make_similarity_func("std", reference_sample)

    gdf["lava_mean_similarity"] = gdf.apply(lambda gds: lava_mean_similarity(gds), axis=1)
    gdf["lava_std_similarity"] = gdf.apply(lambda gds: lava_std_similarity(gds), axis=1)
    gdf["local_lava_likeness"] = gdf.apply(local_lava_likeness, axis=1)

    # gdf was modified in-place, so nothing to return.
    return None
