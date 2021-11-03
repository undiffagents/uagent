#!/bin/bash

ARGS=$@
if [ -z "$ARGS" ]
then
    ARGS="$UAGENT_ARGS"
fi

echo "Removing old log files..."
rm -fr data/logs/*

echo "Starting simulation..."
python3.8 run.py $ARGS > "data/logs/console-logfile.txt"
