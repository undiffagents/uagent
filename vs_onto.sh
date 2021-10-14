#!/bin/bash
bash stop_server.sh
echo "Starting ontology server..."
python3.8 interpreter/interpreter.py --ace "tasks/vs/ace.txt"
echo ""
echo "ONTOLOGY INITIALIZED WITH /tasks/vs/ace.txt"
echo ""