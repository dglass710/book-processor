#!/bin/bash

# Script to download dependencies for Book Processor

DOWNLOAD_DIR="./dependencies"
mkdir -p "$DOWNLOAD_DIR"

echo "Downloading dependencies for Book Processor..."

# Download Tesseract OCR
echo "Downloading Tesseract OCR..."
curl -L "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe" -o "$DOWNLOAD_DIR/tesseract-installer.exe"


echo "Downloads complete!"
echo "Please install the dependencies manually:"
echo "1. Run $DOWNLOAD_DIR/tesseract-installer.exe"
echo ""
echo "After installation, restart your terminal and verify installation with:"
echo "tesseract --version"
echo ""
