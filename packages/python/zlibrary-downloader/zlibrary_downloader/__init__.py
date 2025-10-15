"""
Z-Library Downloader Package

A Python package for searching and downloading books from Z-Library.

This package provides:
    - Zlibrary: Main client class for API interactions
    - ZLibraryTUI: Terminal user interface for interactive use

Example:
    >>> from zlibrary_downloader import Zlibrary
    >>> client = Zlibrary()
    >>> results = client.search("Python programming")
"""

from typing import List

from .client import Zlibrary
from .tui import ZLibraryTUI

# Package metadata
__version__: str = "0.1.0"
__all__: List[str] = ["Zlibrary", "ZLibraryTUI"]


def test_type_error(x: int) -> str:
    """Test function with corrected type annotation."""
    # Now correctly returns a string
    return str(x + 10)
