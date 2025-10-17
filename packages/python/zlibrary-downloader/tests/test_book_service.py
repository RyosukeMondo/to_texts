"""
Unit tests for the BookService class.

Tests cover business logic using mocked repository dependencies,
ensuring service layer validation, error handling, and proper
orchestration of repository operations.
"""

from datetime import datetime
from unittest.mock import Mock, MagicMock

import pytest

from zlibrary_downloader.book_service import (
    BookService,
    BookDetails,
    SavedBook,
)
from zlibrary_downloader.book_repository import BookRepository
from zlibrary_downloader.author_repository import AuthorRepository
from zlibrary_downloader.models import Book, Author


@pytest.fixture
def mock_book_repo() -> Mock:
    """Create mock BookRepository."""
    mock = Mock(spec=BookRepository)
    mock.db_manager = MagicMock()
    return mock


@pytest.fixture
def mock_author_repo() -> Mock:
    """Create mock AuthorRepository."""
    return Mock(spec=AuthorRepository)


@pytest.fixture
def book_service(mock_book_repo: Mock, mock_author_repo: Mock) -> BookService:
    """Create BookService with mocked dependencies."""
    return BookService(mock_book_repo, mock_author_repo)


@pytest.fixture
def sample_book() -> Book:
    """Create a sample book for testing."""
    return Book(
        id="12345",
        hash="abc123",
        title="Test Book",
        year="2023",
        language="English",
        extension="pdf",
    )


@pytest.fixture
def sample_authors() -> list[Author]:
    """Create sample authors for testing."""
    return [
        Author(id=1, name="Author One"),
        Author(id=2, name="Author Two"),
    ]


class TestGetBookDetails:
    """Tests for getting book details with authors."""

    def test_get_book_details_success(
        self,
        book_service: BookService,
        mock_book_repo: Mock,
        mock_author_repo: Mock,
        sample_book: Book,
        sample_authors: list[Author],
    ) -> None:
        """Test successfully getting book details."""
        mock_book_repo.get_by_id.return_value = sample_book
        mock_author_repo.get_authors_for_book.return_value = sample_authors

        result = book_service.get_book_details("12345")

        assert isinstance(result, BookDetails)
        assert result.book == sample_book
        assert result.authors == sample_authors
        mock_book_repo.get_by_id.assert_called_once_with("12345")
        mock_author_repo.get_authors_for_book.assert_called_once_with("12345")

    def test_get_book_details_not_found(
        self,
        book_service: BookService,
        mock_book_repo: Mock,
    ) -> None:
        """Test getting details for nonexistent book raises error."""
        mock_book_repo.get_by_id.return_value = None

        with pytest.raises(ValueError) as exc_info:
            book_service.get_book_details("nonexistent")

        assert "Book not found: nonexistent" in str(exc_info.value)
        assert "db browse" in str(exc_info.value)


class TestBrowseBooks:
    """Tests for browsing books with filters."""

    def test_browse_books_no_filters(
        self,
        book_service: BookService,
        mock_book_repo: Mock,
        sample_book: Book,
    ) -> None:
        """Test browsing books without filters."""
        mock_book_repo.search.return_value = [sample_book]

        result = book_service.browse_books()

        assert len(result) == 1
        assert result[0] == sample_book
        mock_book_repo.search.assert_called_once_with(
            query=None,
            language=None,
            year_from=None,
            year_to=None,
            extension=None,
            author=None,
            limit=100,
        )

    def test_browse_books_with_all_filters(
        self,
        book_service: BookService,
        mock_book_repo: Mock,
        sample_book: Book,
    ) -> None:
        """Test browsing with all filters applied."""
        mock_book_repo.search.return_value = [sample_book]

        result = book_service.browse_books(
            query="Python",
            language="English",
            year_from="2020",
            year_to="2023",
            extension="pdf",
            author="Smith",
            limit=50,
        )

        assert len(result) == 1
        mock_book_repo.search.assert_called_once_with(
            query="Python",
            language="English",
            year_from="2020",
            year_to="2023",
            extension="pdf",
            author="Smith",
            limit=50,
        )

    def test_browse_books_invalid_limit_zero(self, book_service: BookService) -> None:
        """Test that zero limit raises error."""
        with pytest.raises(ValueError) as exc_info:
            book_service.browse_books(limit=0)

        assert "greater than 0" in str(exc_info.value)

    def test_browse_books_invalid_limit_negative(self, book_service: BookService) -> None:
        """Test that negative limit raises error."""
        with pytest.raises(ValueError) as exc_info:
            book_service.browse_books(limit=-10)

        assert "greater than 0" in str(exc_info.value)

    def test_browse_books_limit_too_large(self, book_service: BookService) -> None:
        """Test that limit over 1000 raises error."""
        with pytest.raises(ValueError) as exc_info:
            book_service.browse_books(limit=2000)

        assert "cannot exceed 1000" in str(exc_info.value)


class TestSaveBook:
    """Tests for saving books."""

    def test_save_book_success(
        self,
        book_service: BookService,
        mock_book_repo: Mock,
        sample_book: Book,
    ) -> None:
        """Test successfully saving a book."""
        mock_book_repo.get_by_id.return_value = sample_book
        mock_conn = MagicMock()
        mock_book_repo.db_manager.get_connection.return_value = mock_conn

        book_service.save_book("12345", notes="Great book", tags="python,coding", priority=5)

        mock_book_repo.get_by_id.assert_called_once_with("12345")
        mock_conn.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_save_book_not_found(self, book_service: BookService, mock_book_repo: Mock) -> None:
        """Test saving nonexistent book raises error."""
        mock_book_repo.get_by_id.return_value = None

        with pytest.raises(ValueError) as exc_info:
            book_service.save_book("nonexistent")

        assert "Cannot save book nonexistent" in str(exc_info.value)
        assert "book not found" in str(exc_info.value)

    def test_save_book_negative_priority(
        self,
        book_service: BookService,
        mock_book_repo: Mock,
        sample_book: Book,
    ) -> None:
        """Test saving with negative priority raises error."""
        mock_book_repo.get_by_id.return_value = sample_book

        with pytest.raises(ValueError) as exc_info:
            book_service.save_book("12345", priority=-5)

        assert "Priority cannot be negative" in str(exc_info.value)


class TestUnsaveBook:
    """Tests for unsaving books."""

    def test_unsave_book_success(self, book_service: BookService, mock_book_repo: Mock) -> None:
        """Test successfully unsaving a book."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 1
        mock_conn.execute.return_value = mock_cursor
        mock_book_repo.db_manager.get_connection.return_value = mock_conn

        result = book_service.unsave_book("12345")

        assert result is True
        mock_conn.execute.assert_called_once()
        mock_conn.commit.assert_called_once()

    def test_unsave_book_not_saved(self, book_service: BookService, mock_book_repo: Mock) -> None:
        """Test unsaving book that isn't saved returns False."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0
        mock_conn.execute.return_value = mock_cursor
        mock_book_repo.db_manager.get_connection.return_value = mock_conn

        result = book_service.unsave_book("12345")

        assert result is False


class TestGetSavedBooks:
    """Tests for getting saved books."""

    def test_get_saved_books_empty(self, book_service: BookService, mock_book_repo: Mock) -> None:
        """Test getting saved books when none exist."""
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_conn.execute.return_value = mock_cursor
        mock_book_repo.db_manager.get_connection.return_value = mock_conn

        result = book_service.get_saved_books()

        assert len(result) == 0

    def test_get_saved_books_with_data(
        self,
        book_service: BookService,
        mock_book_repo: Mock,
        mock_author_repo: Mock,
    ) -> None:
        """Test getting saved books with data."""
        mock_row = {
            "id": "12345",
            "hash": "abc123",
            "title": "Test Book",
            "year": "2023",
            "publisher": "Publisher",
            "language": "English",
            "extension": "pdf",
            "size": "10 MB",
            "filesize": 10485760,
            "cover_url": "https://example.com/cover.jpg",
            "description": "Description",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "notes": "Great book",
            "tags": "python,coding",
            "priority": 5,
            "saved_at": datetime.now().isoformat(),
        }

        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [mock_row]
        mock_conn.execute.return_value = mock_cursor
        mock_book_repo.db_manager.get_connection.return_value = mock_conn

        mock_author_repo.get_authors_for_book.return_value = [Author(id=1, name="Author One")]

        result = book_service.get_saved_books()

        assert len(result) == 1
        saved_book = result[0]
        assert isinstance(saved_book, SavedBook)
        assert saved_book.book.id == "12345"
        assert saved_book.book.title == "Test Book"
        assert saved_book.notes == "Great book"
        assert saved_book.tags == "python,coding"
        assert saved_book.priority == 5
        assert len(saved_book.authors) == 1
        assert saved_book.authors[0].name == "Author One"
