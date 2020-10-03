#!/bin/bash

ARGS=$@
if [ -z "$ARGS" ]
then
    ARGS="$UAGENT_ARGS"
fi

echo "Stopping existing servers..."
pkill -f "java"

echo "Starting simulation..."
python3.8 run.py $ARGS
