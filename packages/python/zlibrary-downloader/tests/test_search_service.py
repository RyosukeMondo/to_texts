"""
Unit tests for the SearchService class.

Tests cover business logic using mocked dependencies,
ensuring proper search orchestration, author extraction,
and database storage operations.
"""

from unittest.mock import Mock, MagicMock

import pytest

from zlibrary_downloader.search_service import SearchService
from zlibrary_downloader.book_repository import BookRepository
from zlibrary_downloader.author_repository import AuthorRepository
from zlibrary_downloader.search_history_repository import SearchHistoryRepository
from zlibrary_downloader.models import Book, Author
from zlibrary_downloader.client import Zlibrary


@pytest.fixture
def mock_book_repo() -> Mock:
    """Create mock BookRepository."""
    return Mock(spec=BookRepository)


@pytest.fixture
def mock_author_repo() -> Mock:
    """Create mock AuthorRepository."""
    return Mock(spec=AuthorRepository)


@pytest.fixture
def mock_search_repo() -> Mock:
    """Create mock SearchHistoryRepository."""
    return Mock(spec=SearchHistoryRepository)


@pytest.fixture
def mock_client() -> Mock:
    """Create mock Zlibrary client."""
    return Mock(spec=Zlibrary)


@pytest.fixture
def search_service(
    mock_book_repo: Mock,
    mock_author_repo: Mock,
    mock_search_repo: Mock,
) -> SearchService:
    """Create SearchService with mocked dependencies."""
    return SearchService(mock_book_repo, mock_author_repo, mock_search_repo)


@pytest.fixture
def sample_api_response() -> dict:
    """Create sample API response from Z-Library."""
    return {
        "success": True,
        "books": [
            {
                "id": "12345",
                "hash": "abc123",
                "title": "Python Programming",
                "author": "John Smith",
                "year": "2023",
                "language": "English",
                "extension": "pdf",
                "size": "10 MB",
                "filesize": 10485760,
                "cover": "https://example.com/cover.jpg",
                "description": "A comprehensive guide",
            },
            {
                "id": "67890",
                "hash": "def456",
                "title": "Advanced Python",
                "author": "Jane Doe, Bob Wilson",
                "year": "2024",
                "language": "English",
                "extension": "epub",
            },
        ],
    }


class TestSearchAndStore:
    """Tests for search_and_store method."""

    def test_search_and_store_success(
        self,
        search_service: SearchService,
        mock_client: Mock,
        mock_book_repo: Mock,
        mock_author_repo: Mock,
        mock_search_repo: Mock,
        sample_api_response: dict,
    ) -> None:
        """Test successful search and storage."""
        mock_client.search.return_value = sample_api_response
        mock_book_repo.upsert.side_effect = lambda book: book
        mock_author_repo.get_or_create.side_effect = [
            Author(id=1, name="John Smith"),
            Author(id=2, name="Jane Doe"),
            Author(id=3, name="Bob Wilson"),
        ]

        result = search_service.search_and_store(mock_client, "Python", yearFrom=2020)

        assert len(result) == 2
        assert result[0].id == "12345"
        assert result[0].title == "Python Programming"
        assert result[1].id == "67890"

        mock_client.search.assert_called_once_with(message="Python", yearFrom=2020)
        assert mock_book_repo.upsert.call_count == 2
        assert mock_author_repo.get_or_create.call_count == 3
        mock_search_repo.record_search.assert_called_once()

    def test_search_and_store_failure_response(
        self,
        search_service: SearchService,
        mock_client: Mock,
        mock_search_repo: Mock,
    ) -> None:
        """Test search with unsuccessful API response."""
        mock_client.search.return_value = {"success": False}

        result = search_service.search_and_store(mock_client, "Python")

        assert len(result) == 0
        mock_search_repo.record_search.assert_not_called()

    def test_search_and_store_empty_results(
        self,
        search_service: SearchService,
        mock_client: Mock,
        mock_search_repo: Mock,
    ) -> None:
        """Test search with empty results."""
        mock_client.search.return_value = {"success": True, "books": []}

        result = search_service.search_and_store(mock_client, "Nonexistent")

        assert len(result) == 0
        mock_search_repo.record_search.assert_called_once()

    def test_search_and_store_partial_failure(
        self,
        search_service: SearchService,
        mock_client: Mock,
        mock_book_repo: Mock,
        mock_author_repo: Mock,
        sample_api_response: dict,
    ) -> None:
        """Test that one book failure doesn't stop others."""
        mock_client.search.return_value = sample_api_response
        mock_book_repo.upsert.side_effect = [
            Exception("Database error"),
            Book(
                id="67890",
                hash="def456",
                title="Advanced Python",
                year="2024",
                language="English",
                extension="epub",
            ),
        ]

        result = search_service.search_and_store(mock_client, "Python")

        assert len(result) == 1
        assert result[0].id == "67890"


class TestExtractAuthors:
    """Tests for author extraction from strings."""

    def test_extract_authors_comma_separated(self, search_service: SearchService) -> None:
        """Test extracting comma-separated authors."""
        result = search_service._extract_authors("John Smith, Jane Doe, Bob Wilson")
        assert len(result) == 3
        assert "John Smith" in result
        assert "Jane Doe" in result
        assert "Bob Wilson" in result

    def test_extract_authors_and_separated(self, search_service: SearchService) -> None:
        """Test extracting 'and' separated authors."""
        result = search_service._extract_authors("John Smith and Jane Doe")
        assert len(result) == 2
        assert "John Smith" in result
        assert "Jane Doe" in result

    def test_extract_authors_and_case_insensitive(self, search_service: SearchService) -> None:
        """Test 'and' extraction is case insensitive."""
        result = search_service._extract_authors("John Smith AND Jane Doe")
        assert len(result) == 2

    def test_extract_authors_semicolon_separated(self, search_service: SearchService) -> None:
        """Test extracting semicolon-separated authors."""
        result = search_service._extract_authors("John Smith; Jane Doe")
        assert len(result) == 2
        assert "John Smith" in result
        assert "Jane Doe" in result

    def test_extract_authors_ampersand_separated(self, search_service: SearchService) -> None:
        """Test extracting ampersand-separated authors."""
        result = search_service._extract_authors("John Smith & Jane Doe")
        assert len(result) == 2
        assert "John Smith" in result
        assert "Jane Doe" in result

    def test_extract_authors_single(self, search_service: SearchService) -> None:
        """Test extracting single author."""
        result = search_service._extract_authors("John Smith")
        assert len(result) == 1
        assert result[0] == "John Smith"

    def test_extract_authors_empty_string(self, search_service: SearchService) -> None:
        """Test empty author string returns empty list."""
        result = search_service._extract_authors("")
        assert len(result) == 0

    def test_extract_authors_whitespace_only(self, search_service: SearchService) -> None:
        """Test whitespace-only string returns empty list."""
        result = search_service._extract_authors("   ")
        assert len(result) == 0

    def test_extract_authors_with_extra_whitespace(self, search_service: SearchService) -> None:
        """Test authors are trimmed of whitespace."""
        result = search_service._extract_authors("  John Smith  ,  Jane Doe  ")
        assert len(result) == 2
        assert "John Smith" in result
        assert "Jane Doe" in result


class TestStoreBook:
    """Tests for _store_book method."""

    def test_store_book_with_authors(
        self,
        search_service: SearchService,
        mock_book_repo: Mock,
        mock_author_repo: Mock,
    ) -> None:
        """Test storing book with authors."""
        book_data = {
            "id": "12345",
            "hash": "abc123",
            "title": "Test Book",
            "author": "John Smith, Jane Doe",
        }

        mock_book_repo.upsert.return_value = Book(id="12345", hash="abc123", title="Test Book")
        mock_author_repo.get_or_create.side_effect = [
            Author(id=1, name="John Smith"),
            Author(id=2, name="Jane Doe"),
        ]

        result = search_service._store_book(book_data)

        assert result.id == "12345"
        assert mock_book_repo.upsert.call_count == 1
        assert mock_author_repo.get_or_create.call_count == 2
        assert mock_author_repo.link_book_author.call_count == 2

    def test_store_book_without_authors(
        self,
        search_service: SearchService,
        mock_book_repo: Mock,
        mock_author_repo: Mock,
    ) -> None:
        """Test storing book without authors."""
        book_data = {
            "id": "12345",
            "hash": "abc123",
            "title": "Test Book",
        }

        mock_book_repo.upsert.return_value = Book(id="12345", hash="abc123", title="Test Book")

        result = search_service._store_book(book_data)

        assert result.id == "12345"
        mock_author_repo.get_or_create.assert_not_called()
        mock_author_repo.link_book_author.assert_not_called()

    def test_store_book_missing_id(self, search_service: SearchService) -> None:
        """Test storing book without ID raises error."""
        book_data = {"hash": "abc123", "title": "Test Book"}

        with pytest.raises(ValueError) as exc_info:
            search_service._store_book(book_data)

        assert "Missing required book ID or hash" in str(exc_info.value)

    def test_store_book_missing_hash(self, search_service: SearchService) -> None:
        """Test storing book without hash raises error."""
        book_data = {"id": "12345", "title": "Test Book"}

        with pytest.raises(ValueError) as exc_info:
            search_service._store_book(book_data)

        assert "Missing required book ID or hash" in str(exc_info.value)


class TestBookFromApiData:
    """Tests for _book_from_api_data method."""

    def test_book_from_api_data_complete(self, search_service: SearchService) -> None:
        """Test converting complete API data to Book."""
        data = {
            "id": "12345",
            "hash": "abc123",
            "title": "Test Book",
            "year": "2023",
            "publisher": "Publisher",
            "language": "English",
            "extension": "pdf",
            "size": "10 MB",
            "filesize": 10485760,
            "cover": "https://example.com/cover.jpg",
            "description": "Description",
        }

        book = search_service._book_from_api_data(data)

        assert book.id == "12345"
        assert book.hash == "abc123"
        assert book.title == "Test Book"
        assert book.year == "2023"
        assert book.publisher == "Publisher"
        assert book.language == "English"
        assert book.extension == "pdf"
        assert book.size == "10 MB"
        assert book.filesize == 10485760
        assert book.cover_url == "https://example.com/cover.jpg"
        assert book.description == "Description"

    def test_book_from_api_data_minimal(self, search_service: SearchService) -> None:
        """Test converting minimal API data to Book."""
        data = {
            "id": "12345",
            "hash": "abc123",
        }

        book = search_service._book_from_api_data(data)

        assert book.id == "12345"
        assert book.hash == "abc123"
        assert book.title == "Unknown"
        assert book.year is None


class TestLinkAuthorsToBook:
    """Tests for _link_authors_to_book method."""

    def test_link_authors_to_book_success(
        self,
        search_service: SearchService,
        mock_author_repo: Mock,
    ) -> None:
        """Test successfully linking authors to book."""
        mock_author_repo.get_or_create.side_effect = [
            Author(id=1, name="Author One"),
            Author(id=2, name="Author Two"),
        ]

        search_service._link_authors_to_book("12345", ["Author One", "Author Two"])

        assert mock_author_repo.get_or_create.call_count == 2
        assert mock_author_repo.link_book_author.call_count == 2
        mock_author_repo.link_book_author.assert_any_call("12345", 1, order=0)
        mock_author_repo.link_book_author.assert_any_call("12345", 2, order=1)

    def test_link_authors_partial_failure(
        self,
        search_service: SearchService,
        mock_author_repo: Mock,
    ) -> None:
        """Test linking continues even if one author fails."""
        mock_author_repo.get_or_create.side_effect = [
            Author(id=1, name="Author One"),
            Exception("Database error"),
            Author(id=3, name="Author Three"),
        ]

        search_service._link_authors_to_book("12345", ["Author One", "Author Two", "Author Three"])

        assert mock_author_repo.get_or_create.call_count == 3
