#!/bin/bash
# Turn relay 1 OFF
cd "$(dirname "$0")"  # Change to script directory
python3 relay_simple.py 1 off 