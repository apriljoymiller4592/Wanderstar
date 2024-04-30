#!/bin/bash
# Change directory to Wanderstar
cd $HOME/Wanderstar
# Set LIBFREENECT2_INSTALL_PREFIX environment variable
export LIBFREENECT2_INSTALL_PREFIX=/home/magicwanda/freenect2

# Add freenect2 library path to LD_LIBRARY_PATH
export LD_LIBRARY_PATH=/home/magicwanda/freenect2/lib:$LD_LIBRARY_PATH

# Activate virtual environment
source /home/magicwanda/Wanderstar/myenv/bin/activate

# Run Python script
python3 Artist.py

