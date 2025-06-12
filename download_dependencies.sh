#!/bin/bash

# Script to download dependencies for Book Processor

DOWNLOAD_DIR="./dependencies"
mkdir -p "$DOWNLOAD_DIR"

echo "Downloading dependencies for Book Processor..."

# Download Tesseract OCR
echo "Downloading Tesseract OCR..."
curl -L "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe" -o "$DOWNLOAD_DIR/tesseract-installer.exe"

# Download DjVuLibre
echo "Downloading DjVuLibre..."
curl -L "https://downloads.sourceforge.net/project/djvu/DjVuLibre/3.5.28/DjVuLibre-3.5.28.exe" -o "$DOWNLOAD_DIR/djvulibre-installer.exe"


echo "Downloads complete!"
echo "Please install the dependencies manually:"
echo "1. Run $DOWNLOAD_DIR/tesseract-installer.exe"
echo "2. Run $DOWNLOAD_DIR/djvulibre-installer.exe"
echo ""
echo "After installation, restart your terminal and verify installation with:"
echo "tesseract --version"
echo "ddjvu --version"
echo ""
