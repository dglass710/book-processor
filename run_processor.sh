#!/bin/bash

# Add Poppler to PATH
export PATH="$HOME/poppler/poppler-23.11.0/Library/bin:$PATH"

# Check if dependencies are available
echo "Checking dependencies..."

# Check Poppler
if command -v pdftoppm &> /dev/null; then
    echo "✓ Poppler is installed: $(pdftoppm -v 2>&1 | head -n 1)"
else
    echo "✗ Poppler is not installed or not in PATH"
    echo "  Make sure to extract the poppler.zip file and add the bin directory to your PATH"
fi

# Check Tesseract
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract is installed: $(tesseract --version 2>&1 | head -n 1)"
else
    echo "✗ Tesseract is not installed or not in PATH"
    echo "  Please run the tesseract-installer.exe and ensure you add it to your PATH"
fi

# Check DjVuLibre
if command -v ddjvu &> /dev/null; then
    echo "✓ DjVuLibre is installed"
else
    echo "✗ DjVuLibre is not installed or not in PATH"
    echo "  Please run the djvulibre-installer.exe and ensure you add it to your PATH"
fi

echo ""
echo "Running Book Processor..."
echo ""

# Run the Python script
python main.py
