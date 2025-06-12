#!/usr/bin/env python3
"""
Book Processor - Main Script

This script automates the workflow of converting djvu/pdf files into organized directories
with PNG and text files, then combining text files into chapters and groups.
"""
import os
import sys
import argparse
import re
import time
import shutil
import zipfile
from pathlib import Path
from datetime import datetime

# Import utility modules
from utils.file_utils import (
    get_platform, normalize_path, ensure_dir, get_basename,
    check_file_exists, check_file_readable, open_file_with_default_app,
    create_project_structure, check_command_exists, create_zip_archive
)
from utils.validation import (
    validate_input_file, validate_page_numbers, validate_pdf_integrity,
    validate_djvu_integrity, parse_user_input
)
from utils.progress import ProgressTracker, StepProgress

# Import processor modules
from processors.converter import FormatConverter
from processors.extractor import PDFExtractor
from processors.ocr import OCRProcessor
from processors.organizer import ChapterOrganizer, CombinedChapterOrganizer


def check_dependencies():
    """
    Check if all required dependencies are installed
    
    Returns:
        tuple: (success, missing_dependencies)
    """
    missing = []
    
    # Check for tesseract
    if not check_command_exists('tesseract'):
        missing.append('tesseract')
    
    # Check for Python libraries
    try:
        import PyPDF2
    except ImportError:
        missing.append('PyPDF2')

    try:
        import fitz  # PyMuPDF
    except ImportError:
        missing.append('PyMuPDF')
    
    return len(missing) == 0, missing


def install_dependencies_guide(missing_dependencies):
    """
    Provide instructions for installing missing dependencies
    
    Args:
        missing_dependencies: List of missing dependencies
        
    Returns:
        str: Installation instructions
    """
    instructions = "To install required dependencies:\n\n"
    
    platform = get_platform()
    
    for dep in missing_dependencies:
        if dep == 'tesseract':
            instructions += "Tesseract OCR Installation:\n"
            if platform == 'windows':
                instructions += "- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki\n"
            elif platform == 'macos':
                instructions += "- macOS: Run 'brew install tesseract'\n"
            else:
                instructions += "- Linux (Debian/Ubuntu): Run 'sudo apt-get install tesseract-ocr'\n"
                instructions += "- Linux (Fedora): Run 'sudo dnf install tesseract'\n"

        elif dep == 'PyPDF2':
            instructions += "PyPDF2 Python Library:\n"
            instructions += "- Run 'pip install PyPDF2'\n"

        elif dep == 'PyMuPDF':
            instructions += "PyMuPDF Library:\n"
            instructions += "- Run 'pip install PyMuPDF'\n"

        instructions += "\n"
    
    return instructions


def prompt_for_input_file():
    """
    Prompt the user for the input file path
    
    Returns:
        tuple: (file_path, file_type)
    """
    # Check if we have a pre-selected file from the environment variable
    env_file_path = os.environ.get("BOOK_PROCESSOR_INPUT_FILE")
    if env_file_path and os.path.exists(env_file_path):
        file_path = env_file_path
        print(f"Using input file from environment: {file_path}")
        
        # Normalize path
        file_path = normalize_path(file_path)
        
        # Validate file
        is_valid, message, file_type = validate_input_file(file_path)
        
        if not is_valid:
            print(f"Error with environment file: {message}")
            print("Falling back to manual input...")
            # Fall back to manual input
            env_file_path = None
        else:
            # Validate file integrity
            if file_type == 'pdf':
                is_valid, message = validate_pdf_integrity(file_path)
            else:  # djvu
                is_valid, message = validate_djvu_integrity(file_path)
            
            if not is_valid:
                print(f"Error with environment file: {message}")
                print("Falling back to manual input...")
                # Fall back to manual input
                env_file_path = None
    
    # If no environment file or it was invalid, prompt manually
    if not env_file_path or not os.path.exists(env_file_path):
        while True:
            file_path = input("Enter the path to the input file (PDF or DJVU): ").strip()
            
            if not file_path:
                print("No file path provided. Please try again.")
                continue
            
            # Strip quotes if they were accidentally included
            if (file_path.startswith('"') and file_path.endswith('"')) or \
               (file_path.startswith('\'') and file_path.endswith('\'')):
                file_path = file_path[1:-1]
                print(f"Note: Quotes removed from path. Using: {file_path}")
            
            # Normalize path
            file_path = normalize_path(file_path)
            
            # Validate file
            is_valid, message, file_type = validate_input_file(file_path)
            
            if not is_valid:
                print(f"Error: {message}")
                continue
            
            # Validate file integrity
            if file_type == 'pdf':
                is_valid, message = validate_pdf_integrity(file_path)
            else:  # djvu
                is_valid, message = validate_djvu_integrity(file_path)
            
            if not is_valid:
                print(f"Error: {message}")
                continue
            
            break
    
    return file_path, file_type


def prompt_for_page_offset():
    """
    Prompt the user for a page offset to handle books with preambles using Roman numerals
    
    Returns:
        int: Page offset value (0 if none)
    """
    while True:
        offset_input = input("Enter page offset for preamble/front matter (0 if none): ").strip()
        
        if not offset_input:
            return 0
        
        try:
            offset = int(offset_input)
            if offset < 0:
                print("Error: Offset must be a non-negative number.")
                continue
            
            if offset > 0:
                print(f"\nPage offset set to {offset}.")
                print(f"This means page 1 in the book will be page {offset+1} in the PDF file.")
                confirm = input("Is this correct? (Y/n): ").strip().lower()
                if confirm in ['', 'y', 'yes']:
                    return offset
                print("Let's try again.")
            else:
                return 0
        except ValueError:
            print("Error: Please enter a valid number.")


def prompt_for_chapter_pages(max_page, page_offset=0):
    """
    Prompt the user for chapter start pages
    
    Args:
        max_page: Maximum page number
        page_offset: Offset for pages with preamble/front matter
        
    Returns:
        list: List of page numbers
    """
    while True:
        if page_offset > 0:
            print(f"\nNote: You've set a page offset of {page_offset}.")
            print(f"When entering page numbers, use the actual book page numbers (1-{max_page-page_offset}).")
            print(f"The system will automatically adjust them to PDF page numbers ({page_offset+1}-{max_page}).\n")
        
        page_input = input(f"Enter chapter start pages (1-{max_page-page_offset}, separated by spaces or commas): ").strip()
        
        if not page_input:
            print("No pages provided. Please try again.")
            continue
        
        # Split input by spaces or commas
        if ',' in page_input:
            pages = [p.strip() for p in page_input.split(',')]
        else:
            pages = [p.strip() for p in page_input.split()]
        
        # Validate page numbers and apply offset
        try:
            # Convert to integers first
            int_pages = [int(p) for p in pages]
            
            # Check range before applying offset
            if any(p < 1 or p > (max_page - page_offset) for p in int_pages):
                print(f"Error: Page numbers must be between 1 and {max_page - page_offset}.")
                continue
                
            # Apply offset
            adjusted_pages = [p + page_offset for p in int_pages]
            
            # Display chapter information with both original and adjusted page numbers
            print("\nChapter Information:")
            for i, (orig_page, adj_page) in enumerate(zip(int_pages, adjusted_pages)):
                print(f"Chapter {i+1}: Starting on book page {orig_page} (PDF page {adj_page})")
            
            # Confirm with user
            confirm = input("\nIs this correct? (Y/n): ").strip().lower()
            if confirm in ['', 'y', 'yes']:
                return adjusted_pages
            
            print("Let's try again.")
        except ValueError:
            print("Error: All page numbers must be integers.")
            continue


def prompt_for_chapter_titles(chapter_count):
    """
    Prompt the user for chapter titles
    
    Args:
        chapter_count: Number of chapters
        
    Returns:
        list: List of chapter titles
    """
    print("\nPlease enter a title for each chapter as it appears in the book's table of contents.")
    print("Press Enter to use default title (Chapter X).\n")
    
    titles = []
    
    for i in range(chapter_count):
        default_title = f"Chapter {i+1}"
        title = input(f"Title for Chapter {i+1}: ").strip()
        
        if not title:
            title = default_title
        
        titles.append(title)
    
    return titles


def prompt_for_chapter_descriptions(chapter_count, titles):
    """
    Prompt the user for chapter descriptions
    
    Args:
        chapter_count: Number of chapters
        titles: List of chapter titles
        
    Returns:
        list: List of chapter descriptions
    """
    print("\nPlease enter a brief description for each chapter (topics, subtopics).")
    print("These will be included in the index. Press Enter to skip.\n")
    
    descriptions = []
    
    for i in range(chapter_count):
        title = titles[i]
        description = input(f"Description for {title}: ").strip()
        descriptions.append(description)
    
    return descriptions


def main():
    """Main function"""
    print("="*80)
    print("Book Processor - Automate Book Processing Workflow")
    print("="*80)
    
    # Check dependencies
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        print("Warning: Some dependencies are missing.")
        print(install_dependencies_guide(missing_deps))
        
        # Ask if user wants to continue
        continue_anyway = input("Continue anyway? (y/N): ").strip().lower()
        if continue_anyway not in ['y', 'yes']:
            print("Exiting.")
            return 1
    
    # Prompt for input file
    input_file, file_type = prompt_for_input_file()
    
    # Get base name and create project structure
    base_name = get_basename(input_file)
    base_dir = os.path.dirname(input_file)
    
    print(f"\nProcessing: {base_name}")
    print(f"File type: {file_type.upper()}")
    
    # Create project structure
    dirs = create_project_structure(base_dir, base_name)
    
    # Initialize workflow steps
    workflow_steps = [
        "Converting DJVU to PDF" if file_type == 'djvu' else "Validating PDF",
        "Extracting PNG images from PDF",
        "Performing OCR on images",
        "Creating chapter files",
        "Creating combined chapter files",
        "Creating final ZIP archive"
    ]
    
    # Initialize step progress tracker
    progress = StepProgress(workflow_steps).start()
    
    # Step 1: Convert DJVU to PDF if needed
    progress.start_step()
    pdf_path = input_file
    
    if file_type == 'djvu':
        converter = FormatConverter()
        pdf_path = os.path.join(dirs['project'], f"{base_name}.pdf")
        
        print(f"Converting DJVU to PDF: {pdf_path}")
        success, message = converter.djvu_to_pdf(input_file, pdf_path)
        
        if not success:
            print(f"Error: {message}")
            return 1
        
        print(message)
    else:
        print(f"Using existing PDF: {pdf_path}")
    
    progress.end_step()
    
    # Open PDF for user reference
    print("\nOpening PDF for reference...")
    open_file_with_default_app(pdf_path)
    
    # Get PDF information
    extractor = PDFExtractor()
    pdf_info = extractor.get_pdf_info(pdf_path)
    
    if pdf_info['page_count'] == 0:
        print("Error: Could not determine PDF page count")
        return 1
    
    print(f"PDF has {pdf_info['page_count']} pages")
    if pdf_info['title']:
        print(f"Title: {pdf_info['title']}")
    if pdf_info['author']:
        print(f"Author: {pdf_info['author']}")
    
    # Prompt for book title if not available
    book_title = pdf_info['title']
    if not book_title:
        book_title = input("\nEnter the book title: ").strip()
        if not book_title:
            book_title = base_name
    
    # Prompt for page offset (for books with preambles using Roman numerals)
    page_offset = prompt_for_page_offset()
    
    # Prompt for chapter start pages (with offset applied)
    chapter_pages = prompt_for_chapter_pages(pdf_info['page_count'], page_offset)
    
    # Prompt for chapter titles
    chapter_titles = prompt_for_chapter_titles(len(chapter_pages))
    
    # Prompt for chapter descriptions
    chapter_descriptions = prompt_for_chapter_descriptions(len(chapter_pages), chapter_titles)
    
    # Step 2: Extract PNG images from PDF
    progress.start_step()
    print(f"\nExtracting PNG images from PDF to {dirs['images']}")
    
    success, message, image_files = extractor.extract_images_parallel(
        pdf_path,
        dirs['images'],
        dpi=300,
        format='png',
        prefix='page',
    )
    
    if not success:
        print(f"Error: {message}")
        return 1
    
    print(message)
    progress.end_step()
    
    # Step 3: Perform OCR on images
    progress.start_step()
    print(f"\nPerforming OCR on images to {dirs['text']}")
    
    ocr = OCRProcessor()
    success, message, text_files = ocr.process_images_parallel(
        image_files, dirs['text'], language='eng', prefix='page'
    )
    
    if not success:
        print(f"Error: {message}")
        return 1
    
    print(message)
    progress.end_step()
    
    # Step 4: Create chapter files
    progress.start_step()
    print(f"\nCreating chapter files in {dirs['chapters']}")
    
    organizer = ChapterOrganizer()
    chapters = organizer.parse_chapter_locations(
        chapter_pages, chapter_titles, pdf_info['page_count'], page_offset
    )
    
    # Add descriptions to chapters
    for i, desc in enumerate(chapter_descriptions):
        if i < len(chapters):
            chapters[i]['description'] = desc
    
    success, message, processed_chapters = organizer.process_chapters(
        chapters, dirs['text'], dirs['chapters']
    )
    
    if not success:
        print(f"Error: {message}")
        return 1
    
    print(message)
    progress.end_step()
    
    # Step 5: Create combined chapter files
    progress.start_step()
    print(f"\nCreating combined chapter files in {dirs['combined']}")
    
    combined_organizer = CombinedChapterOrganizer(max_combined_files=15)
    groups = combined_organizer.optimize_chapter_groups(processed_chapters)
    
    success, message, output_files = combined_organizer.create_combined_files(
        groups, processed_chapters, dirs['chapters'], dirs['combined']
    )
    
    if not success:
        print(f"Error: {message}")
        return 1
    
    print(message)
    
    # Create index file
    print("\nCreating index file")
    success, message, index_path = combined_organizer.create_index_file(
        groups, processed_chapters, dirs['combined'], book_title
    )
    
    if not success:
        print(f"Error: {message}")
        return 1
    
    print(message)
    
    # Create instructions file
    print("\nCreating instructions file")
    success, message, instructions_path = combined_organizer.create_instructions_file(
        dirs['combined'], book_title, len(groups), len(processed_chapters), has_page_offset=(page_offset > 0)
    )
    
    if not success:
        print(f"Error: {message}")
        return 1
    
    print(message)
    progress.end_step()
    
    # Step 6: Create ZIP archive
    progress.start_step()
    print("\nCreating ZIP archive")
    
    # Get list of files to include in ZIP
    files_to_include = []
    for group, path in output_files:
        files_to_include.append(path)
    
    if index_path:
        files_to_include.append(index_path)
    
    if instructions_path:
        files_to_include.append(instructions_path)
    
    # Create ZIP file
    zip_path = os.path.join(dirs['project'], f"{base_name}_combined.zip")
    create_zip_archive(None, zip_path, files_to_include)
    
    print(f"ZIP archive created: {zip_path}")
    progress.end_step()
    
    # Finish workflow
    progress.finish()
    
    print("\nProcessing complete!")
    print(f"Output directory: {dirs['project']}")
    print(f"Combined chapters ZIP: {zip_path}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
