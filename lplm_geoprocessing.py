import geopandas
import numpy
import rasterio
from shapely.geometry import shape
from skimage.segmentation import slic
import xarray

def apply_segmentation(xds: xarray.Dataset,
                       date: numpy.datetime64,
                       n_segments = 5000,
                       compactness = 0.1):
    """Performs SLIC0 segmentation on the image on the given date, adding a 'segment_id' variable to the dataset"""
    # Segments an image according to:
    # https://docs.dea.ga.gov.au/notebooks/Frequently_used_code/Image_segmentation.html
    #
    # For an explanation of slic params, see:
    # https://scikit-image.org/docs/dev/api/skimage.segmentation.html#skimage.segmentation.slic

    # skimage-friendly format
    np_image = xds.sel(date=date).to_numpy()

    # This seems to give OK-ish results
    np_segments = slic(np_image, n_segments=n_segments, slic_zero=True, compactness=compactness)

    xa_segments = xarray.DataArray(np_segments,
             coords=xds.drop("date").coords,
             dims=['y', 'x'],
             attrs=xds.attrs)

    xds["segment_id"] = xa_segments

    # xarray has been modified in-place, nothing to return.
    return None

def vectorize_segments(xds):
    """Create a vector layer (GeoDataFrame) from the segment raster layer"""
    # Borrowed heavily from:
    # https://github.com/digitalearthafrica/deafrica-sandbox-notebooks/blob/main/Tools/deafrica_tools/spatial.py#L28
    xa_segments = xds.segment_id.astype("int16")
    shapes = list(
        rasterio.features.shapes(xa_segments.to_numpy(), transform = xds.rio.transform())
    )
    polygons = [shape(polygon) for polygon, _ in shapes]
    segment_ids = [int(segment_id) for _, segment_id in shapes]
    gdf = geopandas.GeoDataFrame(
        data={"segment_id": segment_ids},
        geometry=polygons,
        index=segment_ids,
        crs=xds.rio.crs )

    # We have to sort here, otherwise subsequent bulk field additions get jumbled.
    gdf.sort_index(axis=0, inplace=True)

    return gdf