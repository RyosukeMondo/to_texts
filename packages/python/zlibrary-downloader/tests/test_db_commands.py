"""Unit tests for database command handlers."""

# mypy: disable-error-code="no-untyped-def"

import argparse
from datetime import datetime
from typing import List
from unittest.mock import Mock, patch

import pytest

from zlibrary_downloader.db_commands import (
    db_init_command,
    db_browse_command,
    db_show_command,
    db_save_command,
    db_unsave_command,
    db_saved_command,
    _format_book_row,
    _display_book_details,
    _display_saved_book,
)
from zlibrary_downloader.models import Book, Author
from zlibrary_downloader.book_service import BookDetails, SavedBook


@pytest.fixture
def sample_book() -> Book:
    """Create a sample book for testing."""
    return Book(
        id="123",
        hash="abc123",
        title="Test Book",
        year="2023",
        publisher="Test Publisher",
        language="english",
        extension="pdf",
        size="1.5 MB",
        filesize=1572864,
        cover_url="http://example.com/cover.jpg",
        description="Test description",
        created_at=datetime.now(),
        updated_at=datetime.now(),
    )


@pytest.fixture
def sample_authors() -> List[Author]:
    """Create sample authors for testing."""
    return [
        Author(id=1, name="Author One"),
        Author(id=2, name="Author Two"),
    ]


@pytest.fixture
def sample_book_details(sample_book: Book, sample_authors: List[Author]) -> BookDetails:
    """Create sample book details for testing."""
    return BookDetails(book=sample_book, authors=sample_authors)


@pytest.fixture
def sample_saved_book(sample_book: Book, sample_authors: List[Author]) -> SavedBook:
    """Create sample saved book for testing."""
    return SavedBook(
        book=sample_book,
        authors=sample_authors,
        notes="Test notes",
        tags="tag1,tag2",
        priority=3,
        saved_at="2023-01-01 12:00:00",
    )


class TestDbInitCommand:
    """Tests for db_init_command."""

    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_init_success(self, mock_db_manager, capsys):
        """Test successful database initialization."""
        mock_manager = Mock()
        mock_manager.db_path = "/tmp/test.db"
        mock_db_manager.return_value = mock_manager

        args = argparse.Namespace()
        db_init_command(args)

        mock_manager.initialize_schema.assert_called_once()
        captured = capsys.readouterr()
        assert "Initializing database..." in captured.out
        assert "Database initialized successfully" in captured.out

    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_init_failure(self, mock_db_manager, capsys):
        """Test database initialization failure."""
        mock_manager = Mock()
        mock_manager.initialize_schema.side_effect = RuntimeError("Init failed")
        mock_db_manager.return_value = mock_manager

        args = argparse.Namespace()
        with pytest.raises(RuntimeError):
            db_init_command(args)

        captured = capsys.readouterr()
        assert "Error initializing database" in captured.out


class TestFormatBookRow:
    """Tests for _format_book_row."""

    def test_format_with_authors(self, sample_book, sample_authors):
        """Test formatting book with authors."""
        result = _format_book_row(sample_book, sample_authors)
        assert "ID: 123" in result
        assert "Test Book" in result
        assert "Author One, Author Two" in result
        assert "Year: 2023" in result
        assert "Format: pdf" in result

    def test_format_without_authors(self, sample_book):
        """Test formatting book without authors."""
        result = _format_book_row(sample_book, None)
        assert "ID: 123" in result
        assert "Author: N/A" in result

    def test_format_with_missing_fields(self):
        """Test formatting book with missing optional fields."""
        book = Book(
            id="456",
            hash="def456",
            title="Incomplete Book",
            year=None,
            publisher=None,
            language="english",
            extension=None,
            size=None,
            filesize=None,
            cover_url=None,
            description=None,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        )
        result = _format_book_row(book, [])
        assert "Year: N/A" in result
        assert "Format: N/A" in result


class TestDbBrowseCommand:
    """Tests for db_browse_command."""

    @patch("zlibrary_downloader.db_commands.BookService")
    @patch("zlibrary_downloader.db_commands.AuthorRepository")
    @patch("zlibrary_downloader.db_commands.BookRepository")
    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_browse_with_results(
        self,
        mock_db_manager,
        mock_book_repo,
        mock_author_repo,
        mock_book_service,
        sample_book,
        sample_authors,
        capsys,
    ):
        """Test browsing books with results."""
        args = argparse.Namespace(
            query="test",
            language="english",
            year_from=2020,
            year_to=2023,
            format="pdf",
            author="Author",
            limit=50,
        )

        mock_service = Mock()
        mock_service.browse_books.return_value = [sample_book]
        mock_book_service.return_value = mock_service

        mock_author_instance = Mock()
        mock_author_instance.get_authors_for_book.return_value = sample_authors
        mock_author_repo.return_value = mock_author_instance

        db_browse_command(args)

        mock_service.browse_books.assert_called_once()
        captured = capsys.readouterr()
        assert "Found 1 books" in captured.out
        assert "Test Book" in captured.out

    @patch("zlibrary_downloader.db_commands.BookService")
    @patch("zlibrary_downloader.db_commands.AuthorRepository")
    @patch("zlibrary_downloader.db_commands.BookRepository")
    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_browse_no_results(
        self, mock_db_manager, mock_book_repo, mock_author_repo, mock_book_service, capsys
    ):
        """Test browsing books with no results."""
        args = argparse.Namespace(
            query=None,
            language=None,
            year_from=None,
            year_to=None,
            format=None,
            author=None,
            limit=50,
        )

        mock_service = Mock()
        mock_service.browse_books.return_value = []
        mock_book_service.return_value = mock_service

        db_browse_command(args)

        captured = capsys.readouterr()
        assert "No books found matching your criteria" in captured.out


class TestDisplayBookDetails:
    """Tests for _display_book_details."""

    def test_display_complete_details(self, sample_book_details, capsys):
        """Test displaying complete book details."""
        _display_book_details(sample_book_details)

        captured = capsys.readouterr()
        assert "Book Details" in captured.out
        assert "ID: 123" in captured.out
        assert "Title: Test Book" in captured.out
        assert "Authors: Author One, Author Two" in captured.out
        assert "Year: 2023" in captured.out
        assert "Description: Test description" in captured.out


class TestDbShowCommand:
    """Tests for db_show_command."""

    @patch("zlibrary_downloader.db_commands.BookService")
    @patch("zlibrary_downloader.db_commands.AuthorRepository")
    @patch("zlibrary_downloader.db_commands.BookRepository")
    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_show_existing_book(
        self,
        mock_db_manager,
        mock_book_repo,
        mock_author_repo,
        mock_book_service,
        sample_book_details,
        capsys,
    ):
        """Test showing existing book details."""
        args = argparse.Namespace(book_id=123)

        mock_service = Mock()
        mock_service.get_book_details.return_value = sample_book_details
        mock_book_service.return_value = mock_service

        db_show_command(args)

        mock_service.get_book_details.assert_called_once_with("123")
        captured = capsys.readouterr()
        assert "Book Details" in captured.out

    @patch("zlibrary_downloader.db_commands.BookService")
    @patch("zlibrary_downloader.db_commands.AuthorRepository")
    @patch("zlibrary_downloader.db_commands.BookRepository")
    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_show_nonexistent_book(
        self, mock_db_manager, mock_book_repo, mock_author_repo, mock_book_service, capsys
    ):
        """Test showing nonexistent book."""
        args = argparse.Namespace(book_id=999)

        mock_service = Mock()
        mock_service.get_book_details.side_effect = ValueError("Book not found")
        mock_book_service.return_value = mock_service

        db_show_command(args)

        captured = capsys.readouterr()
        assert "Book not found" in captured.out


class TestDbSaveCommand:
    """Tests for db_save_command."""

    @patch("zlibrary_downloader.db_commands.BookService")
    @patch("zlibrary_downloader.db_commands.AuthorRepository")
    @patch("zlibrary_downloader.db_commands.BookRepository")
    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_save_book_success(
        self, mock_db_manager, mock_book_repo, mock_author_repo, mock_book_service, capsys
    ):
        """Test saving book successfully."""
        args = argparse.Namespace(book_id=123, notes="Test notes", tags="tag1,tag2", priority=3)

        mock_service = Mock()
        mock_book_service.return_value = mock_service

        db_save_command(args)

        mock_service.save_book.assert_called_once_with(
            book_id="123", notes="Test notes", tags="tag1,tag2", priority=3
        )
        captured = capsys.readouterr()
        assert "saved successfully" in captured.out

    @patch("zlibrary_downloader.db_commands.BookService")
    @patch("zlibrary_downloader.db_commands.AuthorRepository")
    @patch("zlibrary_downloader.db_commands.BookRepository")
    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_save_book_not_found(
        self, mock_db_manager, mock_book_repo, mock_author_repo, mock_book_service, capsys
    ):
        """Test saving nonexistent book."""
        args = argparse.Namespace(book_id=999, notes=None, tags=None, priority=None)

        mock_service = Mock()
        mock_service.save_book.side_effect = ValueError("Book not found")
        mock_book_service.return_value = mock_service

        db_save_command(args)

        captured = capsys.readouterr()
        assert "Book not found" in captured.out


class TestDbUnsaveCommand:
    """Tests for db_unsave_command."""

    @patch("zlibrary_downloader.db_commands.BookService")
    @patch("zlibrary_downloader.db_commands.AuthorRepository")
    @patch("zlibrary_downloader.db_commands.BookRepository")
    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_unsave_existing_book(
        self, mock_db_manager, mock_book_repo, mock_author_repo, mock_book_service, capsys
    ):
        """Test unsaving existing saved book."""
        args = argparse.Namespace(book_id=123)

        mock_service = Mock()
        mock_service.unsave_book.return_value = True
        mock_book_service.return_value = mock_service

        db_unsave_command(args)

        mock_service.unsave_book.assert_called_once_with("123")
        captured = capsys.readouterr()
        assert "removed from saved books" in captured.out

    @patch("zlibrary_downloader.db_commands.BookService")
    @patch("zlibrary_downloader.db_commands.AuthorRepository")
    @patch("zlibrary_downloader.db_commands.BookRepository")
    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_unsave_not_saved_book(
        self, mock_db_manager, mock_book_repo, mock_author_repo, mock_book_service, capsys
    ):
        """Test unsaving book that wasn't saved."""
        args = argparse.Namespace(book_id=123)

        mock_service = Mock()
        mock_service.unsave_book.return_value = False
        mock_book_service.return_value = mock_service

        db_unsave_command(args)

        captured = capsys.readouterr()
        assert "was not in saved books" in captured.out


class TestDisplaySavedBook:
    """Tests for _display_saved_book."""

    def test_display_complete_saved_book(self, sample_saved_book, capsys):
        """Test displaying saved book with all metadata."""
        _display_saved_book(sample_saved_book, 1)

        captured = capsys.readouterr()
        assert "1. Test Book" in captured.out
        assert "ID: 123" in captured.out
        assert "Author One, Author Two" in captured.out
        assert "Priority: 3" in captured.out
        assert "Tags: tag1,tag2" in captured.out
        assert "Notes: Test notes" in captured.out


class TestDbSavedCommand:
    """Tests for db_saved_command."""

    @patch("zlibrary_downloader.db_commands.BookService")
    @patch("zlibrary_downloader.db_commands.AuthorRepository")
    @patch("zlibrary_downloader.db_commands.BookRepository")
    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_saved_with_books(
        self,
        mock_db_manager,
        mock_book_repo,
        mock_author_repo,
        mock_book_service,
        sample_saved_book,
        capsys,
    ):
        """Test listing saved books when books exist."""
        args = argparse.Namespace()

        mock_service = Mock()
        mock_service.get_saved_books.return_value = [sample_saved_book]
        mock_book_service.return_value = mock_service

        db_saved_command(args)

        captured = capsys.readouterr()
        assert "Saved Books (1)" in captured.out
        assert "Test Book" in captured.out

    @patch("zlibrary_downloader.db_commands.BookService")
    @patch("zlibrary_downloader.db_commands.AuthorRepository")
    @patch("zlibrary_downloader.db_commands.BookRepository")
    @patch("zlibrary_downloader.db_commands.DatabaseManager")
    def test_saved_no_books(
        self, mock_db_manager, mock_book_repo, mock_author_repo, mock_book_service, capsys
    ):
        """Test listing saved books when none exist."""
        args = argparse.Namespace()

        mock_service = Mock()
        mock_service.get_saved_books.return_value = []
        mock_book_service.return_value = mock_service

        db_saved_command(args)

        captured = capsys.readouterr()
        assert "No saved books found" in captured.out
        assert "Use 'db save" in captured.out
