#!/bin/bash

ARGS=$@
if [ -z "$ARGS" ]
then
    ARGS="$UAGENT_ARGS"
fi

echo "Starting simulation; console output being piped to data/logs/console-logfile.txt"
python3.8 run.py --gaptest $ARGS &> "data/logs/console-logfile.txt"
echo "Simulation complete."