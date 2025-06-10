#!/usr/bin/env python3
"""
Book Processor Runner Script

This script runs the book processor with the correct Python path setup.
"""
import os
import sys
import subprocess

# Add the parent directory to the Python path
parent_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, parent_dir)

# Import the main function directly
from main import main

if __name__ == "__main__":
    # Set environment variables for external tools
    poppler_path = os.path.join(os.path.expanduser("~"), "poppler", "poppler-23.11.0", "Library", "bin")
    
    # Add poppler to PATH if it exists
    if os.path.exists(poppler_path):
        os.environ["PATH"] = poppler_path + os.pathsep + os.environ.get("PATH", "")
    
    # Run the main function
    sys.exit(main())
