# La Palma Lava Mapping

## Getting started

This notebook was developed in a [Pangeo](https://github.com/pangeo-data/pangeo-docker-images) container environment.

To run locally, allowing editing from your host machine:

```
docker run -it --rm --volume $(pwd):/home/jovyan/lplm -p 127.0.0.1:8888:8888 pangeo/pangeo-notebook:latest jupyter lab --ip 0.0.0.0 lplm
```

Then connect with http://localhost:8888.

## Credits

Imagery - Copernicus Sentinel-1, European Space Agency
