"""
Extractor module for converting PDF pages to images
"""
import os
import subprocess
from pathlib import Path
import PyPDF2
from ..utils.file_utils import check_command_exists
from ..utils.progress import ProgressTracker


class PDFExtractor:
    """
    Extract images from PDF files
    """
    def __init__(self):
        # Check for poppler tools
        self.has_pdftoppm = check_command_exists('pdftoppm')
        self.has_pdfimages = check_command_exists('pdfimages')
        
        # Check for pdf2image library
        try:
            import pdf2image
            self.has_pdf2image = True
        except ImportError:
            self.has_pdf2image = False
    
    def check_dependencies(self):
        """
        Check if required dependencies are installed
        
        Returns:
            tuple: (success, message)
        """
        if not (self.has_pdftoppm or self.has_pdf2image):
            return False, "Neither pdftoppm nor pdf2image found. Cannot extract images from PDF."
        return True, "PDF extraction dependencies found."
    
    def install_dependencies_guide(self):
        """
        Provide instructions for installing missing dependencies
        
        Returns:
            str: Installation instructions
        """
        instructions = "To install required dependencies:\n\n"
        
        if not self.has_pdftoppm:
            instructions += "Poppler Utils Installation:\n"
            instructions += "- Windows: Download from http://blog.alivate.com.au/poppler-windows/\n"
            instructions += "- macOS: Run 'brew install poppler'\n"
            instructions += "- Linux (Debian/Ubuntu): Run 'sudo apt-get install poppler-utils'\n"
            instructions += "- Linux (Fedora): Run 'sudo dnf install poppler-utils'\n\n"
        
        if not self.has_pdf2image:
            instructions += "pdf2image Python Library:\n"
            instructions += "Run 'pip install pdf2image'\n\n"
        
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
    
    def extract_images_with_poppler(self, pdf_path, output_dir, dpi=300, format='png', prefix='page'):
        """
        Extract images from PDF using poppler tools
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save extracted images
            dpi: Resolution in dots per inch
            format: Output image format (png, jpg, etc.)
            prefix: Filename prefix for extracted images
            
        Returns:
            tuple: (success, message, extracted_files)
        """
        if not self.has_pdftoppm:
            return False, "pdftoppm not found", []
        
        try:
            # Get page count for progress tracking
            pdf_info = self.get_pdf_info(pdf_path)
            if pdf_info['page_count'] == 0:
                return False, "Could not determine PDF page count", []
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Prepare the command
            cmd = [
                'pdftoppm',
                '-' + format,  # Output format
                f'-r{dpi}',    # Resolution
                pdf_path,      # Input PDF
                os.path.join(output_dir, prefix)  # Output prefix
            ]
            
            # Start progress tracker
            progress = ProgressTracker(pdf_info['page_count'], "Extracting PDF pages").start()
            
            # Instead of running all at once, process page by page to show progress
            extracted_files = []
            
            for i in range(1, pdf_info['page_count'] + 1):
                # Poppler names files with 1-based index
                expected_file = os.path.join(output_dir, f"{prefix}-{i:03d}.{format}")
                
                # Skip if file already exists
                if os.path.exists(expected_file):
                    extracted_files.append(expected_file)
                    progress.update(len(extracted_files))
                    continue
                
                # Process just this page
                page_cmd = cmd + ['-f', str(i), '-l', str(i)]
                
                result = subprocess.run(
                    page_cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    check=False
                )
                
                if result.returncode != 0:
                    print(f"Warning: Error processing page {i}: {result.stderr}")
                    continue
                
                # Check if file was created
                if os.path.exists(expected_file):
                    extracted_files.append(expected_file)
                    progress.update(len(extracted_files))
            
            progress.finish()
            
            if not extracted_files:
                return False, "No images were extracted", []
            
            return True, f"Successfully extracted {len(extracted_files)} images", extracted_files
        
        except Exception as e:
            return False, f"Exception during image extraction: {str(e)}", []
    
    def extract_images_with_pdf2image(self, pdf_path, output_dir, dpi=300, format='png', prefix='page'):
        """
        Extract images from PDF using pdf2image library
        
        Args:
            pdf_path: Path to the PDF file
            output_dir: Directory to save extracted images
            dpi: Resolution in dots per inch
            format: Output image format (png, jpg, etc.)
            prefix: Filename prefix for extracted images
            
        Returns:
            tuple: (success, message, extracted_files)
        """
        if not self.has_pdf2image:
            return False, "pdf2image library not found", []
        
        try:
            from pdf2image import convert_from_path
            
            # Get page count for progress tracking
            pdf_info = self.get_pdf_info(pdf_path)
            if pdf_info['page_count'] == 0:
                return False, "Could not determine PDF page count", []
            
            # Create output directory if it doesn't exist
            os.makedirs(output_dir, exist_ok=True)
            
            # Start progress tracker
            progress = ProgressTracker(pdf_info['page_count'], "Extracting PDF pages").start()
            
            # Convert PDF to images
            images = convert_from_path(
                pdf_path,
                dpi=dpi,
                fmt=format,
                output_folder=output_dir,
                output_file=prefix,
                paths_only=True
            )
            
            # Update progress
            progress.update(len(images), force=True)
            progress.finish()
            
            if not images:
                return False, "No images were extracted", []
            
            return True, f"Successfully extracted {len(images)} images", images
        
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
        # Try pdf2image first if available
        if self.has_pdf2image:
            success, message, files = self.extract_images_with_pdf2image(
                pdf_path, output_dir, dpi, format, prefix
            )
            if success:
                return success, message, files
        
        # Fall back to pdftoppm
        if self.has_pdftoppm:
            return self.extract_images_with_poppler(
                pdf_path, output_dir, dpi, format, prefix
            )
        
        return False, "No PDF extraction methods available", []
