"""
Converter module for handling file format conversions
"""
import os
import subprocess
import shutil
from ..utils.file_utils import check_command_exists


class FormatConverter:
    """
    Convert between different document formats
    """
    def __init__(self):
        self.has_djvulibre = check_command_exists('djvulibre') or check_command_exists('ddjvu')
        self.ddjvu_command = 'ddjvu' if check_command_exists('ddjvu') else 'djvulibre-bin'
    
    def check_dependencies(self):
        """
        Check if required dependencies are installed
        
        Returns:
            tuple: (success, message)
        """
        if not self.has_djvulibre:
            return False, "djvulibre not found. Please install djvulibre package."
        return True, "All dependencies found."
    
    def install_dependencies_guide(self):
        """
        Provide instructions for installing missing dependencies
        
        Returns:
            str: Installation instructions
        """
        instructions = "To install required dependencies:\n\n"
        
        if not self.has_djvulibre:
            instructions += "DjVuLibre Installation:\n"
            instructions += "- Windows: Download from https://sourceforge.net/projects/djvu/files/DjVuLibre_Windows/\n"
            instructions += "- macOS: Run 'brew install djvulibre'\n"
            instructions += "- Linux (Debian/Ubuntu): Run 'sudo apt-get install djvulibre-bin'\n"
            instructions += "- Linux (Fedora): Run 'sudo dnf install djvulibre'\n\n"
        
        return instructions
    
    def djvu_to_pdf(self, djvu_path, output_pdf_path, quality=50):
        """
        Convert DJVU file to PDF
        
        Args:
            djvu_path: Path to the DJVU file
            output_pdf_path: Path where the PDF will be saved
            quality: Output quality (1-100)
            
        Returns:
            tuple: (success, message)
        """
        if not self.has_djvulibre:
            return False, "djvulibre not found. Cannot convert DJVU to PDF."
        
        try:
            # Ensure quality is within range
            quality = max(1, min(100, quality))
            
            # Run the conversion command
            cmd = [self.ddjvu_command, '-format=pdf', f'-quality={quality}', djvu_path, output_pdf_path]
            
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return False, f"Error converting DJVU to PDF: {result.stderr}"
            
            if not os.path.exists(output_pdf_path):
                return False, "Conversion failed: Output PDF not created"
            
            return True, f"Successfully converted DJVU to PDF at {output_pdf_path}"
        
        except Exception as e:
            return False, f"Exception during DJVU to PDF conversion: {str(e)}"
