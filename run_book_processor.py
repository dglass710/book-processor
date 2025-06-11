#!/usr/bin/env python3
"""
Book Processor Runner Script

This script runs the book processor with the correct Python path setup.
"""
import os
import sys

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Import the main function directly
from main import main

if __name__ == "__main__":
    sys.exit(main())
