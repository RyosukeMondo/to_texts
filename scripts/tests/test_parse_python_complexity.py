#!/usr/bin/env python3
"""Unit tests for parse_python_complexity.py script."""

import json
import tempfile
from pathlib import Path

# Import the module we're testing
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from parse_python_complexity import parse_radon_complexity, format_violations


def test_parse_radon_no_violations():
    """Test parsing radon output with no violations."""
    test_data = {
        "test_file.py": [
            {
                "type": "function",
                "name": "simple_func",
                "lineno": 10,
                "complexity": 5,
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = Path(f.name)

    try:
        violations = parse_radon_complexity(temp_path, threshold=10)
        assert len(violations) == 0, f"Expected no violations, got {len(violations)}"
    finally:
        temp_path.unlink()


def test_parse_radon_with_violations():
    """Test parsing radon output with violations."""
    test_data = {
        "test_file.py": [
            {
                "type": "function",
                "name": "simple_func",
                "lineno": 10,
                "complexity": 5,
            },
            {
                "type": "function",
                "name": "complex_func",
                "lineno": 20,
                "complexity": 15,
            },
            {
                "type": "method",
                "name": "complex_method",
                "lineno": 30,
                "complexity": 12,
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = Path(f.name)

    try:
        violations = parse_radon_complexity(temp_path, threshold=10)
        assert len(violations) == 2, f"Expected 2 violations, got {len(violations)}"

        # Check that violations contain correct information
        assert violations[0]['function_name'] == 'complex_func'
        assert violations[0]['complexity'] == 15
        assert violations[0]['line_number'] == 20

        assert violations[1]['function_name'] == 'complex_method'
        assert violations[1]['complexity'] == 12
        assert violations[1]['line_number'] == 30
    finally:
        temp_path.unlink()


def test_parse_radon_at_threshold():
    """Test parsing radon output with complexity exactly at threshold."""
    test_data = {
        "test_file.py": [
            {
                "type": "function",
                "name": "at_threshold",
                "lineno": 10,
                "complexity": 10,
            }
        ]
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = Path(f.name)

    try:
        violations = parse_radon_complexity(temp_path, threshold=10)
        assert len(violations) == 0, "Function at threshold should not be a violation"
    finally:
        temp_path.unlink()


def test_parse_radon_empty_file():
    """Test parsing radon output with empty file (no functions)."""
    test_data = {
        "empty_file.py": []
    }

    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(test_data, f)
        temp_path = Path(f.name)

    try:
        violations = parse_radon_complexity(temp_path, threshold=10)
        assert len(violations) == 0, "Empty file should have no violations"
    finally:
        temp_path.unlink()


def test_format_violations_empty():
    """Test formatting with no violations."""
    result = format_violations([])
    assert "✓" in result
    assert "pass" in result.lower()


def test_format_violations_with_data():
    """Test formatting with violations."""
    violations = [
        {
            "function_name": "func1",
            "file_path": "file.py",
            "line_number": 10,
            "complexity": 15
        },
        {
            "function_name": "func2",
            "file_path": "file.py",
            "line_number": 20,
            "complexity": 12
        }
    ]

    result = format_violations(violations)
    assert "✗" in result
    assert "2 function(s)" in result
    assert "func1" in result
    assert "func2" in result
    assert "complexity 15" in result
    assert "complexity 12" in result
    # Should be sorted by complexity (highest first)
    assert result.index("func1") < result.index("func2")


if __name__ == "__main__":
    print("Running tests for parse_python_complexity.py...")

    test_parse_radon_no_violations()
    print("✓ test_parse_radon_no_violations passed")

    test_parse_radon_with_violations()
    print("✓ test_parse_radon_with_violations passed")

    test_parse_radon_at_threshold()
    print("✓ test_parse_radon_at_threshold passed")

    test_parse_radon_empty_file()
    print("✓ test_parse_radon_empty_file passed")

    test_format_violations_empty()
    print("✓ test_format_violations_empty passed")

    test_format_violations_with_data()
    print("✓ test_format_violations_with_data passed")

    print("\nAll tests passed! ✓")
