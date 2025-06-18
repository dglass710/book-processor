#!/usr/bin/env python3
"""
Book Processor - Main Script

This script automates the workflow of converting djvu/pdf files into organized directories
with PNG and text files, then combining text files into chapters and groups.
"""
import os
import sys

# Import processor modules
from processors.converter import FormatConverter
from processors.extractor import PDFExtractor
from processors.ocr import OCRProcessor
from processors.organizer import ChapterOrganizer, CombinedChapterOrganizer

# Import utility modules
from utils.file_utils import (
    check_command_exists,
    create_project_structure,
    create_zip_archive,
    get_basename,
    get_platform,
    normalize_path,
    open_file_with_default_app,
)
from utils.progress import StepProgress
from utils.validation import (
    validate_djvu_integrity,
    validate_input_file,
    validate_page_numbers,
    validate_pdf_integrity,
)


def check_dependencies():
    """
    Check if all required dependencies are installed

    Returns:
        tuple: (success, missing_dependencies)
    """
    print("Checking for required dependencies...")
    missing = []

    # Check for tesseract
    if not check_command_exists("tesseract"):
        missing.append("tesseract")

    # Check for djvulibre (ddjvu)
    if not check_command_exists("ddjvu"):
        missing.append("ddjvu")

    # Check for Calibre's ebook-convert
    if not check_command_exists("ebook-convert"):
        missing.append("ebook-convert")

    # Check for Python libraries
    try:
        import PyPDF2  # noqa: F401
    except ImportError:
        missing.append("PyPDF2")

    try:
        import fitz  # noqa: F401
    except ImportError:
        missing.append("PyMuPDF")

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
        if dep == "tesseract":
            instructions += "Tesseract OCR Installation:\n"
            if platform == "windows":
                instructions += "- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki\n"
            elif platform == "macos":
                instructions += "- macOS: Run 'brew install tesseract'\n"
            else:
                instructions += "- Linux (Debian/Ubuntu): Run 'sudo apt-get install tesseract-ocr'\n"
                instructions += "- Linux (Fedora): Run 'sudo dnf install tesseract'\n"

        elif dep == "ddjvu":
            instructions += "DjVuLibre Installation (ddjvu):\n"
            if platform == "windows":
                instructions += (
                    "- Windows: Download from https://sourceforge.net/projects/djvu/\n"
                )
            elif platform == "macos":
                instructions += "- macOS: Run 'brew install djvulibre'\n"
            else:
                instructions += "- Linux (Debian/Ubuntu): Run 'sudo apt-get install djvulibre-bin'\n"
                instructions += "- Linux (Fedora): Run 'sudo dnf install djvulibre'\n"

        elif dep == "PyPDF2":
            instructions += "PyPDF2 Python Library:\n"
            instructions += "- Run 'pip install PyPDF2'\n"

        elif dep == "PyMuPDF":
            instructions += "PyMuPDF Library:\n"
            instructions += "- Run 'pip install PyMuPDF'\n"

        elif dep == "ebook-convert":
            instructions += "Calibre (ebook-convert) Installation:\n"
            instructions += (
                "- Visit https://calibre-ebook.com/download to install Calibre\n"
            )

        instructions += "\n"

    return instructions


def prompt_for_input_file():
    """
    Prompt the user for the input file path

    Returns:
        tuple: (file_path, file_type)
    """
    # Initialize variables to avoid unbound errors
    file_path = None
    file_type = None

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
            file_path = None  # Reset file_path to force manual input
            file_type = None
            env_file_path = None
        else:
            # Validate file integrity
            if file_type == "pdf":
                is_valid, message = validate_pdf_integrity(file_path)
            elif file_type == "djvu":
                is_valid, message = validate_djvu_integrity(file_path)
            else:
                is_valid, message = True, ""

            if not is_valid:
                print(f"Error with environment file: {message}")
                print("Falling back to manual input...")
                # Fall back to manual input
                file_path = None  # Reset file_path to force manual input
                file_type = None
                env_file_path = None

    # If no environment file or it was invalid, prompt manually
    if file_path is None or file_type is None:
        while True:
            file_path = input(
                "Enter the path to the input file (PDF, DJVU, EPUB, or MOBI): "
            ).strip()

            if not file_path:
                print("No file path provided. Please try again.")
                continue

            # Strip quotes if they were accidentally included
            if (file_path.startswith('"') and file_path.endswith('"')) or (
                file_path.startswith("'") and file_path.endswith("'")
            ):
                file_path = file_path[1:-1]
                print(f"Note: Quotes removed from path. Using: {file_path}")

            # Normalize path
            file_path = normalize_path(file_path)

            # Validate file
            is_valid, message, file_type = validate_input_file(file_path)

            if not is_valid:
                print("Error: {}".format(message))
                continue

            # Validate file integrity
            if file_type == "pdf":
                is_valid, message = validate_pdf_integrity(file_path)
            elif file_type == "djvu":
                is_valid, message = validate_djvu_integrity(file_path)
            else:
                is_valid, message = True, ""

            if not is_valid:
                print("Error: {}".format(message))
                continue

            break

    # At this point, file_path and file_type should be set properly
    if file_path is None or file_type is None:
        raise ValueError("Failed to get valid file path and type")

    return file_path, file_type


def prompt_for_page_offset():
    """
    Prompt the user for a page offset to handle books with preambles using Roman numerals

    Returns:
        int: Page offset value (0 if none)
    """
    while True:
        offset_input = input(
            "Enter page offset for preamble/front matter (0 if none): "
        ).strip()

        if not offset_input:
            return 0

        try:
            offset = int(offset_input)
            if offset < 0:
                print("Error: Offset must be a non-negative number.")
                continue

            if offset > 0:
                print(f"\nPage offset set to {offset}.")
                print(
                    f"This means page 1 in the book will be page {offset+1} in the PDF file."
                )
                confirm = input("Is this correct? (Y/n): ").strip().lower()
                if confirm in ["", "y", "yes"]:
                    return offset
                print("Let's try again.")
            else:
                return 0
        except ValueError:
            print("Error: Please enter a valid number.")


def prompt_for_chapter_pages(max_page, page_offset=0):
    """
    Prompt the user for chapter start pages and last chapter end page

    Args:
        max_page: Maximum page number
        page_offset: Offset for pages with preamble/front matter

    Returns:
        tuple: (list of start pages, last chapter end page)
    """
    while True:
        # If there's a page offset, explain the numbering system
        if page_offset > 0:
            print("\nNote: This book uses two page numbering systems:")
            print(f"- Book pages: 1-{max_page-page_offset}")
            print(f"- PDF pages: {page_offset+1}-{max_page}")
            print(
                f"When entering page numbers, use the actual book page numbers (1-{max_page-page_offset})."
            )
            print(
                f"The system will automatically adjust them to PDF page numbers ({page_offset+1}-{max_page}).\n"
            )

        # Get chapter start pages
        page_input = input(
            f"Enter chapter start pages (1-{max_page-page_offset}, separated by spaces or commas): "
        ).strip()

        if not page_input:
            print("No pages provided. Please try again.")
            continue

        try:
            # Split input by spaces and/or commas
            pages = [p.strip() for p in page_input.replace(",", " ").split()]
            int_pages = [int(p) for p in pages]

            # Validate page numbers
            if not validate_page_numbers(int_pages, 1, max_page - page_offset):
                print(
                    f"Invalid page numbers. Please enter numbers between 1 and {max_page-page_offset} in ascending order."
                )
                continue

            # Calculate PDF page numbers if there's an offset
            adjusted_pages = [
                p + page_offset if page_offset > 0 else p for p in int_pages
            ]

            # Display chapter information
            print("\nChapter Information:")
            for i, (orig_page, adj_page) in enumerate(zip(int_pages, adjusted_pages)):
                print(
                    f"Chapter {i+1}: Starting on book page {orig_page} (PDF page {adj_page})"
                )

            # Confirm chapter pages
            confirm = (
                input("\nAre these chapter start pages correct? (y/n): ")
                .strip()
                .lower()
            )
            if confirm != "y":
                continue

            # Get last chapter end page
            while True:
                last_page_input = input(
                    f"\nEnter the last page of the final chapter (1-{max_page-page_offset}): "
                ).strip()
                try:
                    last_page = int(last_page_input)
                    if last_page <= int_pages[-1]:
                        print("Last page must be after the start of the last chapter.")
                        continue
                    if not validate_page_numbers(
                        [last_page], int_pages[-1] + 1, max_page - page_offset
                    ):
                        print(
                            f"Invalid page number. Please enter a number between {int_pages[-1] + 1} and {max_page-page_offset}."
                        )
                        continue
                    return int_pages, last_page
                except ValueError:
                    print("Invalid input. Please enter a number.")

        except ValueError:
            print("Invalid input. Please enter numbers only.")
            continue


def prompt_for_chapter_titles(chapter_count):
    """
    Prompt the user for chapter titles

    Args:
        chapter_count: Number of chapters

    Returns:
        list: List of chapter titles
    """
    print(
        "\nPlease enter a title for each chapter as it appears in the book's table of contents."
    )
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
    print("\nPlease enter a brief description for each section (topics, subtopics).")
    print("Press Enter to skip.\n")

    descriptions = []

    # Handle all titles
    for i, title in enumerate(titles):
        description = input(
            f"Description for {title if title is not None else f'Chapter {i + 1}'}: "
        ).strip()
        descriptions.append(description)

    return descriptions


def main():
    """Main function"""
    print("=" * 80)
    print("Book Processor - Automate Book Processing Workflow")
    print("=" * 80)

    # Check dependencies
    deps_ok, missing_deps = check_dependencies()
    if not deps_ok:
        print("Warning: Some dependencies are missing.")
        print(install_dependencies_guide(missing_deps))

        # Ask if user wants to continue
        continue_anyway = input("Continue anyway? (y/N): ").strip().lower()
        if continue_anyway not in ["y", "yes"]:
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

    # Initialize workflow steps based on file type
    if file_type == "djvu":
        workflow_steps = [
            "Converting DJVU to PDF",
            "Extracting PNG images from PDF",
            "Performing OCR on images",
            "Creating chapter files",
            "Creating combined chapter files",
            "Creating final ZIP archive",
        ]
    elif file_type in ["epub", "mobi"]:
        workflow_steps = [
            "Converting ebook to PDF",
            "Extracting text from PDF",
            "Creating chapter files",
            "Creating combined chapter files",
            "Creating final ZIP archive",
        ]
    else:
        workflow_steps = [
            "Validating PDF",
            "Extracting PNG images from PDF",
            "Performing OCR on images",
            "Creating chapter files",
            "Creating combined chapter files",
            "Creating final ZIP archive",
        ]

    # Initialize step progress tracker
    progress = StepProgress(workflow_steps).start()

    # Step 1: Convert to PDF if needed
    progress.start_step()
    pdf_path = input_file

    if file_type == "djvu":
        converter = FormatConverter()
        pdf_path = os.path.join(dirs["project"], f"{base_name}.pdf")

        print(f"Converting DJVU to PDF: {pdf_path}")
        success, message = converter.djvu_to_pdf(input_file, pdf_path)

        if not success:
            print("Error: {}".format(message))
            return 1

        print(message)
    elif file_type in ["epub", "mobi"]:
        converter = FormatConverter()
        pdf_path = os.path.join(dirs["project"], f"{base_name}.pdf")
        print(f"Converting ebook to PDF: {pdf_path}")
        success, message = converter.ebook_to_pdf(input_file, pdf_path)

        if not success:
            print("Error: {}".format(message))
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

    if pdf_info["page_count"] == 0:
        print("Error: Could not determine PDF page count")
        return 1

    print(f"PDF has {pdf_info['page_count']} pages")
    if pdf_info["title"]:
        print(f"Title: {pdf_info['title']}")
    if pdf_info["author"]:
        print(f"Author: {pdf_info['author']}")

    # Prompt for book title if not available
    book_title = pdf_info["title"]
    if not book_title:
        book_title = input("\nEnter the book title: ").strip()
        if not book_title:
            book_title = base_name

    # Prompt for page offset (for books with preambles using Roman numerals)
    page_offset = prompt_for_page_offset()

    # Prompt for chapter start pages and last chapter end page (with offset applied)
    chapter_pages, last_chapter_end = prompt_for_chapter_pages(
        pdf_info["page_count"], page_offset
    )

    # Prompt for chapter titles
    chapter_titles = prompt_for_chapter_titles(len(chapter_pages))

    # Prompt for chapter descriptions
    chapter_descriptions = prompt_for_chapter_descriptions(
        len(chapter_pages), chapter_titles
    )

    # Step 2: Extract content from PDF
    progress.start_step()
    if file_type in ["epub", "mobi"]:
        print(f"\nExtracting text from PDF to {dirs['text']}")
        success, message, text_files = extractor.extract_text_per_page(
            pdf_path,
            dirs["text"],
            prefix="page",
        )
        image_files = []
    else:
        print(f"\nExtracting PNG images from PDF to {dirs['images']}")

        success, message, image_files = extractor.extract_images_parallel(
            pdf_path,
            dirs["images"],
            dpi=300,
            format="png",
            prefix="page",
        )

    if not success:
        print(f"Error: {message}")
        return 1

    print(message)
    progress.end_step()

    # Step 3: Perform OCR on images (skip for digital text)
    if file_type not in ["epub", "mobi"]:
        progress.start_step()
        print(f"\nPerforming OCR on images to {dirs['text']}")

        ocr = OCRProcessor()
        success, message, text_files = ocr.process_images_parallel(
            image_files, dirs["text"], language="eng", prefix="page"
        )

        if not success:
            print("Error: {}".format(message))
            return 1

        print(message)
        progress.end_step()

    # Step 4: Create chapter files
    progress.start_step()
    print(f"\nCreating chapter files in {dirs['chapters']}")

    organizer = ChapterOrganizer()
    chapters = organizer.parse_chapter_locations(
        chapter_pages, chapter_titles, last_chapter_end + 1, page_offset
    )

    # Add descriptions to chapters
    for i, desc in enumerate(chapter_descriptions):
        if i < len(chapters):
            chapters[i]["description"] = desc

    success, message, processed_chapters = organizer.process_chapters(
        chapters, dirs["text"], dirs["chapters"]
    )

    if not success:
        print(f"Error: {message}")
        return 1

    print(message)
    progress.end_step()

    # Step 5: Create combined chapter files
    progress.start_step()
    print(f"\nCreating combined chapter files in {dirs['combined']}")

    combined_organizer = CombinedChapterOrganizer()
    groups = combined_organizer.optimize_chapter_groups(processed_chapters)

    success, message, output_files = combined_organizer.create_combined_files(
        groups, processed_chapters, dirs["chapters"], dirs["combined"]
    )

    if not success:
        print(f"Error: {message}")
        return 1

    print(message)

    # Create index file
    print("\nCreating index file")
    success, message, index_path = combined_organizer.create_index_file(
        groups, processed_chapters, dirs["combined"], book_title
    )

    if not success:
        print(f"Error: {message}")
        return 1

    print(message)

    # Create instructions file
    print("\nCreating instructions file")
    success, message, instructions_path = combined_organizer.create_instructions_file(
        dirs["combined"],
        book_title,
        len(groups),
        len(processed_chapters),
        has_page_offset=(page_offset > 0),
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
    zip_path = os.path.join(dirs["project"], f"{base_name}_combined.zip")
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
