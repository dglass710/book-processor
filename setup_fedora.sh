#!/bin/bash
#
# Simple setup script for Book Processor
# Contains just the necessary dnf and pip commands
#

# Install system dependencies
dnf check-update
dnf install -y tesseract djvulibre calibre python3 python3-pip

# Install Python dependencies
pip install PyMuPDF>=1.21.1 Pillow>=9.5.0 PyPDF2>=3.0.0 ebooklib>=0.17.1

# Install development tools
pip install 'pyright[nodejs]' flake8 black isort pytest
