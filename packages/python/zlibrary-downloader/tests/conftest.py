"""
Pytest configuration and shared fixtures for zlibrary-downloader tests.

This module provides common test fixtures used across all test modules,
including mock clients, sample data, and test utilities.
"""

from typing import Any, Dict
from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_zlibrary_client() -> Mock:
    """
    Create a mock Zlibrary client for testing.

    Returns:
        Mock: A mock Zlibrary client with common methods stubbed
    """
    client = Mock()
    client.login.return_value = True
    client.search.return_value = []
    client.downloadBook.return_value = None
    return client


@pytest.fixture
def sample_book_data() -> Dict[str, Any]:
    """
    Provide sample book data for testing.

    Returns:
        Dict[str, Any]: A dictionary representing a sample book response
    """
    return {
        "id": "12345",
        "title": "Test Book",
        "author": "Test Author",
        "year": "2024",
        "language": "english",
        "extension": "pdf",
        "filesize": "1024000",
    }


@pytest.fixture
def sample_search_results(sample_book_data: Dict[str, Any]) -> list[Dict[str, Any]]:
    """
    Provide sample search results for testing.

    Args:
        sample_book_data: Sample book data fixture

    Returns:
        list[Dict[str, Any]]: A list of sample book dictionaries
    """
    return [sample_book_data, {**sample_book_data, "id": "67890", "title": "Another Book"}]
