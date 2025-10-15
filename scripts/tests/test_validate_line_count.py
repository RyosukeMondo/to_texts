#!/usr/bin/env python3
"""
Tests for the line count validator script.
"""

import os
import tempfile
import pytest
from pathlib import Path
import sys

# Add parent directory to path to import the validator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from validate_line_count import (
    count_lines_python,
    count_lines_rust,
    is_excluded,
    validate_files,
    MAX_LINES,
)


class TestIsExcluded:
    """Tests for the is_excluded function."""

    def test_excludes_test_files(self) -> None:
        """Test that test files are excluded."""
        assert is_excluded("test_foo.py")
        assert is_excluded("foo_test.py")
        assert is_excluded("tests/test_bar.py")

    def test_excludes_build_artifacts(self) -> None:
        """Test that build artifacts are excluded."""
        assert is_excluded("target/debug/foo")
        assert is_excluded("venv/lib/python")
        assert is_excluded(".venv/bin/python")
        assert is_excluded("__pycache__/foo.pyc")
        assert is_excluded("build/lib/foo")
        assert is_excluded("dist/foo-1.0.tar.gz")

    def test_includes_normal_files(self) -> None:
        """Test that normal files are not excluded."""
        assert not is_excluded("src/main.rs")
        assert not is_excluded("zlibrary_downloader/client.py")
        assert not is_excluded("scripts/validate.py")


class TestCountLinesPython:
    """Tests for counting lines in Python files."""

    def test_empty_file(self, tmp_path: Path) -> None:
        """Test counting lines in an empty file."""
        file_path = tmp_path / "empty.py"
        file_path.write_text("")
        assert count_lines_python(str(file_path)) == 0

    def test_only_empty_lines(self, tmp_path: Path) -> None:
        """Test file with only empty lines."""
        file_path = tmp_path / "empty_lines.py"
        file_path.write_text("\n\n\n\n\n")
        assert count_lines_python(str(file_path)) == 0

    def test_only_comments(self, tmp_path: Path) -> None:
        """Test file with only comments."""
        file_path = tmp_path / "comments.py"
        file_path.write_text("# Comment 1\n# Comment 2\n# Comment 3\n")
        assert count_lines_python(str(file_path)) == 0

    def test_code_lines(self, tmp_path: Path) -> None:
        """Test counting actual code lines."""
        file_path = tmp_path / "code.py"
        file_path.write_text("def foo():\n    return 42\n\nprint(foo())\n")
        assert count_lines_python(str(file_path)) == 3

    def test_mixed_content(self, tmp_path: Path) -> None:
        """Test file with mixed content."""
        content = """# This is a comment
import sys

def foo():
    # Another comment
    return 42

# Final comment
"""
        file_path = tmp_path / "mixed.py"
        file_path.write_text(content)
        # Should count: import sys, def foo():, return 42 = 3 lines
        assert count_lines_python(str(file_path)) == 3

    def test_docstring_single_line(self, tmp_path: Path) -> None:
        """Test single-line docstrings."""
        content = '''"""Module docstring."""
def foo():
    """Function docstring."""
    return 42
'''
        file_path = tmp_path / "docstring.py"
        file_path.write_text(content)
        # Should count: docstring, def foo():, function docstring, return 42 = 4 lines
        assert count_lines_python(str(file_path)) == 4

    def test_docstring_multiline(self, tmp_path: Path) -> None:
        """Test multiline docstrings."""
        content = '''"""
Module docstring.
With multiple lines.
"""
def foo():
    """
    Function docstring.
    With multiple lines.
    """
    return 42
'''
        file_path = tmp_path / "docstring_multi.py"
        file_path.write_text(content)
        # Should count: 4 module docstring lines + def foo(): + 4 function docstring lines + return 42 = 10 lines
        assert count_lines_python(str(file_path)) == 10

    def test_exactly_at_limit(self, tmp_path: Path) -> None:
        """Test file with exactly MAX_LINES lines."""
        file_path = tmp_path / "at_limit.py"
        # Create file with exactly MAX_LINES code lines
        lines = ["x = 1\n" for _ in range(MAX_LINES)]
        file_path.write_text("".join(lines))
        assert count_lines_python(str(file_path)) == MAX_LINES

    def test_over_limit(self, tmp_path: Path) -> None:
        """Test file with more than MAX_LINES lines."""
        file_path = tmp_path / "over_limit.py"
        # Create file with MAX_LINES + 1 code lines
        lines = ["x = 1\n" for _ in range(MAX_LINES + 1)]
        file_path.write_text("".join(lines))
        assert count_lines_python(str(file_path)) == MAX_LINES + 1


class TestCountLinesRust:
    """Tests for counting lines in Rust files."""

    def test_empty_file(self, tmp_path: Path) -> None:
        """Test counting lines in an empty Rust file."""
        file_path = tmp_path / "empty.rs"
        file_path.write_text("")
        assert count_lines_rust(str(file_path)) == 0

    def test_only_comments(self, tmp_path: Path) -> None:
        """Test Rust file with only comments."""
        content = """// Comment 1
// Comment 2
/* Block comment */
"""
        file_path = tmp_path / "comments.rs"
        file_path.write_text(content)
        assert count_lines_rust(str(file_path)) == 1  # The block comment line

    def test_code_lines(self, tmp_path: Path) -> None:
        """Test counting actual Rust code lines."""
        content = """fn main() {
    println!("Hello");
}
"""
        file_path = tmp_path / "code.rs"
        file_path.write_text(content)
        assert count_lines_rust(str(file_path)) == 3

    def test_multiline_comment(self, tmp_path: Path) -> None:
        """Test Rust multiline comments."""
        content = """/*
 * Multiline comment
 * Line 2
 */
fn main() {
    println!("Hello");
}
"""
        file_path = tmp_path / "multiline.rs"
        file_path.write_text(content)
        # Should count: 4 comment lines + fn main() + println + } = 7 lines
        assert count_lines_rust(str(file_path)) == 7

    def test_mixed_content(self, tmp_path: Path) -> None:
        """Test Rust file with mixed content."""
        content = """// This is a comment
use std::io;

fn foo() -> i32 {
    // Another comment
    42
}

// Final comment
"""
        file_path = tmp_path / "mixed.rs"
        file_path.write_text(content)
        # Should count: use std::io, fn foo(), 42, } = 4 lines
        assert count_lines_rust(str(file_path)) == 4


class TestValidateFiles:
    """Tests for the validate_files function."""

    def test_no_violations(self, tmp_path: Path) -> None:
        """Test with files that don't exceed the limit."""
        file1 = tmp_path / "small1.py"
        file1.write_text("x = 1\n")
        file2 = tmp_path / "small2.py"
        file2.write_text("y = 2\n")

        violations = validate_files([str(file1), str(file2)])
        assert len(violations) == 0

    def test_with_violations(self, tmp_path: Path) -> None:
        """Test with files that exceed the limit."""
        file1 = tmp_path / "large.py"
        lines = ["x = 1\n" for _ in range(MAX_LINES + 10)]
        file1.write_text("".join(lines))

        violations = validate_files([str(file1)])
        assert len(violations) == 1
        assert violations[0][0] == str(file1)
        assert violations[0][1] == MAX_LINES + 10

    def test_excludes_test_files(self, tmp_path: Path) -> None:
        """Test that test files are excluded from validation."""
        test_file = tmp_path / "test_large.py"
        lines = ["x = 1\n" for _ in range(MAX_LINES + 10)]
        test_file.write_text("".join(lines))

        violations = validate_files([str(test_file)])
        assert len(violations) == 0

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        """Test with nonexistent file."""
        fake_file = tmp_path / "nonexistent.py"
        violations = validate_files([str(fake_file)])
        assert len(violations) == 0

    def test_mixed_files(self, tmp_path: Path) -> None:
        """Test with mix of passing and failing files."""
        small_file = tmp_path / "small.py"
        small_file.write_text("x = 1\n")

        large_file = tmp_path / "large.py"
        lines = ["x = 1\n" for _ in range(MAX_LINES + 5)]
        large_file.write_text("".join(lines))

        test_file = tmp_path / "test_large.py"
        lines = ["x = 1\n" for _ in range(MAX_LINES + 10)]
        test_file.write_text("".join(lines))

        violations = validate_files([str(small_file), str(large_file), str(test_file)])
        assert len(violations) == 1
        assert violations[0][0] == str(large_file)
        assert violations[0][1] == MAX_LINES + 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
