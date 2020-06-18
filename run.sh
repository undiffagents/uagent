#!/bin/bash

ARGS=$@
if [ -z "$ARGS" ]
then
    ARGS="$UAGENT_ARGS"
fi

echo "Stopping existing servers..."
pkill -f "java"

echo "Starting ontology server..."
java -jar lib/fuseki/fuseki-server.jar --update &

echo "Starting simulation..."
python3 run.py $ARGS
