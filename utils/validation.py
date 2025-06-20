"""
Validation utilities for user input and file integrity
"""

import os

from .file_utils import check_file_exists, check_file_readable


def validate_input_file(filepath):
    """
    Validate that the input file exists, is readable, and has the correct extension

    Returns:
        tuple: (is_valid, message, file_type)
    """
    if not filepath:
        return False, "No file path provided", None

    if not check_file_exists(filepath):
        return False, f"File does not exist: {filepath}", None

    if not check_file_readable(filepath):
        return False, f"File exists but is not readable: {filepath}", None

    # Check file extension
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()

    if ext not in [".pdf", ".djvu", ".epub", ".mobi"]:
        return (
            False,
            f"Unsupported file format: {ext}. Only .pdf, .djvu, .epub and .mobi are supported.",
            None,
        )

    # Remove the dot from extension
    file_type = ext[1:]

    return True, "File is valid", file_type


def validate_page_numbers(page_numbers, min_page=1, max_pages=None):
    """
    Validate that page numbers are valid integers in ascending order

    Args:
        page_numbers: List of page numbers as strings or integers
        min_page: Minimum allowed page number (default: 1)
        max_pages: Maximum page number allowed (optional)

    Returns:
        bool: True if valid, False if not
    """
    if not page_numbers:
        return False

    try:
        # Convert to integers if they're strings
        parsed_numbers = [int(str(num).strip()) for num in page_numbers]

        # Check range
        for num in parsed_numbers:
            if num < min_page:
                return False
            if max_pages and num > max_pages:
                return False

        # Check if numbers are in ascending order
        for i in range(1, len(parsed_numbers)):
            if parsed_numbers[i] <= parsed_numbers[i - 1]:
                return False

        return True
    except ValueError:
        return False


def validate_pdf_integrity(pdf_path):
    """
    Check if a PDF file is valid and not corrupted

    Returns:
        tuple: (is_valid, message)
    """
    try:
        # Try to import PyPDF2
        import PyPDF2

        # Try to open and read the PDF
        with open(pdf_path, "rb") as f:
            try:
                pdf = PyPDF2.PdfReader(f)
                num_pages = len(pdf.pages)
                return True, f"PDF is valid with {num_pages} pages"
            except Exception as e:
                return False, f"PDF appears to be corrupt: {str(e)}"
    except ImportError:
        # If PyPDF2 is not available, try a simpler check
        if os.path.getsize(pdf_path) < 100:  # Extremely small files are suspicious
            return False, "PDF file is suspiciously small and may be corrupt"
        return True, "PDF exists but could not verify integrity (PyPDF2 not installed)"


def validate_djvu_integrity(djvu_path):
    """Check if a DJVU file is valid using djvused"""
    import os
    import subprocess

    # Check if the file exists first
    if not os.path.exists(djvu_path):
        return False, f"DJVU file does not exist: {djvu_path}"

    # Try to find djvused in common locations
    djvused_paths = [
        "djvused",  # Try from PATH first
        os.path.join(r"C:\Program Files\DjVuLibre", "djvused.exe"),
        os.path.join(r"C:\Program Files (x86)\DjVuLibre", "djvused.exe"),
        os.path.join(r"C:\Program Files\DjVuLibre\bin", "djvused.exe"),
        os.path.join(r"C:\Program Files (x86)\DjVuLibre\bin", "djvused.exe"),
    ]

    djvused_exe = None
    for path in djvused_paths:
        try:
            if path == "djvused" or os.path.exists(path):
                djvused_exe = path
                break
        except Exception:
            continue

    if not djvused_exe:
        return False, "Could not find djvused executable. Please install DjVuLibre."

    try:
        # Run djvused to get page count
        result = subprocess.run(
            [djvused_exe, "-e", "n", djvu_path],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )

        if result.returncode == 0:
            try:
                page_count = int(result.stdout.strip())
                return True, f"DJVU is valid with {page_count} pages"
            except ValueError:
                return True, "DJVU file is valid (page count unknown)"
        else:
            error_msg = result.stderr.strip() if result.stderr else "Unknown error"
            return False, f"DJVU validation failed: {error_msg}"
    except subprocess.SubprocessError as e:
        return False, f"Could not validate file integrity: {str(e)}"
    except OSError as e:
        return False, f"An OS-related error occurred: {str(e)}"
    except Exception as e:
        return False, f"An unexpected error occurred: {str(e)}"


def parse_user_input(prompt, validation_func=None, default=None, attempts=3):
    """
    Prompt the user for input with validation

    Args:
        prompt: The prompt to display to the user
        validation_func: A function that takes the input and returns (is_valid, message)
        default: Default value if user enters nothing
        attempts: Number of attempts before giving up

    Returns:
        The validated input or None if validation failed
    """
    for i in range(attempts):
        if default:
            user_input = input(f"{prompt} [{default}]: ").strip()
            if not user_input and default:
                user_input = default
        else:
            user_input = input(f"{prompt}: ").strip()

        if validation_func:
            is_valid, message, result = validation_func(user_input)
            if is_valid:
                return result
            print("Error: {}".format(message))
        else:
            return user_input

    print(f"Failed to get valid input after {attempts} attempts")
    return None
