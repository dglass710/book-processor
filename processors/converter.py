"""Converter module for handling file format conversions."""

import os
import subprocess
import sys

# Import utility modules
from utils.file_utils import check_command_exists

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


class FormatConverter:
    """Convert between different document formats."""

    def __init__(self):
        self.has_ddjvu = check_command_exists("ddjvu")
        self.has_ebook_convert = check_command_exists("ebook-convert")

    def check_dependencies(self):
        """Check if required dependencies are installed."""
        if not self.has_ddjvu and not self.has_ebook_convert:
            return False, "ddjvu or ebook-convert command not found."
        if not self.has_ddjvu:
            return False, "ddjvu command not found."
        if not self.has_ebook_convert:
            return False, "ebook-convert command not found."
        return True, "All dependencies found."

    def install_dependencies_guide(self):
        """Provide instructions for installing missing dependencies."""
        instructions = "To install required dependencies:\n\n"
        if not self.has_ddjvu:
            instructions += "DjVuLibre Installation (provides ddjvu):\n"
            instructions += "- Windows: https://sourceforge.net/projects/djvu/files/\n"
            instructions += "- macOS: Run 'brew install djvulibre'\n"
            instructions += "- Linux (Debian/Ubuntu): Run 'sudo apt-get install djvulibre-bin'\n"
            instructions += "- Linux (Fedora): Run 'sudo dnf install djvulibre'\n\n"
        if not self.has_ebook_convert:
            instructions += "Calibre Installation (provides ebook-convert):\n"
            instructions += "- Visit https://calibre-ebook.com/download to download and install Calibre\n\n"
        return instructions

    def ebook_to_pdf(self, ebook_path, output_pdf_path):
        """Convert an EPUB or MOBI file to PDF using ebook-convert."""
        if not self.has_ebook_convert:
            return (
                False,
                "ebook-convert command not available. Cannot convert ebook to PDF.",
            )

        try:
            cmd = ["ebook-convert", ebook_path, output_pdf_path]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                return False, f"ebook-convert failed: {result.stderr.strip()}"

            if not os.path.exists(output_pdf_path):
                return False, "Conversion failed: Output PDF not created"

            return True, f"Successfully converted ebook to PDF at {output_pdf_path}"
        except Exception as e:
            return False, f"Exception during ebook to PDF conversion: {str(e)}"

    def djvu_to_pdf(self, djvu_path, output_pdf_path, quality=50):
        """Convert a DJVU file to PDF using the ddjvu command."""
        if not self.has_ddjvu:
            return False, "ddjvu command not available. Cannot convert DJVU to PDF."

        try:
            cmd = [
                "ddjvu",
                "-format=pdf",
                f"-quality={quality}",
                djvu_path,
                output_pdf_path,
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode != 0:
                return False, f"ddjvu failed: {result.stderr.strip()}"

            if not os.path.exists(output_pdf_path):
                return False, "Conversion failed: Output PDF not created"

            return True, f"Successfully converted DJVU to PDF at {output_pdf_path}"
        except Exception as e:
            return False, f"Exception during DJVU to PDF conversion: {str(e)}"
