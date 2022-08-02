FROM pangeo/pangeo-notebook:latest

# Enable extensions
RUN mkdir -p "/home/jovyan/.jupyter/lab/user-settings/@jupyterlab/extensionmanager-extension/"
RUN echo '{"disclaimed":true}'>"/home/jovyan/.jupyter/lab/user-settings/@jupyterlab/extensionmanager-extension/plugin.jupyterlab-settings"

# Additional dependencies
RUN pip install sidecar
