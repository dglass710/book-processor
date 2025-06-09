# Installation Guide for Book Processor

This guide provides instructions for installing the required dependencies for the Book Processor tool.

## Method 1: Using Chocolatey (Recommended for Windows)

If you have Chocolatey installed, you can install all dependencies with administrator privileges:

1. Right-click on `install_dependencies.bat` and select "Run as administrator"
2. Follow the prompts to install all dependencies
3. Restart your command prompt to ensure PATH is updated

## Method 2: Manual Installation

### Tesseract OCR

1. Download the installer from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and make sure to check "Add to PATH" during installation
3. Verify installation by opening a new command prompt and typing: `tesseract --version`

### Poppler Utils

1. Download the latest release from [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/)
2. Extract the ZIP file to a location on your computer (e.g., `C:\Program Files\poppler`)
3. Add the `bin` directory to your PATH:
   - Search for "Environment Variables" in Windows search
   - Click "Edit the system environment variables"
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add the path to the bin directory (e.g., `C:\Program Files\poppler\bin`)
   - Click "OK" on all dialogs
4. Verify installation by opening a new command prompt and typing: `pdftoppm -v`

### DjVuLibre

1. Download the installer from [DjVuLibre SourceForge](https://sourceforge.net/projects/djvu/files/DjVuLibre_Windows/)
2. Run the installer
3. Add the installation directory to your PATH (similar to Poppler)
4. Verify installation by opening a new command prompt and typing: `ddjvu --help`

## Verifying Installation

After installing all dependencies, run the following commands to verify they are properly installed:

```bash
tesseract --version
pdftoppm -v
ddjvu --help
```

If all commands return version information or help text, the dependencies are correctly installed.

## Python Dependencies

The Book Processor also requires Python dependencies. Install them with:

```bash
pip install PyPDF2 pdf2image
```

## Troubleshooting

If you encounter issues with the dependencies:

1. **Command not found**: Make sure the installation directories are in your PATH
2. **Permission denied**: Run the commands with administrator privileges
3. **Missing DLLs**: Reinstall the dependencies and make sure all required files are present
