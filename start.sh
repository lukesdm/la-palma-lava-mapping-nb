# If running with Git Bash in Windows
MSYS_NO_PATHCONV=1

# Build and run the docker environment; it is approximately 1GB in size.
# Once ready, look out for the link announcing the URL, which includes the token.
docker build -t lplm-nb .
docker run -it --rm --volume $(pwd):/home/jovyan/lplm -p 127.0.0.1:8888:8888 lplm-nb jupyter lab --ip 0.0.0.0 lplm
