#!/bin/bash

eval $(docker-machine env uagent-local)

echo "Building container..."
docker build \
    -t uagent \
    -f docker/Dockerfile \
    .

echo "Running container..."
docker run \
    -it \
    -v uagent-run:/usr/src/uagent/run \
    -v uagent-webapp:/usr/src/uagent/webapp \
    uagent

eval $(docker-machine env -u)
