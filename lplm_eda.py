# Exploratory data analysis
# -------------------------

import matplotlib.pyplot as plt

def plot_segment_histos(xds_grd, segment_ids, date):
    """
    Plot pixel value histograms for the given segments.
    
    Usage example:

    `plot_segment_histos(xds_grd, [2690, 2614, 2593, 2560], date='2021-09-16')`
    """
    fig, axes = plt.subplots(
        ncols=2,
        nrows=len(segment_ids),
        figsize=[6.4,10] )
    for row, segment_id in enumerate(segment_ids):
        seg_data = xds_grd.where(xds_grd.segment_id == segment_id, drop=True).sel(date=date)
        seg_data.plot(ax=axes[row, 0], vmin=0, vmax=250, cmap="gray")
        seg_data.plot.hist(
            ax=axes[row, 1],
            range=(0,250),
            bins=20 )
        axes[row,1].set_title(f"segment_id: {segment_id}")
        axes[row,0].set_title(f"")
    plt.tight_layout()
    plt.show()
