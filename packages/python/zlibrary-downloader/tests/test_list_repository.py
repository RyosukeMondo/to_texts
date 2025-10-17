"""
Unit tests for the ReadingListRepository class.

Tests cover CRUD operations for reading lists, book membership with position
tracking, parameterized queries, and error handling using in-memory SQLite.
"""

import sqlite3
from pathlib import Path

import pytest

from zlibrary_downloader.db_manager import DatabaseManager
from zlibrary_downloader.list_repository import ReadingListRepository
from zlibrary_downloader.models import Book


@pytest.fixture
def db_manager() -> DatabaseManager:
    """Create in-memory database manager with initialized schema."""
    manager = DatabaseManager(db_path=Path(":memory:"))
    manager.initialize_schema()
    return manager


@pytest.fixture
def list_repo(db_manager: DatabaseManager) -> ReadingListRepository:
    """Create ReadingListRepository with in-memory database."""
    return ReadingListRepository(db_manager)


@pytest.fixture
def sample_books(db_manager: DatabaseManager) -> list[Book]:
    """Create sample books for testing list membership."""
    books = [
        Book(id="1", hash="h1", title="Book One"),
        Book(id="2", hash="h2", title="Book Two"),
        Book(id="3", hash="h3", title="Book Three"),
    ]
    conn = db_manager.get_connection()
    for book in books:
        conn.execute(
            """
            INSERT INTO books (id, hash, title)
            VALUES (?, ?, ?)
            """,
            (book.id, book.hash, book.title),
        )
    conn.commit()
    return books


class TestCreateList:
    """Tests for creating reading lists."""

    def test_create_list_with_name_only(self, list_repo: ReadingListRepository) -> None:
        """Test creating a list with name only."""
        result = list_repo.create_list("To Read")
        assert result.id is not None
        assert result.name == "To Read"
        assert result.description == ""

    def test_create_list_with_description(self, list_repo: ReadingListRepository) -> None:
        """Test creating a list with name and description."""
        result = list_repo.create_list("Favorites", "My favorite books")
        assert result.id is not None
        assert result.name == "Favorites"
        assert result.description == "My favorite books"

    def test_create_duplicate_list_raises_error(self, list_repo: ReadingListRepository) -> None:
        """Test that creating duplicate list name raises IntegrityError."""
        list_repo.create_list("To Read")
        with pytest.raises(sqlite3.IntegrityError):
            list_repo.create_list("To Read")


class TestGetListByName:
    """Tests for retrieving lists by name."""

    def test_get_existing_list(self, list_repo: ReadingListRepository) -> None:
        """Test getting an existing list by name."""
        created = list_repo.create_list("To Read", "Books to read")
        result = list_repo.get_list_by_name("To Read")

        assert result is not None
        assert result.id == created.id
        assert result.name == "To Read"
        assert result.description == "Books to read"

    def test_get_nonexistent_list(self, list_repo: ReadingListRepository) -> None:
        """Test getting a list that doesn't exist returns None."""
        result = list_repo.get_list_by_name("Nonexistent")
        assert result is None


class TestGetListById:
    """Tests for retrieving lists by ID."""

    def test_get_existing_list_by_id(self, list_repo: ReadingListRepository) -> None:
        """Test getting an existing list by ID."""
        created = list_repo.create_list("To Read")
        assert created.id is not None
        result = list_repo.get_list_by_id(created.id)

        assert result is not None
        assert result.id == created.id
        assert result.name == "To Read"

    def test_get_nonexistent_list_by_id(self, list_repo: ReadingListRepository) -> None:
        """Test getting a list that doesn't exist returns None."""
        result = list_repo.get_list_by_id(999)
        assert result is None


class TestListAll:
    """Tests for listing all reading lists."""

    def test_list_all_empty(self, list_repo: ReadingListRepository) -> None:
        """Test listing all lists when none exist."""
        results = list_repo.list_all()
        assert len(results) == 0

    def test_list_all_multiple_lists(self, list_repo: ReadingListRepository) -> None:
        """Test listing all lists returns all in alphabetical order."""
        list_repo.create_list("Classics")
        list_repo.create_list("To Read")
        list_repo.create_list("Favorites")

        results = list_repo.list_all()
        assert len(results) == 3
        # Should be ordered by name
        assert results[0].name == "Classics"
        assert results[1].name == "Favorites"
        assert results[2].name == "To Read"


class TestAddBook:
    """Tests for adding books to lists."""

    def test_add_book_to_list(
        self, list_repo: ReadingListRepository, sample_books: list[Book]
    ) -> None:
        """Test adding a book to a list."""
        reading_list = list_repo.create_list("To Read")
        assert reading_list.id is not None
        list_repo.add_book(reading_list.id, sample_books[0].id)

        books = list_repo.get_books(reading_list.id)
        assert len(books) == 1
        assert books[0].id == sample_books[0].id

    def test_add_multiple_books_maintains_position(
        self, list_repo: ReadingListRepository, sample_books: list[Book]
    ) -> None:
        """Test adding multiple books maintains position order."""
        reading_list = list_repo.create_list("To Read")
        assert reading_list.id is not None

        # Add books in specific order
        for book in sample_books:
            list_repo.add_book(reading_list.id, book.id)

        books = list_repo.get_books(reading_list.id)
        assert len(books) == 3
        # Should maintain insertion order via position
        assert books[0].id == sample_books[0].id
        assert books[1].id == sample_books[1].id
        assert books[2].id == sample_books[2].id

    def test_add_duplicate_book_ignored(
        self, list_repo: ReadingListRepository, sample_books: list[Book]
    ) -> None:
        """Test adding same book twice is silently ignored."""
        reading_list = list_repo.create_list("To Read")
        assert reading_list.id is not None
        list_repo.add_book(reading_list.id, sample_books[0].id)
        list_repo.add_book(reading_list.id, sample_books[0].id)

        books = list_repo.get_books(reading_list.id)
        assert len(books) == 1


class TestRemoveBook:
    """Tests for removing books from lists."""

    def test_remove_existing_book(
        self, list_repo: ReadingListRepository, sample_books: list[Book]
    ) -> None:
        """Test removing a book that exists in the list."""
        reading_list = list_repo.create_list("To Read")
        assert reading_list.id is not None
        list_repo.add_book(reading_list.id, sample_books[0].id)
        list_repo.add_book(reading_list.id, sample_books[1].id)

        result = list_repo.remove_book(reading_list.id, sample_books[0].id)
        assert result is True

        books = list_repo.get_books(reading_list.id)
        assert len(books) == 1
        assert books[0].id == sample_books[1].id

    def test_remove_nonexistent_book(self, list_repo: ReadingListRepository) -> None:
        """Test removing a book not in the list returns False."""
        reading_list = list_repo.create_list("To Read")
        assert reading_list.id is not None
        result = list_repo.remove_book(reading_list.id, "nonexistent")
        assert result is False


class TestGetBooks:
    """Tests for getting books in a list."""

    def test_get_books_empty_list(self, list_repo: ReadingListRepository) -> None:
        """Test getting books from empty list."""
        reading_list = list_repo.create_list("To Read")
        assert reading_list.id is not None
        books = list_repo.get_books(reading_list.id)
        assert len(books) == 0

    def test_get_books_returns_in_position_order(
        self, list_repo: ReadingListRepository, sample_books: list[Book]
    ) -> None:
        """Test that books are returned in position order."""
        reading_list = list_repo.create_list("To Read")
        assert reading_list.id is not None

        for book in sample_books:
            list_repo.add_book(reading_list.id, book.id)

        books = list_repo.get_books(reading_list.id)
        assert len(books) == 3
        # Verify order matches insertion order
        for i, book in enumerate(books):
            assert book.id == sample_books[i].id
            assert book.title == sample_books[i].title


class TestDeleteList:
    """Tests for deleting reading lists."""

    def test_delete_existing_list(self, list_repo: ReadingListRepository) -> None:
        """Test deleting an existing list."""
        reading_list = list_repo.create_list("To Read")
        assert reading_list.id is not None
        result = list_repo.delete_list(reading_list.id)
        assert result is True

        # Verify deletion
        retrieved = list_repo.get_list_by_id(reading_list.id)
        assert retrieved is None

    def test_delete_nonexistent_list(self, list_repo: ReadingListRepository) -> None:
        """Test deleting a list that doesn't exist returns False."""
        result = list_repo.delete_list(999)
        assert result is False

    def test_delete_list_cascades_to_books(
        self, list_repo: ReadingListRepository, sample_books: list[Book]
    ) -> None:
        """Test that deleting a list removes book associations."""
        reading_list = list_repo.create_list("To Read")
        assert reading_list.id is not None
        list_repo.add_book(reading_list.id, sample_books[0].id)

        # Delete the list
        list_repo.delete_list(reading_list.id)

        # Verify list is gone but book still exists
        assert list_repo.get_list_by_id(reading_list.id) is None


class TestRowConversion:
    """Tests for database row conversion."""

    def test_row_to_list_preserves_all_fields(self, list_repo: ReadingListRepository) -> None:
        """Test that row conversion preserves all list fields."""
        created = list_repo.create_list("To Read", "Books I want to read")
        assert created.id is not None
        retrieved = list_repo.get_list_by_id(created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.name == created.name
        assert retrieved.description == created.description
        assert retrieved.created_at == created.created_at

    def test_row_to_book_preserves_fields(
        self, list_repo: ReadingListRepository, sample_books: list[Book]
    ) -> None:
        """Test that book row conversion preserves fields."""
        reading_list = list_repo.create_list("To Read")
        assert reading_list.id is not None
        list_repo.add_book(reading_list.id, sample_books[0].id)

        books = list_repo.get_books(reading_list.id)
        assert len(books) == 1
        assert books[0].id == sample_books[0].id
        assert books[0].title == sample_books[0].title
        assert books[0].hash == sample_books[0].hash
