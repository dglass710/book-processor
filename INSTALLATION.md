# Installation Guide for Book Processor

Follow these steps to install the external tools and Python packages required to run the Book Processor. Helper scripts are provided for each platform.

## Windows

1. Install [Chocolatey](https://chocolatey.org/) if it's not already available.
2. Right-click `install_dependencies.bat` and choose **Run as administrator** to install Tesseract, DjVuLibre and Calibre.
3. Restart your command prompt so the updated `PATH` is used.

You can also install the tools manually from their websites:

- **Tesseract OCR** – [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
- **DjVuLibre** – [SourceForge page](https://sourceforge.net/projects/djvu/)
- **Calibre (ebook-convert)** – [Calibre download](https://calibre-ebook.com/download)

## macOS

Run the included script to install the dependencies with Homebrew:

```bash
./setup_mac.sh
```

## Linux

For Debian/Ubuntu systems run:

```bash
sudo ./setup_linux.sh
```

For Fedora based systems run:

```bash
sudo ./setup_fedora.sh
```

## Python Packages

Install the Python requirements with:

```bash
pip install -r requirements.txt
```

The setup scripts also install the development tools used by `run_tests.py` (pyright, flake8, black, isort and pytest).

## Verifying the Installation

Check that the external commands are available:

```bash
tesseract --version
ddjvu --version
ebook-convert --version
```

Then run the test suite to ensure everything works:

```bash
python run_tests.py
```

All checks should pass without errors.

## Troubleshooting

- **Command not found** – confirm the installation directories are in your `PATH`.
- **Permission denied** – run the commands with administrator/root privileges.
- **Missing libraries** – reinstall the dependencies to make sure all files are present.
