"""
Unit tests for the BookRepository class.

Tests cover CRUD operations, search with filters, upsert logic,
parameterized queries, and SQL injection prevention using in-memory SQLite.
"""

import sqlite3
from pathlib import Path

import pytest

from zlibrary_downloader.book_repository import BookRepository
from zlibrary_downloader.db_manager import DatabaseManager
from zlibrary_downloader.models import Book


@pytest.fixture
def db_manager() -> DatabaseManager:
    """Create in-memory database manager with initialized schema."""
    manager = DatabaseManager(db_path=Path(":memory:"))
    manager.initialize_schema()
    return manager


@pytest.fixture
def book_repo(db_manager: DatabaseManager) -> BookRepository:
    """Create BookRepository with in-memory database."""
    return BookRepository(db_manager)


@pytest.fixture
def sample_book() -> Book:
    """Create a sample book for testing."""
    return Book(
        id="12345",
        hash="abc123",
        title="Test Book",
        year="2023",
        publisher="Test Publisher",
        language="English",
        extension="pdf",
        size="10 MB",
        filesize=10485760,
        cover_url="https://example.com/cover.jpg",
        description="A test book",
    )


class TestCreate:
    """Tests for creating books."""

    def test_create_book(self, book_repo: BookRepository, sample_book: Book) -> None:
        """Test creating a new book."""
        result = book_repo.create(sample_book)
        assert result.id == sample_book.id
        assert result.title == sample_book.title

    def test_create_duplicate_raises_error(
        self, book_repo: BookRepository, sample_book: Book
    ) -> None:
        """Test that creating duplicate book raises IntegrityError."""
        book_repo.create(sample_book)
        with pytest.raises(sqlite3.IntegrityError):
            book_repo.create(sample_book)


class TestGetById:
    """Tests for retrieving books by ID."""

    def test_get_existing_book(
        self, book_repo: BookRepository, sample_book: Book
    ) -> None:
        """Test getting an existing book by ID."""
        book_repo.create(sample_book)
        result = book_repo.get_by_id(sample_book.id)
        assert result is not None
        assert result.id == sample_book.id
        assert result.title == sample_book.title

    def test_get_nonexistent_book(self, book_repo: BookRepository) -> None:
        """Test getting a book that doesn't exist returns None."""
        result = book_repo.get_by_id("nonexistent")
        assert result is None


class TestSearch:
    """Tests for searching books."""

    def test_search_all_books(self, book_repo: BookRepository) -> None:
        """Test searching without filters returns all books."""
        book1 = Book(id="1", hash="h1", title="Book One")
        book2 = Book(id="2", hash="h2", title="Book Two")
        book_repo.create(book1)
        book_repo.create(book2)

        results = book_repo.search()
        assert len(results) == 2

    def test_search_by_title_query(self, book_repo: BookRepository) -> None:
        """Test searching by title with LIKE pattern."""
        book1 = Book(id="1", hash="h1", title="Python Programming")
        book2 = Book(id="2", hash="h2", title="Java Programming")
        book_repo.create(book1)
        book_repo.create(book2)

        results = book_repo.search(query="Python")
        assert len(results) == 1
        assert results[0].title == "Python Programming"

    def test_search_by_language(self, book_repo: BookRepository) -> None:
        """Test searching by language filter."""
        book1 = Book(id="1", hash="h1", title="Book 1", language="English")
        book2 = Book(id="2", hash="h2", title="Book 2", language="Spanish")
        book_repo.create(book1)
        book_repo.create(book2)

        results = book_repo.search(language="English")
        assert len(results) == 1
        assert results[0].language == "English"

    def test_search_by_year_range(self, book_repo: BookRepository) -> None:
        """Test searching by year range."""
        book1 = Book(id="1", hash="h1", title="Book 1", year="2020")
        book2 = Book(id="2", hash="h2", title="Book 2", year="2022")
        book3 = Book(id="3", hash="h3", title="Book 3", year="2024")
        book_repo.create(book1)
        book_repo.create(book2)
        book_repo.create(book3)

        results = book_repo.search(year_from="2021", year_to="2023")
        assert len(results) == 1
        assert results[0].year == "2022"

    def test_search_by_extension(self, book_repo: BookRepository) -> None:
        """Test searching by file extension."""
        book1 = Book(id="1", hash="h1", title="Book 1", extension="pdf")
        book2 = Book(id="2", hash="h2", title="Book 2", extension="epub")
        book_repo.create(book1)
        book_repo.create(book2)

        results = book_repo.search(extension="pdf")
        assert len(results) == 1
        assert results[0].extension == "pdf"

    def test_search_with_limit(self, book_repo: BookRepository) -> None:
        """Test search respects limit parameter."""
        for i in range(10):
            book = Book(id=str(i), hash=f"h{i}", title=f"Book {i}")
            book_repo.create(book)

        results = book_repo.search(limit=5)
        assert len(results) == 5

    def test_search_sql_injection_prevention(
        self, book_repo: BookRepository
    ) -> None:
        """Test that search uses parameterized queries to prevent SQL injection."""
        book = Book(id="1", hash="h1", title="Safe Book")
        book_repo.create(book)

        # Attempt SQL injection through title query
        injection = "'; DROP TABLE books; --"
        results = book_repo.search(query=injection)

        # Should treat injection as literal string, not find anything
        assert len(results) == 0

        # Verify table still exists
        results = book_repo.search()
        assert len(results) == 1


class TestUpdate:
    """Tests for updating books."""

    def test_update_existing_book(
        self, book_repo: BookRepository, sample_book: Book
    ) -> None:
        """Test updating an existing book."""
        book_repo.create(sample_book)

        sample_book.title = "Updated Title"
        original_updated_at = sample_book.updated_at

        result = book_repo.update(sample_book)
        assert result.title == "Updated Title"
        assert result.updated_at > original_updated_at

        # Verify in database
        retrieved = book_repo.get_by_id(sample_book.id)
        assert retrieved is not None
        assert retrieved.title == "Updated Title"


class TestUpsert:
    """Tests for upsert operations."""

    def test_upsert_creates_new_book(
        self, book_repo: BookRepository, sample_book: Book
    ) -> None:
        """Test upsert creates book if it doesn't exist."""
        result = book_repo.upsert(sample_book)
        assert result.id == sample_book.id

        retrieved = book_repo.get_by_id(sample_book.id)
        assert retrieved is not None

    def test_upsert_updates_existing_book(
        self, book_repo: BookRepository, sample_book: Book
    ) -> None:
        """Test upsert updates book if it exists."""
        book_repo.create(sample_book)

        sample_book.title = "Updated via Upsert"
        result = book_repo.upsert(sample_book)
        assert result.title == "Updated via Upsert"

        retrieved = book_repo.get_by_id(sample_book.id)
        assert retrieved is not None
        assert retrieved.title == "Updated via Upsert"


class TestDelete:
    """Tests for deleting books."""

    def test_delete_existing_book(
        self, book_repo: BookRepository, sample_book: Book
    ) -> None:
        """Test deleting an existing book."""
        book_repo.create(sample_book)
        result = book_repo.delete(sample_book.id)
        assert result is True

        # Verify deletion
        retrieved = book_repo.get_by_id(sample_book.id)
        assert retrieved is None

    def test_delete_nonexistent_book(self, book_repo: BookRepository) -> None:
        """Test deleting a book that doesn't exist returns False."""
        result = book_repo.delete("nonexistent")
        assert result is False


class TestCount:
    """Tests for counting books."""

    def test_count_all_books(self, book_repo: BookRepository) -> None:
        """Test counting all books."""
        for i in range(5):
            book = Book(id=str(i), hash=f"h{i}", title=f"Book {i}")
            book_repo.create(book)

        count = book_repo.count()
        assert count == 5

    def test_count_with_language_filter(self, book_repo: BookRepository) -> None:
        """Test counting books filtered by language."""
        book1 = Book(id="1", hash="h1", title="Book 1", language="English")
        book2 = Book(id="2", hash="h2", title="Book 2", language="English")
        book3 = Book(id="3", hash="h3", title="Book 3", language="Spanish")
        book_repo.create(book1)
        book_repo.create(book2)
        book_repo.create(book3)

        count = book_repo.count(language="English")
        assert count == 2

    def test_count_with_year_range(self, book_repo: BookRepository) -> None:
        """Test counting books filtered by year range."""
        book1 = Book(id="1", hash="h1", title="Book 1", year="2020")
        book2 = Book(id="2", hash="h2", title="Book 2", year="2022")
        book3 = Book(id="3", hash="h3", title="Book 3", year="2024")
        book_repo.create(book1)
        book_repo.create(book2)
        book_repo.create(book3)

        count = book_repo.count(year_from="2021")
        assert count == 2


class TestRowConversion:
    """Tests for database row conversion."""

    def test_row_to_book_preserves_all_fields(
        self, book_repo: BookRepository, sample_book: Book
    ) -> None:
        """Test that row conversion preserves all book fields."""
        book_repo.create(sample_book)
        retrieved = book_repo.get_by_id(sample_book.id)

        assert retrieved is not None
        assert retrieved.id == sample_book.id
        assert retrieved.hash == sample_book.hash
        assert retrieved.title == sample_book.title
        assert retrieved.year == sample_book.year
        assert retrieved.publisher == sample_book.publisher
        assert retrieved.language == sample_book.language
        assert retrieved.extension == sample_book.extension
        assert retrieved.size == sample_book.size
        assert retrieved.filesize == sample_book.filesize
        assert retrieved.cover_url == sample_book.cover_url
        assert retrieved.description == sample_book.description
