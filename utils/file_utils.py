"""
File utility functions for handling paths, file operations, and cross-platform compatibility
"""

import os
import platform
import subprocess
from pathlib import Path


def get_platform():
    """Return the current platform: 'windows', 'macos', or 'linux'"""
    system = platform.system().lower()
    if system == "darwin":
        return "macos"
    elif system == "windows":
        return "windows"
    else:
        return "linux"


def normalize_path(path):
    """Convert a path to the correct format for the current OS"""
    return str(Path(path))


def ensure_dir(directory):
    """Create a directory if it doesn't exist"""
    os.makedirs(directory, exist_ok=True)
    return directory


def get_basename(filepath, with_extension=False):
    """Extract the basename from a filepath"""
    basename = os.path.basename(filepath)
    if not with_extension:
        basename = os.path.splitext(basename)[0]
    return basename


def check_file_exists(filepath):
    """Check if a file exists and is a file (not a directory)"""
    return os.path.isfile(filepath)


def check_file_readable(filepath):
    """Check if a file exists and is readable"""
    return os.path.isfile(filepath) and os.access(filepath, os.R_OK)


def open_file_with_default_app(filepath):
    """Open a file with the default application based on platform"""
    filepath = normalize_path(filepath)

    try:
        if get_platform() == "windows":
            subprocess.run(["cmd", "/c", "start", "", filepath], check=True)
        elif get_platform() == "macos":
            subprocess.call(["open", filepath])
        else:  # linux
            subprocess.call(["xdg-open", filepath])
        return True
    except Exception as e:
        print(f"Error opening file: {e}")
        return False


def create_project_structure(base_dir, book_name):
    """Create the directory structure for processing a book

    If the target directory already exists, create a new one with an incremented
    number suffix (e.g., 'Book Name (1)', 'Book Name (2)', etc.)
    """
    # Create main project directory with unique name
    original_project_dir = os.path.join(base_dir, book_name)
    project_dir = original_project_dir

    # If directory exists, create a new one with incremented number suffix
    counter = 1
    while os.path.exists(project_dir):
        project_dir = os.path.join(base_dir, f"{book_name} ({counter})")
        counter += 1

    # Now create the unique directory
    os.makedirs(project_dir, exist_ok=False)  # Use False here since we know it doesn't exist
    print(f"Creating project directory: {project_dir}")

    # Create subdirectories
    images_dir = ensure_dir(os.path.join(project_dir, "images"))
    text_dir = ensure_dir(os.path.join(project_dir, "text"))
    chapters_dir = ensure_dir(os.path.join(project_dir, "chapters"))
    combined_dir = ensure_dir(os.path.join(project_dir, "combined"))

    return {
        "project": project_dir,
        "images": images_dir,
        "text": text_dir,
        "chapters": chapters_dir,
        "combined": combined_dir,
    }


def check_command_exists(command):
    """Check if a command exists in the system path"""
    try:
        if get_platform() == "windows":
            # On Windows, use where command
            result = subprocess.run(
                ["where", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        else:
            # On Unix-like systems, use which command
            result = subprocess.run(
                ["which", command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )
        return result.returncode == 0
    except Exception:
        return False


def create_zip_archive(source_dir, output_file, files_to_include=None):
    """Create a zip archive of specified files or an entire directory"""
    import zipfile

    with zipfile.ZipFile(output_file, "w", zipfile.ZIP_DEFLATED) as zipf:
        if files_to_include:
            for file in files_to_include:
                if os.path.isfile(file):
                    arcname = os.path.basename(file)
                    zipf.write(file, arcname)
        else:
            for root, _, files in os.walk(source_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    zipf.write(file_path, arcname)

    return output_file
