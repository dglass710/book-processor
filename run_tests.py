#!/usr/bin/env python3
"""
Run all tests and code quality checks for the book-processor project.
"""

import os
import subprocess
import sys
from typing import List, Tuple


def run_command(command: List[str], description: str) -> Tuple[bool, str]:
    """Run a command and return its success status and output."""
    print(f"\nRunning {description}...")
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=True,
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        return False, f"Failed with error:\n{e.stdout}\n{e.stderr}"


def main() -> int:
    """Run all tests and checks."""
    # Change to repository root directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    # Define all checks to run
    checks = [
        (["isort", ".", "--check-only"], "isort check"),
        (["black", "--check", "."], "black check"),
        (["flake8"], "flake8 check"),
        (["pyright"], "pyright type check"),
        ([sys.executable, "-m", "pytest", "tests/"], "pytest unit tests"),
    ]

    # Track overall success
    all_passed = True
    results = []

    # Run each check
    for command, description in checks:
        success, output = run_command(command, description)
        all_passed &= success
        results.append((description, success, output))

    # Print summary
    print("\n" + "=" * 40)
    print("Test Summary:")
    print("=" * 40)
    for description, success, output in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} - {description}")
        if not success:
            print(f"Details:\n{output}\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
