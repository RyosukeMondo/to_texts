#!/usr/bin/env python3
"""Tests for parse_rust_complexity.py script."""

import json
import sys
import tempfile
from pathlib import Path

# Add scripts directory to path so we can import the module
sys.path.insert(0, str(Path(__file__).parent.parent))

from parse_rust_complexity import parse_rust_complexity, format_violations


def test_no_violations():
    """Test parsing with no complexity violations."""
    # Create sample JSON with low complexity
    sample_data = {
        "src/lib.rs": {
            "kind": "unit",
            "spaces": [
                {
                    "kind": "function",
                    "name": "simple_function",
                    "start_line": 10,
                    "metrics": {
                        "cyclomatic": {"sum": 5}
                    }
                }
            ]
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f)
        temp_path = Path(f.name)

    try:
        violations = parse_rust_complexity(temp_path, threshold=10)
        assert len(violations) == 0, "Expected no violations for low complexity"
        print("✓ test_no_violations passed")
    finally:
        temp_path.unlink()


def test_with_violations():
    """Test parsing with complexity violations."""
    # Create sample JSON with high complexity
    sample_data = {
        "src/main.rs": {
            "kind": "unit",
            "spaces": [
                {
                    "kind": "function",
                    "name": "complex_function",
                    "start_line": 42,
                    "metrics": {
                        "cyclomatic": {"sum": 15}
                    }
                }
            ]
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f)
        temp_path = Path(f.name)

    try:
        violations = parse_rust_complexity(temp_path, threshold=10)
        assert len(violations) == 1, f"Expected 1 violation, got {len(violations)}"
        assert violations[0]["function_name"] == "complex_function"
        assert violations[0]["complexity"] == 15
        assert violations[0]["line_number"] == 42
        print("✓ test_with_violations passed")
    finally:
        temp_path.unlink()


def test_nested_functions():
    """Test parsing with nested function structures."""
    # Create sample JSON with nested functions
    sample_data = {
        "src/complex.rs": {
            "kind": "unit",
            "spaces": [
                {
                    "kind": "function",
                    "name": "outer_function",
                    "start_line": 10,
                    "metrics": {
                        "cyclomatic": {"sum": 3}
                    },
                    "spaces": [
                        {
                            "kind": "closure",
                            "name": "inner_closure",
                            "start_line": 15,
                            "metrics": {
                                "cyclomatic": {"sum": 12}
                            }
                        }
                    ]
                }
            ]
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f)
        temp_path = Path(f.name)

    try:
        violations = parse_rust_complexity(temp_path, threshold=10)
        assert len(violations) == 1, f"Expected 1 violation from nested closure, got {len(violations)}"
        assert violations[0]["function_name"] == "inner_closure"
        assert violations[0]["complexity"] == 12
        print("✓ test_nested_functions passed")
    finally:
        temp_path.unlink()


def test_multiple_files():
    """Test parsing with multiple files in JSON."""
    sample_data = {
        "src/file1.rs": {
            "kind": "unit",
            "spaces": [
                {
                    "kind": "function",
                    "name": "func1",
                    "start_line": 5,
                    "metrics": {
                        "cyclomatic": {"sum": 11}
                    }
                }
            ]
        },
        "src/file2.rs": {
            "kind": "unit",
            "spaces": [
                {
                    "kind": "function",
                    "name": "func2",
                    "start_line": 20,
                    "metrics": {
                        "cyclomatic": {"sum": 13}
                    }
                }
            ]
        }
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_data, f)
        temp_path = Path(f.name)

    try:
        violations = parse_rust_complexity(temp_path, threshold=10)
        assert len(violations) == 2, f"Expected 2 violations, got {len(violations)}"
        print("✓ test_multiple_files passed")
    finally:
        temp_path.unlink()


def test_format_violations():
    """Test violation formatting output."""
    violations = [
        {
            "function_name": "test_func",
            "file_path": "src/test.rs",
            "line_number": 42,
            "complexity": 15
        }
    ]

    output = format_violations(violations)
    assert "test_func" in output
    assert "src/test.rs:42" in output
    assert "15" in output
    print("✓ test_format_violations passed")


def test_empty_violations():
    """Test formatting with no violations."""
    output = format_violations([])
    assert "✓" in output
    assert "pass" in output.lower()
    print("✓ test_empty_violations passed")


if __name__ == "__main__":
    print("Running tests for parse_rust_complexity.py...\n")

    try:
        test_no_violations()
        test_with_violations()
        test_nested_functions()
        test_multiple_files()
        test_format_violations()
        test_empty_violations()

        print("\n✓ All tests passed!")
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(2)
