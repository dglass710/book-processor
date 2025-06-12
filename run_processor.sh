#!/bin/bash


# Check if dependencies are available
echo "Checking dependencies..."

# Check Tesseract
if command -v tesseract &> /dev/null; then
    echo "✓ Tesseract is installed: $(tesseract --version 2>&1 | head -n 1)"
else
    echo "✗ Tesseract is not installed or not in PATH"
    echo "  Please run the tesseract-installer.exe and ensure you add it to your PATH"
fi

# Check ddjvu
if command -v ddjvu &> /dev/null; then
    echo "✓ ddjvu is installed: $(ddjvu --version 2>&1 | head -n 1)"
else
    echo "✗ ddjvu is not installed or not in PATH"
    echo "  Please install DjVuLibre and ensure ddjvu is available"
fi


echo ""
echo "Running Book Processor..."
echo ""

# Run the Python script
python main.py
