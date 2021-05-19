#!/bin/bash

ARGS=$@
if [ -z "$ARGS" ]
then
    ARGS="$UAGENT_ARGS"
fi

echo "Starting simulation..."
python3.8 run.py $ARGS
