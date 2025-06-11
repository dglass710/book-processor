"""
OCR module for extracting text from images
"""
import os
import subprocess
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import sys

# Add parent directory to path to allow imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))  
from utils.file_utils import check_command_exists
from utils.progress import ProgressTracker


def _process_batch_worker(args):
    """Process a batch of images in a single worker."""
    batch, language, config = args
    proc = OCRProcessor()
    processed = []
    failed = []
    for image_path, output_path in batch:
        success, message = proc.process_image(image_path, output_path, language, config)
        if success:
            processed.append(f"{output_path}.txt")
        else:
            failed.append((image_path, message))
    return processed, failed


class OCRProcessor:
    """
    Process images with OCR to extract text
    """
    def __init__(self):
        self.has_tesseract = check_command_exists('tesseract')
    
    def check_dependencies(self):
        """
        Check if required dependencies are installed
        
        Returns:
            tuple: (success, message)
        """
        if not self.has_tesseract:
            return False, "Tesseract OCR not found. Cannot perform OCR."
        return True, "OCR dependencies found."
    
    def install_dependencies_guide(self):
        """
        Provide instructions for installing missing dependencies
        
        Returns:
            str: Installation instructions
        """
        instructions = "To install required dependencies:\n\n"
        
        if not self.has_tesseract:
            instructions += "Tesseract OCR Installation:\n"
            instructions += "- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki\n"
            instructions += "- macOS: Run 'brew install tesseract'\n"
            instructions += "- Linux (Debian/Ubuntu): Run 'sudo apt-get install tesseract-ocr'\n"
            instructions += "- Linux (Fedora): Run 'sudo dnf install tesseract'\n\n"
            instructions += "After installation, ensure tesseract is in your PATH.\n"
        
        return instructions
    
    def get_tesseract_version(self):
        """
        Get the installed Tesseract version
        
        Returns:
            str: Tesseract version or None if not found
        """
        if not self.has_tesseract:
            return None
        
        try:
            result = subprocess.run(
                ['tesseract', '--version'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode == 0:
                # Extract version from the first line
                first_line = result.stdout.strip().split('\n')[0]
                if 'tesseract' in first_line.lower():
                    return first_line
            
            return None
        except Exception:
            return None
    
    def get_available_languages(self):
        """
        Get list of available OCR languages
        
        Returns:
            list: Available language codes
        """
        if not self.has_tesseract:
            return []
        
        try:
            result = subprocess.run(
                ['tesseract', '--list-langs'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            # Tesseract outputs languages to stderr
            output = result.stderr if result.stderr else result.stdout
            
            # Parse languages (skip the first line which is a header)
            lines = output.strip().split('\n')
            if len(lines) > 1:
                return [lang.strip() for lang in lines[1:]]
            
            return []
        except Exception:
            return []
    
    def process_image(self, image_path, output_path, language='eng', config=''):
        """
        Process a single image with OCR
        
        Args:
            image_path: Path to the image file
            output_path: Path where the text will be saved (without extension)
            language: OCR language
            config: Additional tesseract configuration
            
        Returns:
            tuple: (success, message)
        """
        if not self.has_tesseract:
            return False, "Tesseract OCR not found"
        
        try:
            # Build command
            cmd = ['tesseract', image_path, output_path, '-l', language]
            
            # Add config if provided
            if config:
                cmd.extend(['--psm', config])
            
            # Run OCR
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                return False, f"OCR failed: {result.stderr}"
            
            # Tesseract automatically adds .txt extension
            expected_output = f"{output_path}.txt"
            if not os.path.exists(expected_output):
                return False, "OCR completed but output file not found"
            
            return True, f"OCR completed successfully: {expected_output}"
        
        except Exception as e:
            return False, f"Exception during OCR: {str(e)}"
    
    def process_images(self, image_paths, output_dir, language='eng', config='', prefix='page'):
        """
        Process multiple images sequentially with OCR
        
        Args:
            image_paths: List of paths to image files
            output_dir: Directory to save text files
            language: OCR language
            config: Additional tesseract configuration
            prefix: Filename prefix for output files
            
        Returns:
            tuple: (success, message, processed_files)
        """
        if not self.has_tesseract:
            return False, "Tesseract OCR not found", []
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        processed_files = []
        failed_files = []
        
        # Start progress tracker
        progress = ProgressTracker(len(image_paths), "Processing OCR").start()
        
        for i, image_path in enumerate(image_paths):
            # Generate output filename without extension
            # Extract page number from filename if possible
            try:
                # Try to extract page number from filename (assuming format like page-001.png)
                filename = os.path.basename(image_path)
                name_parts = os.path.splitext(filename)[0].split('-')
                if len(name_parts) > 1 and name_parts[-1].isdigit():
                    page_num = int(name_parts[-1])
                    output_filename = f"{prefix}-{page_num:03d}"
                else:
                    # Fall back to using index
                    output_filename = f"{prefix}-{i+1:03d}"
            except Exception:
                # Fall back to using index
                output_filename = f"{prefix}-{i+1:03d}"
            
            output_path = os.path.join(output_dir, output_filename)
            
            # Process the image
            success, message = self.process_image(image_path, output_path, language, config)
            
            if success:
                processed_files.append(f"{output_path}.txt")
            else:
                failed_files.append((image_path, message))
            
            # Update progress
            progress.update()
        
        progress.finish()
        
        # Report results
        if failed_files:
            failures = len(failed_files)
            return (
                len(processed_files) > 0,
                f"OCR completed with {failures} failures out of {len(image_paths)} images",
                processed_files
            )
        
        return True, f"OCR completed successfully for all {len(image_paths)} images", processed_files

    def process_images_parallel(self, image_paths, output_dir, language='eng', config='', prefix='page', max_workers=None):
        """Process multiple images in parallel using batches."""
        if not self.has_tesseract:
            return False, "Tesseract OCR not found", []

        if max_workers is None:
            max_workers = os.cpu_count() or 1

        os.makedirs(output_dir, exist_ok=True)

        # Pre-compute output filenames and pair them with input images
        pairs = []
        for i, image_path in enumerate(image_paths):
            try:
                filename = os.path.basename(image_path)
                name_parts = os.path.splitext(filename)[0].split('-')
                if len(name_parts) > 1 and name_parts[-1].isdigit():
                    page_num = int(name_parts[-1])
                    output_filename = f"{prefix}-{page_num:03d}"
                else:
                    output_filename = f"{prefix}-{i+1:03d}"
            except Exception:
                output_filename = f"{prefix}-{i+1:03d}"

            output_path = os.path.join(output_dir, output_filename)
            pairs.append((image_path, output_path))

        total_pages = len(pairs)
        max_workers = min(max_workers, total_pages)
        pages_per_worker = total_pages // max_workers
        remainder = total_pages % max_workers

        batches = []
        start = 0
        for i in range(max_workers):
            extra = 1 if i < remainder else 0
            end = start + pages_per_worker + extra
            if start < end:
                batches.append(pairs[start:end])
            start = end

        processed_files = []
        failed_files = []
        progress = ProgressTracker(total_pages, "Processing OCR").start()

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            futures = {
                executor.submit(_process_batch_worker, (batch, language, config)): len(batch)
                for batch in batches
            }
            for future in as_completed(futures):
                proc_files, errors = future.result()
                processed_files.extend(proc_files)
                failed_files.extend(errors)
                for _ in range(len(proc_files) + len(errors)):
                    progress.update()

        progress.finish()

        if failed_files:
            failures = len(failed_files)
            return (
                len(processed_files) > 0,
                f"OCR completed with {failures} failures out of {total_pages} images",
                processed_files,
            )

        return True, f"OCR completed successfully for all {total_pages} images", processed_files
