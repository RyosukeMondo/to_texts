"""
Z-Library Downloader Package

A Python package for searching and downloading books from Z-Library.
"""

from .client import Zlibrary
from .tui import ZLibraryTUI

__version__ = "0.1.0"
__all__ = ["Zlibrary", "ZLibraryTUI"]
