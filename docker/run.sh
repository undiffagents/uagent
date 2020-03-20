#!/bin/bash

eval $(docker-machine env uagent-local)

echo "Building container..."
docker build -t uagent .

echo "Running container..."
docker run -it -p 3030:3030 uagent

eval $(docker-machine env -u)
