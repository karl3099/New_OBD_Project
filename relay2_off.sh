#!/bin/bash
# Turn relay 2 OFF
cd "$(dirname "$0")"  # Change to script directory
python3 relay_simple.py 2 off 