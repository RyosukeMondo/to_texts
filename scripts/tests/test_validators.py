#!/usr/bin/env python3
"""
Unit tests for QA validator scripts.

Tests for:
- validate_line_count.py
- validate_function_size.py
- parse_python_complexity.py
- parse_rust_complexity.py
"""

import json
import sys
from pathlib import Path

import pytest

# Add parent directory to path to import validators
sys.path.insert(0, str(Path(__file__).parent.parent))

from validate_line_count import (  # noqa: E402
    MAX_LINES,
    count_lines_python,
    count_lines_rust,
    is_excluded,
    validate_files as validate_line_count_files,
)
from validate_function_size import (  # noqa: E402
    MAX_FUNCTION_LINES,
    validate_files as validate_function_size_files,
    validate_python_file,
    validate_rust_file,
)
from parse_python_complexity import parse_radon_complexity  # noqa: E402
from parse_rust_complexity import parse_rust_complexity  # noqa: E402


class TestLineCountValidator:
    """Tests for validate_line_count.py"""

    def test_is_excluded_test_files(self):
        """Test that test files are excluded"""
        assert is_excluded("test_foo.py")
        assert is_excluded("foo_test.py")
        assert is_excluded("foo_test.rs")
        assert is_excluded("test_utils.rs")  # Files starting with test_ are excluded
        assert not is_excluded("my_file.py")

    def test_is_excluded_directories(self):
        """Test that files in excluded directories are excluded"""
        assert is_excluded("tests/test_foo.py")
        assert is_excluded("target/debug/foo.rs")
        assert is_excluded("venv/lib/python3.9/site.py")
        assert is_excluded("__pycache__/foo.pyc")
        assert is_excluded("build/lib/foo.py")
        assert not is_excluded("src/main.rs")

    def test_count_lines_python_simple(self, tmp_path):
        """Test counting lines in simple Python file"""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """# This is a comment
def foo():
    pass

# Another comment
def bar():
    return 42
"""
        )
        # Should count: def foo, pass, def bar, return 42 = 4 lines
        assert count_lines_python(str(test_file)) == 4

    def test_count_lines_python_with_docstrings(self, tmp_path):
        """Test that docstrings are counted"""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            '''def foo():
    """This is a docstring."""
    pass

def bar():
    """
    Multi-line docstring.
    More lines here.
    """
    return 42
'''
        )
        # def foo, docstring, pass, def bar, 4 docstring lines, return = 9 lines
        assert count_lines_python(str(test_file)) == 9

    def test_count_lines_python_empty_lines_ignored(self, tmp_path):
        """Test that empty lines are not counted"""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """def foo():

    pass


def bar():

    return 42

"""
        )
        # def foo, pass, def bar, return 42 = 4 lines
        assert count_lines_python(str(test_file)) == 4

    def test_count_lines_rust_simple(self, tmp_path):
        """Test counting lines in simple Rust file"""
        test_file = tmp_path / "test.rs"
        test_file.write_text(
            """// Comment
fn main() {
    println!("Hello");
}

// Another comment
fn foo() {
    let x = 42;
}
"""
        )
        # fn main, println, }, fn foo, let x, } = 6 lines
        assert count_lines_rust(str(test_file)) == 6

    def test_count_lines_rust_multiline_comment(self, tmp_path):
        """Test that multiline comments are counted"""
        test_file = tmp_path / "test.rs"
        test_file.write_text(
            """fn main() {
    /*
     * Multi-line comment
     * More lines
     */
    println!("Hello");
}
"""
        )
        # fn main, 4 comment lines (/* and 3 inner lines), println, } = 7 lines
        assert count_lines_rust(str(test_file)) == 7

    def test_validate_files_under_limit(self, tmp_path):
        """Test validation passes when files are under limit"""
        test_file = tmp_path / "small.py"
        test_file.write_text("def foo():\n    pass\n")
        violations = validate_line_count_files([str(test_file)])
        assert len(violations) == 0

    def test_validate_files_at_limit(self, tmp_path):
        """Test validation passes when file is exactly at limit"""
        test_file = tmp_path / "at_limit.py"
        # Create a file with exactly MAX_LINES lines
        lines = "\n".join([f"x = {i}" for i in range(MAX_LINES)])
        test_file.write_text(lines)
        violations = validate_line_count_files([str(test_file)])
        assert len(violations) == 0

    def test_validate_files_over_limit(self, tmp_path):
        """Test validation fails when file exceeds limit"""
        test_file = tmp_path / "large.py"
        # Create a file with MAX_LINES + 1 lines
        lines = "\n".join([f"x = {i}" for i in range(MAX_LINES + 1)])
        test_file.write_text(lines)
        violations = validate_line_count_files([str(test_file)])
        assert len(violations) == 1
        assert violations[0][0] == str(test_file)
        assert violations[0][1] == MAX_LINES + 1


class TestFunctionSizeValidator:
    """Tests for validate_function_size.py"""

    def test_validate_python_small_function(self, tmp_path):
        """Test that small functions pass validation"""
        test_file = tmp_path / "test.py"
        test_file.write_text(
            """def foo():
    '''Docstring'''
    x = 1
    return x
"""
        )
        violations = validate_python_file(str(test_file))
        assert len(violations) == 0

    def test_validate_python_function_at_limit(self, tmp_path):
        """Test that functions at exactly the limit pass"""
        test_file = tmp_path / "test.py"
        # Create function with exactly MAX_FUNCTION_LINES lines in body
        body_lines = "\n    ".join([f"x{i} = {i}" for i in range(MAX_FUNCTION_LINES)])
        test_file.write_text(
            f"""def foo():
    '''Docstring'''
    {body_lines}
"""
        )
        violations = validate_python_file(str(test_file))
        assert len(violations) == 0

    def test_validate_python_function_over_limit(self, tmp_path):
        """Test that large functions fail validation"""
        test_file = tmp_path / "test.py"
        # Create function with MAX_FUNCTION_LINES + 1 lines in body
        body_lines = "\n    ".join([f"x{i} = {i}" for i in range(MAX_FUNCTION_LINES + 5)])
        test_file.write_text(
            f"""def large_function():
    '''Docstring'''
    {body_lines}
"""
        )
        violations = validate_python_file(str(test_file))
        assert len(violations) == 1
        assert violations[0].function_name == "large_function"
        assert violations[0].line_count > MAX_FUNCTION_LINES

    def test_validate_python_async_function(self, tmp_path):
        """Test that async functions are validated correctly"""
        test_file = tmp_path / "test.py"
        body_lines = "\n    ".join([f"await task{i}()" for i in range(MAX_FUNCTION_LINES + 5)])
        test_file.write_text(
            f"""async def large_async():
    '''Async function'''
    {body_lines}
"""
        )
        violations = validate_python_file(str(test_file))
        assert len(violations) == 1
        assert violations[0].function_name == "large_async"

    def test_validate_python_multiple_functions(self, tmp_path):
        """Test validation of multiple functions"""
        test_file = tmp_path / "test.py"
        large_body = "\n    ".join([f"x{i} = {i}" for i in range(MAX_FUNCTION_LINES + 5)])
        test_file.write_text(
            f"""def small():
    return 1

def large():
    {large_body}

def another_small():
    return 2
"""
        )
        violations = validate_python_file(str(test_file))
        assert len(violations) == 1
        assert violations[0].function_name == "large"

    def test_validate_rust_small_function(self, tmp_path):
        """Test that small Rust functions pass validation"""
        test_file = tmp_path / "test.rs"
        test_file.write_text(
            """fn foo() -> i32 {
    let x = 42;
    x
}
"""
        )
        violations = validate_rust_file(str(test_file))
        assert len(violations) == 0

    def test_validate_rust_function_over_limit(self, tmp_path):
        """Test that large Rust functions fail validation"""
        test_file = tmp_path / "test.rs"
        body_lines = "\n    ".join([f"let x{i} = {i};" for i in range(MAX_FUNCTION_LINES + 5)])
        test_file.write_text(
            f"""fn large_function() {{
    {body_lines}
}}
"""
        )
        violations = validate_rust_file(str(test_file))
        assert len(violations) == 1
        assert violations[0].function_name == "large_function"
        assert violations[0].line_count > MAX_FUNCTION_LINES

    def test_validate_rust_pub_function(self, tmp_path):
        """Test that public Rust functions are validated"""
        test_file = tmp_path / "test.rs"
        body_lines = "\n    ".join([f"let x{i} = {i};" for i in range(MAX_FUNCTION_LINES + 5)])
        test_file.write_text(
            f"""pub fn large_pub() {{
    {body_lines}
}}
"""
        )
        violations = validate_rust_file(str(test_file))
        assert len(violations) == 1
        assert violations[0].function_name == "large_pub"

    def test_validate_files_skips_test_files(self, tmp_path):
        """Test that test files are skipped"""
        test_file = tmp_path / "test_foo.py"
        body_lines = "\n    ".join([f"x{i} = {i}" for i in range(MAX_FUNCTION_LINES + 10)])
        test_file.write_text(
            f"""def huge_test():
    {body_lines}
"""
        )
        violations = validate_function_size_files([str(test_file)])
        assert len(violations) == 0  # Test files should be skipped


class TestPythonComplexityParser:
    """Tests for parse_python_complexity.py"""

    def test_parse_empty_json(self, tmp_path):
        """Test parsing empty radon output"""
        json_file = tmp_path / "empty.json"
        json_file.write_text("{}")
        violations = parse_radon_complexity(json_file, threshold=10)
        assert len(violations) == 0

    def test_parse_no_violations(self, tmp_path):
        """Test parsing radon output with no violations"""
        json_file = tmp_path / "no_violations.json"
        data = {
            "test.py": [
                {
                    "type": "function",
                    "name": "simple_function",
                    "lineno": 1,
                    "complexity": 5,
                    "rank": "A"
                }
            ]
        }
        json_file.write_text(json.dumps(data))
        violations = parse_radon_complexity(json_file, threshold=10)
        assert len(violations) == 0

    def test_parse_with_violations(self, tmp_path):
        """Test parsing radon output with complexity violations"""
        json_file = tmp_path / "violations.json"
        data = {
            "complex.py": [
                {
                    "type": "function",
                    "name": "complex_function",
                    "lineno": 10,
                    "complexity": 15,
                    "rank": "C"
                },
                {
                    "type": "function",
                    "name": "simple_function",
                    "lineno": 30,
                    "complexity": 5,
                    "rank": "A"
                }
            ]
        }
        json_file.write_text(json.dumps(data))
        violations = parse_radon_complexity(json_file, threshold=10)
        assert len(violations) == 1
        assert violations[0]["function_name"] == "complex_function"
        assert violations[0]["complexity"] == 15
        assert violations[0]["line_number"] == 10

    def test_parse_at_threshold(self, tmp_path):
        """Test that functions at threshold pass"""
        json_file = tmp_path / "at_threshold.json"
        data = {
            "test.py": [
                {
                    "type": "function",
                    "name": "at_limit",
                    "lineno": 1,
                    "complexity": 10,
                    "rank": "B"
                }
            ]
        }
        json_file.write_text(json.dumps(data))
        violations = parse_radon_complexity(json_file, threshold=10)
        assert len(violations) == 0

    def test_parse_just_over_threshold(self, tmp_path):
        """Test that functions just over threshold fail"""
        json_file = tmp_path / "over_threshold.json"
        data = {
            "test.py": [
                {
                    "type": "function",
                    "name": "just_over",
                    "lineno": 1,
                    "complexity": 11,
                    "rank": "B"
                }
            ]
        }
        json_file.write_text(json.dumps(data))
        violations = parse_radon_complexity(json_file, threshold=10)
        assert len(violations) == 1

    def test_parse_methods_included(self, tmp_path):
        """Test that methods are included in validation"""
        json_file = tmp_path / "methods.json"
        data = {
            "test.py": [
                {
                    "type": "method",
                    "name": "complex_method",
                    "lineno": 5,
                    "complexity": 12,
                    "rank": "B"
                }
            ]
        }
        json_file.write_text(json.dumps(data))
        violations = parse_radon_complexity(json_file, threshold=10)
        assert len(violations) == 1
        assert violations[0]["function_name"] == "complex_method"

    def test_parse_classes_excluded(self, tmp_path):
        """Test that classes are excluded from validation"""
        json_file = tmp_path / "classes.json"
        data = {
            "test.py": [
                {
                    "type": "class",
                    "name": "ComplexClass",
                    "lineno": 1,
                    "complexity": 20,
                    "rank": "D"
                }
            ]
        }
        json_file.write_text(json.dumps(data))
        violations = parse_radon_complexity(json_file, threshold=10)
        assert len(violations) == 0

    def test_parse_invalid_json(self, tmp_path):
        """Test handling of invalid JSON"""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{ invalid json }")
        with pytest.raises(json.JSONDecodeError):
            parse_radon_complexity(json_file, threshold=10)

    def test_parse_missing_file(self, tmp_path):
        """Test handling of missing file"""
        json_file = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            parse_radon_complexity(json_file, threshold=10)

    def test_parse_multiple_files(self, tmp_path):
        """Test parsing output from multiple source files"""
        json_file = tmp_path / "multi.json"
        data = {
            "file1.py": [
                {
                    "type": "function",
                    "name": "func1",
                    "lineno": 1,
                    "complexity": 12,
                    "rank": "B"
                }
            ],
            "file2.py": [
                {
                    "type": "function",
                    "name": "func2",
                    "lineno": 5,
                    "complexity": 15,
                    "rank": "C"
                }
            ]
        }
        json_file.write_text(json.dumps(data))
        violations = parse_radon_complexity(json_file, threshold=10)
        assert len(violations) == 2
        assert violations[0]["file_path"] == "file1.py"
        assert violations[1]["file_path"] == "file2.py"


class TestRustComplexityParser:
    """Tests for parse_rust_complexity.py"""

    def test_parse_empty_json(self, tmp_path):
        """Test parsing empty rust-code-analysis output"""
        json_file = tmp_path / "empty.json"
        json_file.write_text("{}")
        violations = parse_rust_complexity(json_file, threshold=10)
        assert len(violations) == 0

    def test_parse_no_violations(self, tmp_path):
        """Test parsing output with no violations"""
        json_file = tmp_path / "no_violations.json"
        data = {
            "test.rs": {
                "kind": "unit",
                "spaces": [
                    {
                        "kind": "function",
                        "name": "simple_fn",
                        "start_line": 1,
                        "metrics": {
                            "cyclomatic": {"sum": 5}
                        },
                        "spaces": []
                    }
                ]
            }
        }
        json_file.write_text(json.dumps(data))
        violations = parse_rust_complexity(json_file, threshold=10)
        assert len(violations) == 0

    def test_parse_with_violations(self, tmp_path):
        """Test parsing output with complexity violations"""
        json_file = tmp_path / "violations.json"
        data = {
            "complex.rs": {
                "kind": "unit",
                "spaces": [
                    {
                        "kind": "function",
                        "name": "complex_fn",
                        "start_line": 10,
                        "metrics": {
                            "cyclomatic": {"sum": 15}
                        },
                        "spaces": []
                    }
                ]
            }
        }
        json_file.write_text(json.dumps(data))
        violations = parse_rust_complexity(json_file, threshold=10)
        assert len(violations) == 1
        assert violations[0]["function_name"] == "complex_fn"
        assert violations[0]["complexity"] == 15
        assert violations[0]["line_number"] == 10

    def test_parse_methods_included(self, tmp_path):
        """Test that methods are included in validation"""
        json_file = tmp_path / "methods.json"
        data = {
            "test.rs": {
                "kind": "unit",
                "spaces": [
                    {
                        "kind": "method",
                        "name": "complex_method",
                        "start_line": 20,
                        "metrics": {
                            "cyclomatic": {"sum": 12}
                        },
                        "spaces": []
                    }
                ]
            }
        }
        json_file.write_text(json.dumps(data))
        violations = parse_rust_complexity(json_file, threshold=10)
        assert len(violations) == 1
        assert violations[0]["function_name"] == "complex_method"

    def test_parse_nested_functions(self, tmp_path):
        """Test parsing nested function structures"""
        json_file = tmp_path / "nested.json"
        data = {
            "test.rs": {
                "kind": "unit",
                "spaces": [
                    {
                        "kind": "function",
                        "name": "outer",
                        "start_line": 1,
                        "metrics": {
                            "cyclomatic": {"sum": 5}
                        },
                        "spaces": [
                            {
                                "kind": "closure",
                                "name": "inner",
                                "start_line": 3,
                                "metrics": {
                                    "cyclomatic": {"sum": 12}
                                },
                                "spaces": []
                            }
                        ]
                    }
                ]
            }
        }
        json_file.write_text(json.dumps(data))
        violations = parse_rust_complexity(json_file, threshold=10)
        assert len(violations) == 1
        assert violations[0]["function_name"] == "inner"

    def test_parse_at_threshold(self, tmp_path):
        """Test that functions at threshold pass"""
        json_file = tmp_path / "at_threshold.json"
        data = {
            "test.rs": {
                "kind": "unit",
                "spaces": [
                    {
                        "kind": "function",
                        "name": "at_limit",
                        "start_line": 1,
                        "metrics": {
                            "cyclomatic": {"sum": 10}
                        },
                        "spaces": []
                    }
                ]
            }
        }
        json_file.write_text(json.dumps(data))
        violations = parse_rust_complexity(json_file, threshold=10)
        assert len(violations) == 0

    def test_parse_just_over_threshold(self, tmp_path):
        """Test that functions just over threshold fail"""
        json_file = tmp_path / "over_threshold.json"
        data = {
            "test.rs": {
                "kind": "unit",
                "spaces": [
                    {
                        "kind": "function",
                        "name": "just_over",
                        "start_line": 1,
                        "metrics": {
                            "cyclomatic": {"sum": 11}
                        },
                        "spaces": []
                    }
                ]
            }
        }
        json_file.write_text(json.dumps(data))
        violations = parse_rust_complexity(json_file, threshold=10)
        assert len(violations) == 1

    def test_parse_invalid_json(self, tmp_path):
        """Test handling of invalid JSON"""
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{ invalid json }")
        with pytest.raises(json.JSONDecodeError):
            parse_rust_complexity(json_file, threshold=10)

    def test_parse_missing_file(self, tmp_path):
        """Test handling of missing file"""
        json_file = tmp_path / "nonexistent.json"
        with pytest.raises(FileNotFoundError):
            parse_rust_complexity(json_file, threshold=10)

    def test_parse_multiple_files(self, tmp_path):
        """Test parsing output from multiple source files"""
        json_file = tmp_path / "multi.json"
        data = {
            "file1.rs": {
                "kind": "unit",
                "spaces": [
                    {
                        "kind": "function",
                        "name": "func1",
                        "start_line": 1,
                        "metrics": {
                            "cyclomatic": {"sum": 12}
                        },
                        "spaces": []
                    }
                ]
            },
            "file2.rs": {
                "kind": "unit",
                "spaces": [
                    {
                        "kind": "function",
                        "name": "func2",
                        "start_line": 5,
                        "metrics": {
                            "cyclomatic": {"sum": 15}
                        },
                        "spaces": []
                    }
                ]
            }
        }
        json_file.write_text(json.dumps(data))
        violations = parse_rust_complexity(json_file, threshold=10)
        assert len(violations) == 2
        assert violations[0]["file_path"] == "file1.rs"
        assert violations[1]["file_path"] == "file2.rs"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
