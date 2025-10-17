"""
Unit tests for the DownloadRepository class.

Tests cover recording downloads, querying history with filters,
and SQL injection prevention using in-memory SQLite.
"""

from pathlib import Path

import pytest

from zlibrary_downloader.book_repository import BookRepository
from zlibrary_downloader.db_manager import DatabaseManager
from zlibrary_downloader.download_repository import DownloadRepository
from zlibrary_downloader.models import Book


@pytest.fixture
def db_manager() -> DatabaseManager:
    """Create in-memory database manager with initialized schema."""
    manager = DatabaseManager(db_path=Path(":memory:"))
    manager.initialize_schema()
    return manager


@pytest.fixture
def download_repo(db_manager: DatabaseManager) -> DownloadRepository:
    """Create DownloadRepository with in-memory database."""
    return DownloadRepository(db_manager)


@pytest.fixture
def book_repo(db_manager: DatabaseManager) -> BookRepository:
    """Create BookRepository with in-memory database."""
    return BookRepository(db_manager)


@pytest.fixture
def sample_book(book_repo: BookRepository) -> Book:
    """Create and persist a sample book for testing."""
    book = Book(id="12345", hash="abc123", title="Test Book")
    book_repo.create(book)
    return book


class TestRecordDownload:
    """Tests for recording downloads."""

    def test_record_download_basic(
        self, download_repo: DownloadRepository, sample_book: Book
    ) -> None:
        """Test recording a basic download."""
        result = download_repo.record_download(
            book_id=sample_book.id,
            filename="test.pdf",
            file_path="/downloads/test.pdf",
        )

        assert result.id is not None
        assert result.book_id == sample_book.id
        assert result.filename == "test.pdf"
        assert result.file_path == "/downloads/test.pdf"
        assert result.status == "completed"

    def test_record_download_with_all_fields(
        self, download_repo: DownloadRepository, sample_book: Book
    ) -> None:
        """Test recording download with all optional fields."""
        result = download_repo.record_download(
            book_id=sample_book.id,
            filename="test.pdf",
            file_path="/downloads/test.pdf",
            credential_id=42,
            file_size=1048576,
            status="completed",
        )

        assert result.credential_id == 42
        assert result.file_size == 1048576
        assert result.status == "completed"
        assert result.error_msg is None

    def test_record_failed_download(
        self, download_repo: DownloadRepository, sample_book: Book
    ) -> None:
        """Test recording a failed download with error message."""
        result = download_repo.record_download(
            book_id=sample_book.id,
            filename="test.pdf",
            file_path="/downloads/test.pdf",
            status="failed",
            error_msg="Network timeout",
        )

        assert result.status == "failed"
        assert result.error_msg == "Network timeout"


class TestGetHistory:
    """Tests for retrieving download history."""

    def test_get_history_empty(self, download_repo: DownloadRepository) -> None:
        """Test getting history when no downloads exist."""
        result = download_repo.get_history()
        assert len(result) == 0

    def test_get_history_all_downloads(
        self, download_repo: DownloadRepository, sample_book: Book
    ) -> None:
        """Test getting all download history."""
        download_repo.record_download(
            book_id=sample_book.id, filename="file1.pdf", file_path="/d/file1.pdf"
        )
        download_repo.record_download(
            book_id=sample_book.id, filename="file2.pdf", file_path="/d/file2.pdf"
        )

        result = download_repo.get_history()
        assert len(result) == 2

    def test_get_history_ordered_newest_first(
        self, download_repo: DownloadRepository, sample_book: Book
    ) -> None:
        """Test that history is returned newest first."""
        download_repo.record_download(
            book_id=sample_book.id, filename="old.pdf", file_path="/d/old.pdf"
        )
        download_repo.record_download(
            book_id=sample_book.id, filename="new.pdf", file_path="/d/new.pdf"
        )

        result = download_repo.get_history()
        assert result[0].filename == "new.pdf"
        assert result[1].filename == "old.pdf"

    def test_get_history_with_limit(
        self, download_repo: DownloadRepository, sample_book: Book
    ) -> None:
        """Test limiting number of history results."""
        for i in range(10):
            download_repo.record_download(
                book_id=sample_book.id,
                filename=f"file{i}.pdf",
                file_path=f"/d/file{i}.pdf",
            )

        result = download_repo.get_history(limit=5)
        assert len(result) == 5

    def test_get_history_filter_by_credential(
        self,
        download_repo: DownloadRepository,
        sample_book: Book,
        book_repo: BookRepository,
    ) -> None:
        """Test filtering history by credential ID."""
        book2 = Book(id="67890", hash="def456", title="Book 2")
        book_repo.create(book2)

        download_repo.record_download(
            book_id=sample_book.id,
            filename="cred1.pdf",
            file_path="/d/cred1.pdf",
            credential_id=1,
        )
        download_repo.record_download(
            book_id=book2.id,
            filename="cred2.pdf",
            file_path="/d/cred2.pdf",
            credential_id=2,
        )

        result = download_repo.get_history(credential_id=1)
        assert len(result) == 1
        assert result[0].credential_id == 1


class TestGetForBook:
    """Tests for getting downloads for a specific book."""

    def test_get_for_book_empty(self, download_repo: DownloadRepository, sample_book: Book) -> None:
        """Test getting downloads for book with no downloads."""
        result = download_repo.get_for_book(sample_book.id)
        assert len(result) == 0

    def test_get_for_book_multiple_downloads(
        self,
        download_repo: DownloadRepository,
        sample_book: Book,
        book_repo: BookRepository,
    ) -> None:
        """Test getting multiple downloads for same book."""
        book2 = Book(id="67890", hash="def456", title="Book 2")
        book_repo.create(book2)

        download_repo.record_download(
            book_id=sample_book.id, filename="v1.pdf", file_path="/d/v1.pdf"
        )
        download_repo.record_download(
            book_id=sample_book.id, filename="v2.pdf", file_path="/d/v2.pdf"
        )
        download_repo.record_download(
            book_id=book2.id, filename="other.pdf", file_path="/d/other.pdf"
        )

        result = download_repo.get_for_book(sample_book.id)
        assert len(result) == 2
        assert all(d.book_id == sample_book.id for d in result)


class TestRowConversion:
    """Tests for database row conversion."""

    def test_row_to_download_preserves_all_fields(
        self, download_repo: DownloadRepository, sample_book: Book
    ) -> None:
        """Test that row conversion preserves all download fields."""
        original = download_repo.record_download(
            book_id=sample_book.id,
            filename="test.pdf",
            file_path="/downloads/test.pdf",
            credential_id=42,
            file_size=1048576,
            status="completed",
        )

        retrieved = download_repo.get_for_book(sample_book.id)[0]

        assert retrieved.id == original.id
        assert retrieved.book_id == original.book_id
        assert retrieved.filename == original.filename
        assert retrieved.file_path == original.file_path
        assert retrieved.credential_id == original.credential_id
        assert retrieved.file_size == original.file_size
        assert retrieved.status == original.status
        assert retrieved.error_msg == original.error_msg
