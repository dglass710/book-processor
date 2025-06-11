#!/bin/bash
#
# Setup script for Book Processor on Linux (Debian/Ubuntu)
# This script installs all required dependencies using apt and pip
#

echo "====================================================="
echo "Setting up Book Processor dependencies for Linux"
echo "====================================================="

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run this script with sudo:"
    echo "sudo $0"
    exit 1
fi

# Update package lists
echo "Updating package lists..."
apt update

# Install Python and pip if not already installed
echo "Installing Python and pip..."
apt install -y python3 python3-pip

# Install Tesseract OCR
echo "Installing Tesseract OCR..."
apt install -y tesseract-ocr

# Install additional language data if needed
# Uncomment and modify as needed
# apt install -y tesseract-ocr-eng tesseract-ocr-fra

# Verify Tesseract installation
if command_exists tesseract; then
    echo "[OK] Tesseract OCR installed successfully"
    tesseract --version
else
    echo "[ERROR] Failed to install Tesseract OCR"
    exit 1
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install -r requirements.txt

# Verify Python dependencies
echo "Verifying Python dependencies..."
python3 -c "import fitz; print(f'[OK] PyMuPDF version: {fitz.__version__}')"
python3 -c "from PIL import Image; import PIL; print(f'[OK] Pillow version: {PIL.__version__}')"

echo "====================================================="
echo "Setup complete! Book Processor is ready to use."
echo "Run the processor with: python3 setup_environment.py"
echo "====================================================="
