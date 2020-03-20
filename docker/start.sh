#!/bin/bash

echo "Starting ontology server..."
java -jar ontology/fuseki-server.jar --update &

echo "Starting agent..."
python3 uagent.py
