#!/bin/bash
#
# Simple setup script for Book Processor
# Contains just the necessary apt and pip commands
#

# Install system dependencies
apt-get update
apt-get install -y tesseract-ocr djvulibre-bin python3 python3-pip

# Install Python dependencies
pip install PyMuPDF>=1.21.1 Pillow>=9.5.0

# Install development tools
pip install pyright flake8 black isort
