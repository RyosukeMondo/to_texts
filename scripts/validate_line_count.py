#!/usr/bin/env python3
"""
Line count validator script for QA compliance.

Validates that files do not exceed the maximum line count limit (400 lines).
Counts non-empty, non-comment lines only.
Excludes test files, generated code, and build artifacts.

Usage:
    validate_line_count.py <file1> <file2> ...

Exit codes:
    0 - All files pass validation
    1 - One or more files exceed line count limit
    2 - Error occurred during validation
"""

import sys
import os
from typing import List, Tuple

MAX_LINES = 400
EXCLUDE_DIR_PATTERNS = [
    'tests/',
    'target/',
    'venv/',
    '.venv/',
    '__pycache__',
    '.egg-info',
    'build/',
    'dist/',
]


def is_excluded(file_path: str) -> bool:
    """
    Check if file should be excluded from validation.

    Args:
        file_path: Path to the file to check

    Returns:
        True if file should be excluded, False otherwise
    """
    # Check if file is in an excluded directory
    for pattern in EXCLUDE_DIR_PATTERNS:
        if pattern in file_path:
            return True

    # Check if filename is a test file
    basename = os.path.basename(file_path)
    if basename.startswith('test_') or basename.endswith('_test.py') or basename.endswith('_test.rs'):
        return True

    return False


def count_lines_python(file_path: str) -> int:
    """
    Count non-empty, non-comment lines in a Python file.

    Args:
        file_path: Path to the Python file

    Returns:
        Number of lines (excluding empty lines and comments)
    """
    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            in_multiline_string = False
            multiline_delimiter = None

            for line in f:
                stripped = line.strip()

                # Handle multiline strings (docstrings)
                if not in_multiline_string:
                    if stripped.startswith('"""') or stripped.startswith("'''"):
                        delimiter = '"""' if '"""' in stripped else "'''"
                        # Check if string starts and ends on same line
                        if stripped.count(delimiter) >= 2:
                            # Single-line docstring, count it
                            if stripped and not stripped.startswith('#'):
                                count += 1
                        else:
                            # Multiline docstring starts
                            in_multiline_string = True
                            multiline_delimiter = delimiter
                            count += 1  # Count the opening line
                        continue
                else:
                    # Inside multiline string
                    count += 1
                    if multiline_delimiter in stripped:
                        in_multiline_string = False
                        multiline_delimiter = None
                    continue

                # Skip empty lines
                if not stripped:
                    continue

                # Skip comment-only lines
                if stripped.startswith('#'):
                    continue

                # Count this line
                count += 1

    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return 0

    return count


def count_lines_rust(file_path: str) -> int:
    """
    Count non-empty, non-comment lines in a Rust file.

    Args:
        file_path: Path to the Rust file

    Returns:
        Number of lines (excluding empty lines and comments)
    """
    count = 0
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            in_multiline_comment = False

            for line in f:
                stripped = line.strip()

                # Handle multiline comments
                if in_multiline_comment:
                    count += 1
                    if '*/' in stripped:
                        in_multiline_comment = False
                    continue

                # Check for start of multiline comment
                if '/*' in stripped:
                    in_multiline_comment = True
                    count += 1
                    # Check if comment ends on same line
                    if '*/' in stripped:
                        in_multiline_comment = False
                    continue

                # Skip empty lines
                if not stripped:
                    continue

                # Skip single-line comment-only lines
                if stripped.startswith('//'):
                    continue

                # Count this line
                count += 1

    except Exception as e:
        print(f"Error reading {file_path}: {e}", file=sys.stderr)
        return 0

    return count


def count_lines(file_path: str) -> int:
    """
    Count non-empty, non-comment lines in a file.

    Dispatches to appropriate counter based on file extension.

    Args:
        file_path: Path to the file

    Returns:
        Number of lines (excluding empty lines and comments)
    """
    if file_path.endswith('.py'):
        return count_lines_python(file_path)
    elif file_path.endswith('.rs'):
        return count_lines_rust(file_path)
    else:
        return 0


def validate_files(files: List[str]) -> List[Tuple[str, int]]:
    """
    Validate line counts for a list of files.

    Args:
        files: List of file paths to validate

    Returns:
        List of (file_path, line_count) tuples for files that exceed the limit
    """
    violations = []

    for file_path in files:
        # Skip if file doesn't exist
        if not os.path.exists(file_path):
            continue

        # Skip excluded files
        if is_excluded(file_path):
            continue

        # Count lines
        count = count_lines(file_path)

        # Check if exceeds limit
        if count > MAX_LINES:
            violations.append((file_path, count))

    return violations


def main(args: List[str]) -> int:
    """
    Main entry point for line count validation.

    Args:
        args: Command-line arguments (file paths)

    Returns:
        Exit code (0 for success, 1 for violations, 2 for error)
    """
    if not args:
        print("Usage: validate_line_count.py <file1> <file2> ...", file=sys.stderr)
        return 2

    violations = validate_files(args)

    if violations:
        print("Line count violations found:")
        for file_path, count in violations:
            print(f"  {file_path}: {count} lines (max: {MAX_LINES})")
        print()
        print(f"Suggestion: Split large files into smaller modules.")
        print(f"Consider extracting classes/functions into separate files.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
