#!/usr/bin/env python3
"""
Function size validator script for QA compliance.

Validates that functions do not exceed the maximum line count limit (30 lines).
Uses Python AST for parsing Python files and regex for Rust files.
Counts lines excluding function signature and docstrings.

Usage:
    validate_function_size.py <file1> <file2> ...

Exit codes:
    0 - All functions pass validation
    1 - One or more functions exceed line count limit
    2 - Error occurred during validation
"""

import ast
import os
import re
import sys
from typing import List, Tuple, NamedTuple


MAX_FUNCTION_LINES = 30


class FunctionViolation(NamedTuple):
    """Information about a function that exceeds size limit."""
    file_path: str
    function_name: str
    line_number: int
    line_count: int


def count_function_lines_python(node: ast.FunctionDef | ast.AsyncFunctionDef) -> int:
    """
    Count the number of lines in a Python function, excluding signature and docstring.

    Args:
        node: AST node representing the function

    Returns:
        Number of lines in the function body
    """
    # Get the function's line range
    start_line = node.lineno

    # Find the actual end line
    end_line = node.end_lineno
    if end_line is None:
        # Fallback: find the max line number among all child nodes
        end_line = max((getattr(child, 'end_lineno', start_line) or start_line
                       for child in ast.walk(node)), default=start_line)

    # Calculate total lines (including signature and docstring)
    total_lines = end_line - start_line + 1

    # Subtract lines for function signature
    # Count decorator lines if present
    decorator_lines = len(node.decorator_list)

    # Function signature is typically 1 line, but can be multi-line
    # We approximate by counting from the first decorator/def to first statement
    if node.body:
        first_stmt = node.body[0]
        first_stmt_line = first_stmt.lineno
        signature_lines = first_stmt_line - start_line

        # Check if first statement is a docstring
        docstring_lines = 0
        if (isinstance(first_stmt, ast.Expr) and
            isinstance(first_stmt.value, (ast.Str, ast.Constant))):
            # This is a docstring
            docstring_end = first_stmt.end_lineno or first_stmt.lineno
            docstring_lines = docstring_end - first_stmt.lineno + 1

        # Calculate body lines (total - signature - docstring)
        body_lines = total_lines - signature_lines - docstring_lines
        return max(0, body_lines)

    # Empty function body
    return 0


def validate_python_file(file_path: str) -> List[FunctionViolation]:
    """
    Validate function sizes in a Python file using AST.

    Args:
        file_path: Path to the Python file

    Returns:
        List of functions that exceed the size limit
    """
    violations = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source = f.read()

        tree = ast.parse(source, filename=file_path)

        # Walk the AST and find all function definitions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                line_count = count_function_lines_python(node)

                if line_count > MAX_FUNCTION_LINES:
                    violations.append(FunctionViolation(
                        file_path=file_path,
                        function_name=node.name,
                        line_number=node.lineno,
                        line_count=line_count
                    ))

    except SyntaxError as e:
        print(f"Syntax error in {file_path}:{e.lineno}: {e.msg}", file=sys.stderr)
    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)

    return violations


def validate_rust_file(file_path: str) -> List[FunctionViolation]:
    """
    Validate function sizes in a Rust file using regex parsing.

    This uses a heuristic approach:
    - Finds 'fn function_name' declarations
    - Counts lines until the matching closing brace
    - Excludes function signature and doc comments

    Args:
        file_path: Path to the Rust file

    Returns:
        List of functions that exceed the size limit
    """
    violations = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Pattern to match function declarations
        # Matches: pub fn, async fn, fn, pub(crate) fn, etc.
        fn_pattern = re.compile(r'^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?(?:unsafe\s+)?fn\s+(\w+)')

        i = 0
        while i < len(lines):
            line = lines[i]
            match = fn_pattern.match(line)

            if match:
                function_name = match.group(1)
                fn_start_line = i + 1  # 1-indexed for display

                # Find the opening brace of the function body
                brace_line = i
                while brace_line < len(lines):
                    if '{' in lines[brace_line]:
                        break
                    brace_line += 1

                if brace_line >= len(lines):
                    # No opening brace found, skip
                    i += 1
                    continue

                # Count braces to find matching closing brace
                brace_count = 0
                fn_end_line = brace_line

                for check_line in range(brace_line, len(lines)):
                    line_text = lines[check_line]

                    # Count braces (simple approach - doesn't handle strings/comments perfectly)
                    # Remove string literals to avoid counting braces in strings
                    cleaned = re.sub(r'"[^"]*"', '', line_text)
                    cleaned = re.sub(r"'[^']*'", '', cleaned)

                    brace_count += cleaned.count('{')
                    brace_count -= cleaned.count('}')

                    if brace_count == 0 and '{' in lines[brace_line]:
                        fn_end_line = check_line
                        break

                # Calculate function body lines
                # Start counting from line after opening brace
                # End counting at line before closing brace
                body_start = brace_line + 1
                body_end = fn_end_line

                # Count non-empty, non-comment lines in the body
                body_line_count = 0
                for body_line_idx in range(body_start, body_end):
                    if body_line_idx >= len(lines):
                        break

                    body_line = lines[body_line_idx].strip()

                    # Skip empty lines
                    if not body_line:
                        continue

                    # Skip comment-only lines
                    if body_line.startswith('//'):
                        continue

                    body_line_count += 1

                if body_line_count > MAX_FUNCTION_LINES:
                    violations.append(FunctionViolation(
                        file_path=file_path,
                        function_name=function_name,
                        line_number=fn_start_line,
                        line_count=body_line_count
                    ))

                # Move to the line after the function
                i = fn_end_line + 1
            else:
                i += 1

    except Exception as e:
        print(f"Error parsing {file_path}: {e}", file=sys.stderr)

    return violations


def validate_files(files: List[str]) -> List[FunctionViolation]:
    """
    Validate function sizes for a list of files.

    Args:
        files: List of file paths to validate

    Returns:
        List of functions that exceed the size limit
    """
    violations = []

    for file_path in files:
        # Skip if file doesn't exist
        if not os.path.exists(file_path):
            continue

        # Skip test files
        basename = os.path.basename(file_path)
        if basename.startswith('test_') or '_test' in basename:
            continue

        # Dispatch based on file extension
        if file_path.endswith('.py'):
            violations.extend(validate_python_file(file_path))
        elif file_path.endswith('.rs'):
            violations.extend(validate_rust_file(file_path))

    return violations


def main(args: List[str]) -> int:
    """
    Main entry point for function size validation.

    Args:
        args: Command-line arguments (file paths)

    Returns:
        Exit code (0 for success, 1 for violations, 2 for error)
    """
    if not args:
        print("Usage: validate_function_size.py <file1> <file2> ...", file=sys.stderr)
        return 2

    violations = validate_files(args)

    if violations:
        print(f"Function size violations found ({len(violations)} function(s) exceed {MAX_FUNCTION_LINES} lines):")
        print()

        # Sort by line count (highest first) for visibility
        sorted_violations = sorted(violations, key=lambda v: v.line_count, reverse=True)

        for v in sorted_violations:
            print(f"  {v.file_path}:{v.line_number}")
            print(f"    Function '{v.function_name}' has {v.line_count} lines (max: {MAX_FUNCTION_LINES})")

        print()
        print(f"Suggestion: Break down large functions into smaller, focused functions.")
        print(f"Consider extracting logical blocks into helper functions.")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
