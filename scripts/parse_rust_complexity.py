#!/usr/bin/env python3
"""Parse rust-code-analysis JSON output and validate cyclomatic complexity.

This script parses the JSON output from rust-code-analysis-cli and identifies
functions with cyclomatic complexity exceeding a specified threshold.

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


class FunctionMetrics(TypedDict):
    """Type definition for function metrics."""
    name: str
    file_path: str
    start_line: int
    cyclomatic: int


class ComplexityViolation(TypedDict):
    """Type definition for complexity violation."""
    function_name: str
    file_path: str
    line_number: int
    complexity: int


def extract_function_metrics(
    data: Dict[str, Any], file_path: str, threshold: int
) -> List[FunctionMetrics]:
    """Extract function metrics from rust-code-analysis JSON data.

    Args:
        data: Parsed JSON data from rust-code-analysis
        file_path: Path to the source file being analyzed
        threshold: Complexity threshold to check against

    Returns:
        List of function metrics that exceed the threshold
    """
    violations: List[FunctionMetrics] = []

    def traverse_metrics(node: Dict[str, Any], current_file: str) -> None:
        """Recursively traverse the metrics tree to find functions."""
        if not isinstance(node, dict):
            return

        # Check if this is a function/method node
        kind = node.get("kind")
        if kind in ["function", "method", "closure"]:
            metrics = node.get("metrics", {})
            cyclomatic = metrics.get("cyclomatic", {})

            # Get cyclomatic complexity value
            complexity_value = cyclomatic.get("sum", 0)

            if complexity_value > threshold:
                name = node.get("name", "<anonymous>")
                start_line = node.get("start_line", 0)

                violations.append({
                    "name": name,
                    "file_path": current_file,
                    "start_line": start_line,
                    "cyclomatic": int(complexity_value)
                })

        # Recursively process children
        spaces = node.get("spaces", [])
        if isinstance(spaces, list):
            for child in spaces:
                traverse_metrics(child, current_file)

    # Start traversal from root
    traverse_metrics(data, file_path)

    return violations


def parse_rust_complexity(json_path: Path, threshold: int) -> List[ComplexityViolation]:
    """Parse rust-code-analysis JSON output and find complexity violations.

    Args:
        json_path: Path to the JSON file containing rust-code-analysis output
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

    # rust-code-analysis output is a dictionary with file paths as keys
    if not isinstance(data, dict):
        raise ValueError(f"Expected JSON object at root, got {type(data).__name__}")

    for file_path, file_data in data.items():
        if not isinstance(file_data, dict):
            continue

        # Extract function metrics from the file's data
        function_violations = extract_function_metrics(file_data, file_path, threshold)

        # Convert to ComplexityViolation format
        for func in function_violations:
            violations.append({
                "function_name": func["name"],
                "file_path": func["file_path"],
                "line_number": func["start_line"],
                "complexity": func["cyclomatic"]
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
        description="Parse rust-code-analysis JSON output and validate cyclomatic complexity",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s metrics.json
  %(prog)s metrics.json --threshold 15
  %(prog)s /tmp/rust-metrics.json --threshold 8
        """
    )

    parser.add_argument(
        "json_file",
        type=Path,
        help="Path to JSON file containing rust-code-analysis output"
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
        violations = parse_rust_complexity(args.json_file, args.threshold)
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
