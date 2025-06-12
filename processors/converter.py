"""Converter module for handling file format conversions."""

import os
import sys
import subprocess

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.file_utils import check_command_exists


class FormatConverter:
    """Convert between different document formats."""

    def __init__(self):
        self.has_ddjvu = check_command_exists("ddjvu")

    def check_dependencies(self):
        """Check if required dependencies are installed."""
        if not self.has_ddjvu:
            return False, "ddjvu command not found."
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
        return instructions

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
            result = subprocess.run(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            if result.returncode != 0:
                return False, f"ddjvu failed: {result.stderr.strip()}"

            if not os.path.exists(output_pdf_path):
                return False, "Conversion failed: Output PDF not created"

            return True, f"Successfully converted DJVU to PDF at {output_pdf_path}"
        except Exception as e:
            return False, f"Exception during DJVU to PDF conversion: {str(e)}"

