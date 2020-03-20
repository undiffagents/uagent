#!/bin/bash

BASE=$PWD

echo "Base directory: $BASE"

echo "Stopping servers???"
# pkill -f python3

echo "Starting servers???"
# can start various servers here

echo "Starting run..."
python3 uagent.py
