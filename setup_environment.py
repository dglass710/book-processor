#!/usr/bin/env python3
"""
Setup Environment for Book Processor

This script sets up the environment by adding necessary tools to PATH
and then runs the book processor.
"""
import os
import sys
import subprocess

def check_dependency(name, command):
    """Check if a dependency is available in the PATH."""
    try:
        # Different commands have different version flags
        version_flags = ["--version", "-v"]
        
        # Try each version flag
        for flag in version_flags:
            try:
                result = subprocess.run([command, flag], 
                                      stdout=subprocess.PIPE, 
                                      stderr=subprocess.PIPE, 
                                      text=True,
                                      timeout=5)
                if result.returncode == 0:
                    print(f"[OK] {name} is available: {result.stdout.strip() or result.stderr.strip()}")
                    return True
            except (subprocess.TimeoutExpired, subprocess.SubprocessError):
                continue
        
        # If we get here, none of the version flags worked, but the command exists
        # Let's try just running the command without arguments
        try:
            result = subprocess.run([command], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE, 
                                  text=True,
                                  timeout=1)
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
    
    # Add Tesseract to PATH if it exists
    tesseract_path = r"C:\Program Files\Tesseract-OCR"
    if os.path.exists(tesseract_path):
        print(f"Found Tesseract at {tesseract_path}")
        os.environ["PATH"] = tesseract_path + os.pathsep + os.environ.get("PATH", "")
        print("Added Tesseract to PATH")
    else:
        print(f"Tesseract not found at {tesseract_path}")
        print("Please install Tesseract from https://github.com/UB-Mannheim/tesseract/wiki")
    
    # Verify dependencies
    print("\nVerifying dependencies:")
    tesseract_ok = check_dependency("Tesseract", "tesseract")
    
    if not tesseract_ok:
        print("\nTesseract is missing or not working properly.")
        print("Would you like to continue anyway? (y/N)")
        response = input().strip().lower()
        if response != 'y':
            print("Exiting setup. Please install the missing dependencies and try again.")
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
