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
        "hash": "abcd1234",
        "title": "Test Book",
        "author": "Test Author",
        "year": "2024",
        "language": "english",
        "extension": "pdf",
        "filesize": "1024000",
        "cover": "https://example.com/cover.jpg",
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


@pytest.fixture
def sample_login_response() -> Dict[str, Any]:
    """
    Provide sample successful login response for testing.

    Returns:
        Dict[str, Any]: A dictionary representing a successful login response
    """
    return {
        "success": True,
        "user": {
            "id": "123456",
            "email": "test@example.com",
            "name": "Test User",
            "kindle_email": "test@kindle.com",
            "remix_userkey": "test_userkey_12345",
        },
    }


@pytest.fixture
def sample_profile_response() -> Dict[str, Any]:
    """
    Provide sample profile response for testing.

    Returns:
        Dict[str, Any]: A dictionary representing a profile response
    """
    return {
        "success": True,
        "user": {
            "id": "123456",
            "email": "test@example.com",
            "name": "Test User",
            "kindle_email": "test@kindle.com",
            "remix_userkey": "test_userkey_12345",
            "downloads_limit": 10,
            "downloads_today": 3,
        },
    }


@pytest.fixture
def sample_book_file_response() -> Dict[str, Any]:
    """
    Provide sample book file download response for testing.

    Returns:
        Dict[str, Any]: A dictionary representing a book file response
    """
    return {
        "success": True,
        "file": {
            "description": "Test Book",
            "author": "Test Author",
            "extension": "pdf",
            "downloadLink": "https://example.com/download/testbook.pdf",
        },
    }
