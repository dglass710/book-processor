#!/bin/bash
#
# Simple setup script for Book Processor (macOS)
# Contains just the necessary brew and pip commands
#

# Install system dependencies
brew install tesseract djvulibre calibre 

# Install Python dependencies
pip3 install PyMuPDF>=1.21.1 Pillow>=9.5.0 PyPDF2>=3.0.0

# Install development tools
pip3 install pyright flake8 black isort pytest
