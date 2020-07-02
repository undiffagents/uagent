#!/bin/bash

eval $(docker-machine env uagent-local)

echo "Stopping existing container..."
docker stop $(docker ps -a -q)

echo "Removing existing container..."
docker rm $(docker ps -a -q)

eval $(docker-machine env -u)
