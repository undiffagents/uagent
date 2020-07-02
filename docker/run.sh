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
    -p 4321:4321 \
    uagent

eval $(docker-machine env -u)
