#!/usr/bin/env python3
"""
Book Processor Runner Script

This script runs the book processor with the correct Python path setup.
"""
import os
import sys

from main import main

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

if __name__ == "__main__":
    sys.exit(main())
