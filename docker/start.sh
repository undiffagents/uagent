#!/bin/bash

echo "Stopping existing servers..."
pkill -f "java"

echo "Starting ontology server..."
java -jar lib/fuseki/fuseki-server.jar --update &

echo "Starting agent..."
python3 uagent.py
