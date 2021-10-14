#!/bin/bash

ARGS=$@
if [ -z "$ARGS" ]
then
    ARGS="$UAGENT_ARGS"
fi
#"tasks/pvt/ace.txt"
#"tasks/vs/ace.txt"
echo "Starting ontology server..."
# java -jar lib/fuseki/fuseki-server.jar --update &
python3.8 interpreter/interpreter.py $ARGS