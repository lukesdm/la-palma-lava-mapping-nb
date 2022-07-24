# La Palma Lava Mapping

A [JupyterLab](https://jupyter.org/) notebook and associated scripts for the analsyis and semi-automated mapping of the La Palma *Cumbre Vieja* eruption (September-December 2021),
using Sentinel-1 imagery.

## Getting started

The notebook is developed using a [Pangeo](https://github.com/pangeo-data/pangeo-docker-images)-based Docker JupyterLab environment.

The dataset is quite small, so is stored alongside the code in this repository.

### Running locally

Requires [Docker](https://www.docker.com/get-started/).

Execute the script `./start.sh`, assuming this is your current working directory. This will build and start a Docker container.
It's about 1GB, so will take some time.

The script will mount the current directory as a [Docker volume](https://docs.docker.com/storage/volumes/) so that you can make changes,
and they will show up in the Jupyter environment.

Once ready, look out for the link announcing the URL, which includes the access token. It will look something like:

```http://127.0.0.1:8888/lab?token=xxxxxx...```

### Running remotely

The [Microsoft Planetary Computer](https://planetarycomputer.microsoft.com/) is another option for running this notebook... with some tweaks.
It is currently free for non-commercial use, and new accounts typically take a couple of hours to approve.

Once you have an account, start a *CPU - Python* (Pangeo Notebook environment) instance.

#### Setup Sidecar

The notebook makes use of the [Sidecar widget extension](https://github.com/jupyter-widgets/jupyterlab-sidecar), which is not available in Pangeo, out-of-the-box.
To enable it: 
  * Go to the Extensions tab, and enable extensions.  
  * Open a new terminal, and run `pip install sidecar`.
  * Close any open notebooks, and reload the page

Upload the files from this repository to your environment, and you should now be able to run the notebook. 

## Credits

Imagery - Copernicus Sentinel-1, European Space Agency
