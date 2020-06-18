#!/bin/bash

ARGS="$@"

eval $(docker-machine env uagent-local)

echo "Building container..."
docker build \
    --build-arg "ARGS=$ARGS" \
    -f docker/Dockerfile \
    -t uagent \
    .

echo "Running container..."
docker run \
    -it \
    -v uagent-data:/usr/src/uagent/data \
    -v uagent-run:/usr/src/uagent/run \
    -v uagent-webapp:/usr/src/uagent/webapp \
    -p 4321:4321 \
    uagent

eval $(docker-machine env -u)
