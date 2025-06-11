"""
Extractor module for converting PDF pages to images
"""
import os
import sys
import fitz  # PyMuPDF
import PyPDF2

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.progress import ProgressTracker


class PDFExtractor:
    """
    Extract images from PDF files
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
            return False, "PyMuPDF not installed. Cannot extract images from PDF."
        return True, "PDF extraction dependencies found."
    
    def install_dependencies_guide(self):
        """
        Provide instructions for installing missing dependencies
        
        Returns:
            str: Installation instructions
        """
        instructions = "To install required dependencies:\n\n"
        
        if not self.has_pymupdf:
            instructions += "PyMuPDF Installation:\n"
            instructions += "Run 'pip install PyMuPDF'\n\n"
        
        return instructions
    
    def get_pdf_info(self, pdf_path):
        """
        Get information about a PDF file
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            dict: PDF information including page count
        """
        try:
            with open(pdf_path, 'rb') as f:
                pdf = PyPDF2.PdfReader(f)
                num_pages = len(pdf.pages)
                
                # Try to get metadata
                info = pdf.metadata
                title = info.title if info and hasattr(info, 'title') else None
                author = info.author if info and hasattr(info, 'author') else None
                
                return {
                    'page_count': num_pages,
                    'title': title,
                    'author': author
                }
        except Exception as e:
            return {
                'page_count': 0,
                'title': None,
                'author': None,
                'error': str(e)
            }
    
    def extract_images_with_pymupdf(self, pdf_path, output_dir, dpi=300, format='png', prefix='page'):
        """Extract images from PDF using PyMuPDF"""
        if not self.has_pymupdf:
            return False, "PyMuPDF not available", []

        try:
            pdf_info = self.get_pdf_info(pdf_path)
            if pdf_info['page_count'] == 0:
                return False, "Could not determine PDF page count", []

            os.makedirs(output_dir, exist_ok=True)

            progress = ProgressTracker(pdf_info['page_count'], "Extracting PDF pages").start()

            extracted_files = []
            doc = fitz.open(pdf_path)

            for i in range(doc.page_count):
                expected_file = os.path.join(output_dir, f"{prefix}-{i+1:03d}.{format}")

                if os.path.exists(expected_file):
                    extracted_files.append(expected_file)
                    progress.update(len(extracted_files))
                    continue

                page = doc.load_page(i)
                pix = page.get_pixmap(dpi=dpi)
                pix.save(expected_file)
                extracted_files.append(expected_file)
                progress.update(len(extracted_files))

            doc.close()
            progress.finish()

            if not extracted_files:
                return False, "No images were extracted", []

            return True, f"Successfully extracted {len(extracted_files)} images", extracted_files

        except Exception as e:
            return False, f"Exception during image extraction: {str(e)}", []
    
    def extract_images(self, pdf_path, output_dir, dpi=300, format='png', prefix='page'):
        """
        Extract images from PDF using the best available method
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save extracted images
            dpi: Resolution in dots per inch
            format: Output image format (png, jpg, etc.)
            prefix: Filename prefix for extracted images
            
        Returns:
            tuple: (success, message, extracted_files)
        """
        return self.extract_images_with_pymupdf(pdf_path, output_dir, dpi, format, prefix)
