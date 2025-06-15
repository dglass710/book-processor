#!/usr/bin/env python3
"""
Setup Environment for Book Processor

This script sets up the environment by adding necessary tools to PATH
and then runs the book processor.
"""
import os
import subprocess
import sys


def check_dependency(name, command):
    """Check if a dependency is available in the PATH."""
    try:
        # Different commands have different version flags
        version_flags = ["--version", "-v"]

        # Try each version flag
        for flag in version_flags:
            try:
                result = subprocess.run(
                    [command, flag],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=5,
                )
                if result.returncode == 0:
                    print(
                        f"[OK] {name} is available: {result.stdout.strip() or result.stderr.strip()}"
                    )
                    return True
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                continue

        # If we get here, none of the version flags worked, but the command exists
        # Let's try just running the command without arguments
        try:
            result = subprocess.run(
                [command],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=1,
            )
            print(f"[OK] {name} exists but version info not available")
            return True
        except (subprocess.TimeoutExpired, subprocess.SubprocessError):
            pass

        print(f"✗ {name} is not working properly")
        return False
    except FileNotFoundError:
        print(f"✗ {name} is not found in PATH")
        return False


def main():
    """Setup environment and run book processor."""
    print("=" * 80)
    print("Setting up environment for Book Processor")
    print("=" * 80)

    # Find and add Tesseract to PATH
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR",
        r"C:\Program Files (x86)\Tesseract-OCR",
    ]
    tesseract_found = False
    for tesseract_path in tesseract_paths:
        if os.path.exists(tesseract_path):
            print(f"Found Tesseract at {tesseract_path}")
            os.environ["PATH"] = (
                tesseract_path + os.pathsep + os.environ.get("PATH", "")
            )
            print("Added Tesseract to PATH")
            tesseract_found = True
            break

    if not tesseract_found:
        print("Tesseract not found in standard locations")
        print(
            "Please install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki"
        )

    # Find and add DjVuLibre to PATH
    djvulibre_paths = [
        r"C:\Program Files\DjVuLibre",
        r"C:\Program Files (x86)\DjVuLibre",
    ]
    djvulibre_found = False
    for djvu_path in djvulibre_paths:
        if os.path.exists(djvu_path):
            print(f"Found DjVuLibre at {djvu_path}")
            os.environ["PATH"] = djvu_path + os.pathsep + os.environ.get("PATH", "")
            print("Added DjVuLibre to PATH")
            djvulibre_found = True
            break

    if not djvulibre_found:
        print("DjVuLibre not found in standard locations")
        print(
            "Please install DjVuLibre from https://sourceforge.net/projects/djvu/files/DjVuLibre_Windows/"
        )

    # Verify dependencies
    print("\nVerifying dependencies:")
    tesseract_ok = check_dependency("Tesseract", "tesseract")

    # Check for DjVuLibre tools - try both djvused and ddjvu
    djvused_ok = check_dependency("djvused", "djvused")
    if not djvused_ok:
        # Only check ddjvu if djvused is not available
        check_dependency("ddjvu", "ddjvu")
    else:
        # If djvused is available, we don't need to check ddjvu
        print("[INFO] djvused is available, skipping ddjvu check")

    djvulibre_ok = djvused_ok  # Consider DjVuLibre OK if djvused works (primary tool)

    if not tesseract_ok or not djvulibre_ok:
        print("\nSome dependencies are missing or not working properly.")
        print("Would you like to continue anyway? (y/N)")
        response = input().strip().lower()
        if response != "y":
            print(
                "Exiting setup. Please install the missing dependencies and try again."
            )
            return 1

    # Run the book processor
    print("\nRunning book processor...")

    # Add the parent directory to the Python path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, current_dir)

    # Import the main function directly
    from main import main as run_processor

    # Check if we have a pre-selected PDF file
    input_file = os.environ.get("BOOK_PROCESSOR_INPUT_FILE")
    if input_file and os.path.exists(input_file):
        print(f"Using pre-selected input file: {input_file}")
        # We need to modify the main function to accept an input file parameter
        # For now, we'll set an environment variable that the main function can check
        os.environ["BOOK_PROCESSOR_INPUT_FILE"] = input_file

    # Run the main function
    return run_processor()


if __name__ == "__main__":
    sys.exit(main())
