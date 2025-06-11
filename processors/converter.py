"""
Converter module for handling file format conversions
"""
import os
import sys
import fitz  # PyMuPDF

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class FormatConverter:
    """
    Convert between different document formats
    """
    def __init__(self):
        try:
            import fitz  # noqa: F401
            self.has_pymupdf = True
        except Exception:
            self.has_pymupdf = False
    
    def check_dependencies(self):
        """
        Check if required dependencies are installed
        
        Returns:
            tuple: (success, message)
        """
        if not self.has_pymupdf:
            return False, "PyMuPDF (fitz) not installed."
        return True, "All dependencies found."
    
    def install_dependencies_guide(self):
        """
        Provide instructions for installing missing dependencies
        
        Returns:
            str: Installation instructions
        """
        instructions = "To install required dependencies:\n\n"
        
        if not self.has_pymupdf:
            instructions += "PyMuPDF Installation:\n"
            instructions += "- Run 'pip install PyMuPDF'\n\n"
        
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
        if not self.has_pymupdf:
            return False, "PyMuPDF not available. Cannot convert DJVU to PDF."
        
        try:
            doc = fitz.open(djvu_path)
            doc.save(output_pdf_path)
            doc.close()
            if not os.path.exists(output_pdf_path):
                return False, "Conversion failed: Output PDF not created"

            return True, f"Successfully converted DJVU to PDF at {output_pdf_path}"
        
        except Exception as e:
            return False, f"Exception during DJVU to PDF conversion: {str(e)}"
