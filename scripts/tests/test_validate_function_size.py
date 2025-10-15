#!/usr/bin/env python3
"""
Tests for the function size validator script.
"""

import os
import tempfile
import pytest
from pathlib import Path
import sys

# Add parent directory to path to import the validator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validate_function_size import (
    validate_python_file,
    validate_rust_file,
    validate_files,
    MAX_FUNCTION_LINES,
)


class TestValidatePythonFile:
    """Tests for validating Python files."""

    def test_empty_file(self, tmp_path: Path) -> None:
        """Test that an empty file has no violations."""
        file_path = tmp_path / "empty.py"
        file_path.write_text("")
        violations = validate_python_file(str(file_path))
        assert len(violations) == 0

    def test_small_function(self, tmp_path: Path) -> None:
        """Test that a small function passes validation."""
        content = """def small_function():
    '''A small function.'''
    x = 1
    y = 2
    return x + y
"""
        file_path = tmp_path / "small.py"
        file_path.write_text(content)
        violations = validate_python_file(str(file_path))
        assert len(violations) == 0

    def test_function_exactly_at_limit(self, tmp_path: Path) -> None:
        """Test function with exactly MAX_FUNCTION_LINES lines."""
        # Create a function with exactly MAX_FUNCTION_LINES body lines
        lines = ["def at_limit():\n"]
        lines.append('    """Docstring."""\n')
        for i in range(MAX_FUNCTION_LINES):
            lines.append(f"    x{i} = {i}\n")

        file_path = tmp_path / "at_limit.py"
        file_path.write_text("".join(lines))
        violations = validate_python_file(str(file_path))
        assert len(violations) == 0

    def test_function_over_limit(self, tmp_path: Path) -> None:
        """Test function exceeding MAX_FUNCTION_LINES."""
        # Create a function with MAX_FUNCTION_LINES + 5 body lines
        lines = ["def over_limit():\n"]
        lines.append('    """Docstring."""\n')
        for i in range(MAX_FUNCTION_LINES + 5):
            lines.append(f"    x{i} = {i}\n")

        file_path = tmp_path / "over_limit.py"
        file_path.write_text("".join(lines))
        violations = validate_python_file(str(file_path))

        assert len(violations) == 1
        assert violations[0].function_name == "over_limit"
        assert violations[0].line_count > MAX_FUNCTION_LINES

    def test_multiple_functions_mixed(self, tmp_path: Path) -> None:
        """Test file with multiple functions, some passing, some failing."""
        lines = []

        # Small function (passes)
        lines.append("def small_func():\n")
        lines.append('    """Small function."""\n')
        lines.append("    return 1\n")
        lines.append("\n")

        # Large function (fails)
        lines.append("def large_func():\n")
        lines.append('    """Large function."""\n')
        for i in range(MAX_FUNCTION_LINES + 3):
            lines.append(f"    x{i} = {i}\n")
        lines.append("\n")

        # Another small function (passes)
        lines.append("def another_small():\n")
        lines.append("    return 2\n")

        file_path = tmp_path / "mixed.py"
        file_path.write_text("".join(lines))
        violations = validate_python_file(str(file_path))

        assert len(violations) == 1
        assert violations[0].function_name == "large_func"

    def test_async_function(self, tmp_path: Path) -> None:
        """Test that async functions are validated correctly."""
        lines = ["async def async_large():\n"]
        lines.append('    """Async function."""\n')
        for i in range(MAX_FUNCTION_LINES + 2):
            lines.append(f"    await something{i}()\n")

        file_path = tmp_path / "async_func.py"
        file_path.write_text("".join(lines))
        violations = validate_python_file(str(file_path))

        assert len(violations) == 1
        assert violations[0].function_name == "async_large"

    def test_nested_functions(self, tmp_path: Path) -> None:
        """Test that nested functions are validated."""
        lines = ["def outer():\n"]
        lines.append('    """Outer function."""\n')
        lines.append("    x = 1\n")
        lines.append("\n")
        lines.append("    def inner():\n")
        lines.append('        """Inner function."""\n')
        for i in range(MAX_FUNCTION_LINES + 1):
            lines.append(f"        y{i} = {i}\n")
        lines.append("\n")
        lines.append("    return inner\n")

        file_path = tmp_path / "nested.py"
        file_path.write_text("".join(lines))
        violations = validate_python_file(str(file_path))

        # Should detect the inner function as violating
        assert len(violations) >= 1
        assert any(v.function_name == "inner" for v in violations)

    def test_method_in_class(self, tmp_path: Path) -> None:
        """Test that class methods are validated."""
        lines = ["class MyClass:\n"]
        lines.append('    """A class."""\n')
        lines.append("\n")
        lines.append("    def large_method(self):\n")
        lines.append('        """Large method."""\n')
        for i in range(MAX_FUNCTION_LINES + 2):
            lines.append(f"        self.x{i} = {i}\n")

        file_path = tmp_path / "class_method.py"
        file_path.write_text("".join(lines))
        violations = validate_python_file(str(file_path))

        assert len(violations) == 1
        assert violations[0].function_name == "large_method"

    def test_function_with_decorators(self, tmp_path: Path) -> None:
        """Test that functions with decorators are handled correctly."""
        lines = ["@decorator1\n"]
        lines.append("@decorator2\n")
        lines.append("def decorated_func():\n")
        lines.append('    """Decorated function."""\n')
        for i in range(MAX_FUNCTION_LINES + 1):
            lines.append(f"    x{i} = {i}\n")

        file_path = tmp_path / "decorated.py"
        file_path.write_text("".join(lines))
        violations = validate_python_file(str(file_path))

        assert len(violations) == 1
        assert violations[0].function_name == "decorated_func"

    def test_syntax_error_file(self, tmp_path: Path) -> None:
        """Test that syntax errors are handled gracefully."""
        content = "def broken(\n    # Missing closing paren and colon\n    return 42\n"
        file_path = tmp_path / "syntax_error.py"
        file_path.write_text(content)

        # Should not crash, just return empty violations
        violations = validate_python_file(str(file_path))
        assert isinstance(violations, list)


class TestValidateRustFile:
    """Tests for validating Rust files."""

    def test_empty_file(self, tmp_path: Path) -> None:
        """Test that an empty Rust file has no violations."""
        file_path = tmp_path / "empty.rs"
        file_path.write_text("")
        violations = validate_rust_file(str(file_path))
        assert len(violations) == 0

    def test_small_function(self, tmp_path: Path) -> None:
        """Test that a small Rust function passes validation."""
        content = """fn small_function() -> i32 {
    let x = 1;
    let y = 2;
    x + y
}
"""
        file_path = tmp_path / "small.rs"
        file_path.write_text(content)
        violations = validate_rust_file(str(file_path))
        assert len(violations) == 0

    def test_function_over_limit(self, tmp_path: Path) -> None:
        """Test Rust function exceeding MAX_FUNCTION_LINES."""
        lines = ["fn large_function() -> i32 {\n"]
        for i in range(MAX_FUNCTION_LINES + 5):
            lines.append(f"    let x{i} = {i};\n")
        lines.append("    0\n")
        lines.append("}\n")

        file_path = tmp_path / "large.rs"
        file_path.write_text("".join(lines))
        violations = validate_rust_file(str(file_path))

        assert len(violations) == 1
        assert violations[0].function_name == "large_function"
        assert violations[0].line_count > MAX_FUNCTION_LINES

    def test_pub_function(self, tmp_path: Path) -> None:
        """Test that public functions are validated."""
        lines = ["pub fn public_large() -> i32 {\n"]
        for i in range(MAX_FUNCTION_LINES + 3):
            lines.append(f"    let x{i} = {i};\n")
        lines.append("    0\n")
        lines.append("}\n")

        file_path = tmp_path / "pub_func.rs"
        file_path.write_text("".join(lines))
        violations = validate_rust_file(str(file_path))

        assert len(violations) == 1
        assert violations[0].function_name == "public_large"

    def test_async_function(self, tmp_path: Path) -> None:
        """Test that async Rust functions are validated."""
        lines = ["async fn async_large() -> Result<(), Error> {\n"]
        for i in range(MAX_FUNCTION_LINES + 2):
            lines.append(f"    do_something{i}().await?;\n")
        lines.append("    Ok(())\n")
        lines.append("}\n")

        file_path = tmp_path / "async_rust.rs"
        file_path.write_text("".join(lines))
        violations = validate_rust_file(str(file_path))

        assert len(violations) == 1
        assert violations[0].function_name == "async_large"

    def test_unsafe_function(self, tmp_path: Path) -> None:
        """Test that unsafe functions are validated."""
        lines = ["unsafe fn unsafe_large() {\n"]
        for i in range(MAX_FUNCTION_LINES + 1):
            lines.append(f"    *ptr{i} = {i};\n")
        lines.append("}\n")

        file_path = tmp_path / "unsafe_func.rs"
        file_path.write_text("".join(lines))
        violations = validate_rust_file(str(file_path))

        assert len(violations) == 1
        assert violations[0].function_name == "unsafe_large"

    def test_multiple_functions(self, tmp_path: Path) -> None:
        """Test file with multiple functions."""
        lines = []

        # Small function
        lines.append("fn small() -> i32 {\n")
        lines.append("    42\n")
        lines.append("}\n")
        lines.append("\n")

        # Large function
        lines.append("fn large() -> i32 {\n")
        for i in range(MAX_FUNCTION_LINES + 2):
            lines.append(f"    let x{i} = {i};\n")
        lines.append("    0\n")
        lines.append("}\n")

        file_path = tmp_path / "multiple.rs"
        file_path.write_text("".join(lines))
        violations = validate_rust_file(str(file_path))

        assert len(violations) == 1
        assert violations[0].function_name == "large"

    def test_function_with_comments(self, tmp_path: Path) -> None:
        """Test that comments are not counted in function body."""
        lines = ["fn with_comments() -> i32 {\n"]
        for i in range(MAX_FUNCTION_LINES + 10):
            lines.append(f"    // Comment line {i}\n")
        lines.append("    let x = 42;\n")
        lines.append("    x\n")
        lines.append("}\n")

        file_path = tmp_path / "comments.rs"
        file_path.write_text("".join(lines))
        violations = validate_rust_file(str(file_path))

        # Should pass because comments are not counted
        assert len(violations) == 0

    def test_pub_crate_function(self, tmp_path: Path) -> None:
        """Test that pub(crate) functions are validated."""
        lines = ["pub(crate) fn crate_large() -> i32 {\n"]
        for i in range(MAX_FUNCTION_LINES + 1):
            lines.append(f"    let x{i} = {i};\n")
        lines.append("    0\n")
        lines.append("}\n")

        file_path = tmp_path / "pub_crate.rs"
        file_path.write_text("".join(lines))
        violations = validate_rust_file(str(file_path))

        assert len(violations) == 1
        assert violations[0].function_name == "crate_large"


class TestValidateFiles:
    """Tests for the validate_files function."""

    def test_no_violations(self, tmp_path: Path) -> None:
        """Test with files that don't exceed the limit."""
        py_file = tmp_path / "small.py"
        py_file.write_text("def foo():\n    return 1\n")

        rs_file = tmp_path / "small.rs"
        rs_file.write_text("fn bar() -> i32 {\n    42\n}\n")

        violations = validate_files([str(py_file), str(rs_file)])
        assert len(violations) == 0

    def test_with_violations(self, tmp_path: Path) -> None:
        """Test with files that have violations."""
        py_file = tmp_path / "large.py"
        lines = ["def large():\n"]
        for i in range(MAX_FUNCTION_LINES + 5):
            lines.append(f"    x{i} = {i}\n")
        py_file.write_text("".join(lines))

        violations = validate_files([str(py_file)])
        assert len(violations) == 1
        assert violations[0].function_name == "large"

    def test_excludes_test_files(self, tmp_path: Path) -> None:
        """Test that test files are excluded."""
        test_file = tmp_path / "test_large.py"
        lines = ["def test_large():\n"]
        for i in range(MAX_FUNCTION_LINES + 10):
            lines.append(f"    x{i} = {i}\n")
        test_file.write_text("".join(lines))

        violations = validate_files([str(test_file)])
        assert len(violations) == 0

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        """Test with nonexistent file."""
        fake_file = tmp_path / "nonexistent.py"
        violations = validate_files([str(fake_file)])
        assert len(violations) == 0

    def test_mixed_languages(self, tmp_path: Path) -> None:
        """Test with both Python and Rust files."""
        py_file = tmp_path / "large.py"
        lines = ["def py_large():\n"]
        for i in range(MAX_FUNCTION_LINES + 3):
            lines.append(f"    x{i} = {i}\n")
        py_file.write_text("".join(lines))

        rs_file = tmp_path / "large.rs"
        lines = ["fn rs_large() -> i32 {\n"]
        for i in range(MAX_FUNCTION_LINES + 2):
            lines.append(f"    let x{i} = {i};\n")
        lines.append("    0\n}\n")
        rs_file.write_text("".join(lines))

        violations = validate_files([str(py_file), str(rs_file)])
        assert len(violations) == 2
        assert any(v.function_name == "py_large" for v in violations)
        assert any(v.function_name == "rs_large" for v in violations)

    def test_unsupported_extension(self, tmp_path: Path) -> None:
        """Test that unsupported file types are ignored."""
        txt_file = tmp_path / "readme.txt"
        txt_file.write_text("This is just text, not code.")

        violations = validate_files([str(txt_file)])
        assert len(violations) == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
