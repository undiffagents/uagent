#!/bin/bash

eval $(docker-machine env uagent-local)

echo "Building container..."
docker build -t uagent -f docker/Dockerfile .

echo "Running container..."
docker run -it uagent

eval $(docker-machine env -u)
