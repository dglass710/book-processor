"""
Extractor module for converting PDF pages to images
"""
import os
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
import fitz  # PyMuPDF
import PyPDF2

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.progress import ProgressTracker


def _extract_page_worker(args):
    """Helper function to extract a single page as an image."""
    pdf_path, page_num, output_dir, dpi, fmt, prefix = args
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_num)
        pix = page.get_pixmap(dpi=dpi)
        output_file = os.path.join(
            output_dir, f"{prefix}-{page_num + 1:03d}.{fmt}"
        )
        pix.save(output_file)
        doc.close()
        return page_num, output_file, True, ""
    except Exception as e:
        return page_num, None, False, str(e)

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

    def extract_images_parallel(
        self,
        pdf_path,
        output_dir,
        dpi=300,
        format='png',
        prefix='page',
        max_workers=None,
    ):
        """Extract images from PDF using multiple CPU cores."""
        if not self.has_pymupdf:
            return False, "PyMuPDF not available", []

        pdf_info = self.get_pdf_info(pdf_path)
        if pdf_info['page_count'] == 0:
            return False, "Could not determine PDF page count", []

        os.makedirs(output_dir, exist_ok=True)

        total_pages = pdf_info['page_count']
        extracted_files = []
        failed_tasks = []
        tasks = []

        progress = ProgressTracker(total_pages, "Extracting PDF pages").start()

        for i in range(total_pages):
            expected_file = os.path.join(output_dir, f"{prefix}-{i+1:03d}.{format}")
            if os.path.exists(expected_file):
                extracted_files.append(expected_file)
                progress.update(len(extracted_files))
            else:
                tasks.append((pdf_path, i, output_dir, dpi, format, prefix))

        completed = len(extracted_files)
        if tasks:
            with ProcessPoolExecutor(max_workers=max_workers) as executor:
                future_to_task = {executor.submit(_extract_page_worker, t): t for t in tasks}
                for future in as_completed(future_to_task):
                    page_num, output_file, success, error = future.result()
                    completed += 1
                    if success:
                        extracted_files.append(output_file)
                    else:
                        failed_tasks.append((page_num, error))
                    progress.update(completed)

        progress.finish()

        extracted_files.sort()

        if failed_tasks:
            failures = len(failed_tasks)
            return (
                len(extracted_files) > 0,
                f"Extraction completed with {failures} failures out of {total_pages} pages",
                extracted_files,
            )

        return True, f"Successfully extracted {len(extracted_files)} images", extracted_files
    
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
        return self.extract_images_parallel(pdf_path, output_dir, dpi, format, prefix)

    def extract_text_per_page(self, pdf_path, output_dir, prefix='page'):
        """Extract text from each PDF page using PyMuPDF."""
        if not self.has_pymupdf:
            return False, "PyMuPDF not available", []

        pdf_info = self.get_pdf_info(pdf_path)
        if pdf_info['page_count'] == 0:
            return False, "Could not determine PDF page count", []

        os.makedirs(output_dir, exist_ok=True)

        doc = fitz.open(pdf_path)
        progress = ProgressTracker(doc.page_count, "Extracting PDF text").start()

        output_files = []
        for i in range(doc.page_count):
            page = doc.load_page(i)
            text = page.get_text()
            output_file = os.path.join(output_dir, f"{prefix}-{i+1:03d}.txt")
            with open(output_file, "w", encoding="utf-8") as f:
                f.write(text)
            output_files.append(output_file)
            progress.update(i + 1)

        doc.close()
        progress.finish()

        return True, f"Successfully extracted text from {len(output_files)} pages", output_files
