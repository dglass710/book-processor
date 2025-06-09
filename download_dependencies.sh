#!/bin/bash

# Script to download dependencies for Book Processor

DOWNLOAD_DIR="./dependencies"
mkdir -p "$DOWNLOAD_DIR"

echo "Downloading dependencies for Book Processor..."

# Download Tesseract OCR
echo "Downloading Tesseract OCR..."
curl -L "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe" -o "$DOWNLOAD_DIR/tesseract-installer.exe"

# Download Poppler
echo "Downloading Poppler..."
curl -L "https://github.com/oschwartz10612/poppler-windows/releases/download/v23.11.0-0/Release-23.11.0-0.zip" -o "$DOWNLOAD_DIR/poppler.zip"

# Download DjVuLibre
echo "Downloading DjVuLibre..."
curl -L "https://sourceforge.net/projects/djvu/files/DjVuLibre_Windows/3.5.28/DjVuLibre-3.5.28_DjView-4.12_Setup.exe/download" -o "$DOWNLOAD_DIR/djvulibre-installer.exe"

echo "Downloads complete!"
echo "Please install the dependencies manually:"
echo "1. Run $DOWNLOAD_DIR/tesseract-installer.exe"
echo "2. Extract $DOWNLOAD_DIR/poppler.zip and add the 'bin' directory to your PATH"
echo "3. Run $DOWNLOAD_DIR/djvulibre-installer.exe"
echo ""
echo "After installation, restart your terminal and verify installation with:"
echo "tesseract --version"
echo "pdftoppm -v"
echo "ddjvu --help"
