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

### DjVuLibre (ddjvu)

1. Download the installer from [DjVuLibre SourceForge](https://sourceforge.net/projects/djvu/)
2. Run the installer and ensure the tools are added to your PATH
3. Verify installation with: `ddjvu --version`

### Calibre (ebook-convert)

1. Download Calibre from [Calibre website](https://calibre-ebook.com/download)
2. Install and ensure `ebook-convert` is added to your PATH
3. Verify installation with: `ebook-convert --version`


## Verifying Installation

After installing all dependencies, run the following commands to verify the tools are installed:

```bash
tesseract --version
ddjvu --version
ebook-convert --version
```

If all commands return version information or help text, the dependencies are correctly installed.

## Python Dependencies

The Book Processor also requires Python dependencies. Install them with:

```bash
pip install PyPDF2 PyMuPDF
```

## Troubleshooting

If you encounter issues with the dependencies:

1. **Command not found**: Make sure the installation directories are in your PATH
2. **Permission denied**: Run the commands with administrator privileges
3. **Missing DLLs**: Reinstall the dependencies and make sure all required files are present
