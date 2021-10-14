#!/bin/bash
bash stop_server.sh
echo "Starting ontology server..."
python3.8 interpreter/interpreter.py --ace "tasks/pvt/ace.txt"
echo ""
echo "ONTOLOGY INITIALIZED WITH /tasks/pvt/ace.txt"
echo ""