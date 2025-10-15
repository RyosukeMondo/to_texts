#!/usr/bin/env python3
"""Parse radon JSON output and validate cyclomatic complexity.

This script parses the JSON output from radon cc and identifies functions
with cyclomatic complexity exceeding a specified threshold.

Exit codes:
    0: All functions pass complexity check
    1: One or more functions exceed complexity threshold
    2: Error occurred (invalid JSON, file not found, etc.)
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, TypedDict


class ComplexityViolation(TypedDict):
    """Type definition for complexity violation."""
    function_name: str
    file_path: str
    line_number: int
    complexity: int


def parse_radon_complexity(json_path: Path, threshold: int) -> List[ComplexityViolation]:
    """Parse radon JSON output and find complexity violations.

    Radon JSON format:
    {
        "file_path.py": [
            {
                "type": "function"|"method"|"class",
                "name": "function_name",
                "lineno": 10,
                "col_offset": 0,
                "endline": 20,
                "complexity": 12,
                "rank": "B"
            },
            ...
        ]
    }

    Args:
        json_path: Path to the JSON file containing radon output
        threshold: Maximum allowed cyclomatic complexity

    Returns:
        List of complexity violations found

    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON is malformed
        KeyError: If JSON structure is unexpected
    """
    if not json_path.exists():
        raise FileNotFoundError(f"JSON file not found: {json_path}")

    with open(json_path, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError as e:
            raise json.JSONDecodeError(
                f"Invalid JSON in {json_path}: {e.msg}",
                e.doc,
                e.pos
            )

    violations: List[ComplexityViolation] = []

    # Radon output is a dictionary with file paths as keys
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object at root, got {type(data).__name__}")

    for file_path, functions in data.items():
        if not isinstance(functions, list):
            # Empty file or no functions found - skip
            continue

        for func_data in functions:
            if not isinstance(func_data, dict):
                continue

            # Extract function information
            func_type = func_data.get("type", "")
            func_name = func_data.get("name", "<anonymous>")
            line_number = func_data.get("lineno", 0)
            complexity = func_data.get("complexity", 0)

            # Only check functions and methods (skip classes)
            if func_type in ["function", "method"] and complexity > threshold:
                violations.append({
                    "function_name": func_name,
                    "file_path": file_path,
                    "line_number": line_number,
                    "complexity": int(complexity)
                })

    return violations


def format_violations(violations: List[ComplexityViolation]) -> str:
    """Format violations into a human-readable report.

    Args:
        violations: List of complexity violations

    Returns:
        Formatted string report
    """
    if not violations:
        return "✓ All functions pass complexity check"

    lines = [
        f"\n✗ Found {len(violations)} function(s) exceeding complexity threshold:\n"
    ]

    # Sort by complexity (highest first) for better visibility
    sorted_violations = sorted(violations, key=lambda x: x["complexity"], reverse=True)

    for v in sorted_violations:
        lines.append(
            f"  {v['file_path']}:{v['line_number']} - "
            f"Function '{v['function_name']}' has complexity {v['complexity']}"
        )

    return "\n".join(lines)


def main() -> int:
    """Main entry point for the script.

    Returns:
        Exit code (0=pass, 1=violations, 2=error)
    """
    parser = argparse.ArgumentParser(
        description="Parse radon JSON output and validate cyclomatic complexity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s metrics.json
  %(prog)s metrics.json --threshold 15
  %(prog)s /tmp/python-metrics.json --threshold 8
        """
    )

    parser.add_argument(
        "json_file",
        type=Path,
        help="Path to JSON file containing radon output"
    )

    parser.add_argument(
        "--threshold",
        type=int,
        default=10,
        help="Maximum allowed cyclomatic complexity (default: 10)"
    )

    args = parser.parse_args()

    # Validate threshold
    if args.threshold < 1:
        print(f"Error: Threshold must be positive, got {args.threshold}", file=sys.stderr)
        return 2

    try:
        violations = parse_radon_complexity(args.json_file, args.threshold)
        report = format_violations(violations)
        print(report)

        return 1 if violations else 0

    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except json.JSONDecodeError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 2
    except (ValueError, KeyError) as e:
        print(f"Error parsing JSON structure: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
