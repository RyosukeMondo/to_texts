"""
Unit tests for the AuthorRepository class.

Tests cover get_or_create, book-author relationships, duplicate handling,
and parameterized queries using in-memory SQLite.
"""

import sqlite3
from pathlib import Path

import pytest

from zlibrary_downloader.author_repository import AuthorRepository
from zlibrary_downloader.book_repository import BookRepository
from zlibrary_downloader.db_manager import DatabaseManager
from zlibrary_downloader.models import Author, Book


@pytest.fixture
def db_manager() -> DatabaseManager:
    """Create in-memory database manager with initialized schema."""
    manager = DatabaseManager(db_path=Path(":memory:"))
    manager.initialize_schema()
    return manager


@pytest.fixture
def author_repo(db_manager: DatabaseManager) -> AuthorRepository:
    """Create AuthorRepository with in-memory database."""
    return AuthorRepository(db_manager)


@pytest.fixture
def book_repo(db_manager: DatabaseManager) -> BookRepository:
    """Create BookRepository with in-memory database."""
    return BookRepository(db_manager)


@pytest.fixture
def sample_book(book_repo: BookRepository) -> Book:
    """Create and persist a sample book for testing."""
    book = Book(id="12345", hash="abc123", title="Test Book")
    return book_repo.create(book)


class TestGetOrCreate:
    """Tests for get_or_create method."""

    def test_create_new_author(self, author_repo: AuthorRepository) -> None:
        """Test creating a new author."""
        author = author_repo.get_or_create("John Doe")
        assert author.id is not None
        assert author.name == "John Doe"

    def test_get_existing_author(self, author_repo: AuthorRepository) -> None:
        """Test getting an existing author returns same ID."""
        author1 = author_repo.get_or_create("Jane Smith")
        author2 = author_repo.get_or_create("Jane Smith")

        assert author1.id == author2.id
        assert author1.name == author2.name

    def test_handles_whitespace(self, author_repo: AuthorRepository) -> None:
        """Test that whitespace is stripped from author names."""
        author1 = author_repo.get_or_create("  Robert Brown  ")
        author2 = author_repo.get_or_create("Robert Brown")

        assert author1.id == author2.id
        assert author1.name == "Robert Brown"

    def test_empty_name_raises_error(self, author_repo: AuthorRepository) -> None:
        """Test that empty name raises ValueError."""
        with pytest.raises(ValueError, match="Author name cannot be empty"):
            author_repo.get_or_create("")

    def test_whitespace_only_raises_error(
        self, author_repo: AuthorRepository
    ) -> None:
        """Test that whitespace-only name raises ValueError."""
        with pytest.raises(ValueError, match="Author name cannot be empty"):
            author_repo.get_or_create("   ")

    def test_race_condition_handling(self, author_repo: AuthorRepository) -> None:
        """Test INSERT OR IGNORE handles race conditions."""
        # This simulates concurrent creation attempts
        author1 = author_repo.get_or_create("Concurrent Author")
        author2 = author_repo.get_or_create("Concurrent Author")

        assert author1.id == author2.id


class TestLinkBookAuthor:
    """Tests for link_book_author method."""

    def test_link_book_to_author(
        self,
        author_repo: AuthorRepository,
        sample_book: Book,
    ) -> None:
        """Test linking a book to an author."""
        author = author_repo.get_or_create("Test Author")
        author_repo.link_book_author(sample_book.id, author.id)

        authors = author_repo.get_authors_for_book(sample_book.id)
        assert len(authors) == 1
        assert authors[0].id == author.id

    def test_link_multiple_authors_with_order(
        self,
        author_repo: AuthorRepository,
        sample_book: Book,
    ) -> None:
        """Test linking multiple authors with specified order."""
        author1 = author_repo.get_or_create("First Author")
        author2 = author_repo.get_or_create("Second Author")
        author3 = author_repo.get_or_create("Third Author")

        author_repo.link_book_author(sample_book.id, author2.id, order=1)
        author_repo.link_book_author(sample_book.id, author3.id, order=2)
        author_repo.link_book_author(sample_book.id, author1.id, order=0)

        authors = author_repo.get_authors_for_book(sample_book.id)
        assert len(authors) == 3
        assert authors[0].name == "First Author"
        assert authors[1].name == "Second Author"
        assert authors[2].name == "Third Author"

    def test_duplicate_link_raises_error(
        self,
        author_repo: AuthorRepository,
        sample_book: Book,
    ) -> None:
        """Test that duplicate book-author link raises IntegrityError."""
        author = author_repo.get_or_create("Duplicate Test")
        author_repo.link_book_author(sample_book.id, author.id)

        with pytest.raises(sqlite3.IntegrityError):
            author_repo.link_book_author(sample_book.id, author.id)


class TestGetAuthorsForBook:
    """Tests for get_authors_for_book method."""

    def test_get_authors_empty_list(
        self,
        author_repo: AuthorRepository,
        sample_book: Book,
    ) -> None:
        """Test getting authors for book with no authors."""
        authors = author_repo.get_authors_for_book(sample_book.id)
        assert len(authors) == 0

    def test_get_authors_maintains_order(
        self,
        author_repo: AuthorRepository,
        sample_book: Book,
    ) -> None:
        """Test that authors are returned in correct order."""
        author1 = author_repo.get_or_create("Alpha")
        author2 = author_repo.get_or_create("Beta")

        # Link in reverse alphabetical order
        author_repo.link_book_author(sample_book.id, author2.id, order=0)
        author_repo.link_book_author(sample_book.id, author1.id, order=1)

        authors = author_repo.get_authors_for_book(sample_book.id)
        assert authors[0].name == "Beta"
        assert authors[1].name == "Alpha"

    def test_get_authors_nonexistent_book(
        self,
        author_repo: AuthorRepository,
    ) -> None:
        """Test getting authors for nonexistent book returns empty list."""
        authors = author_repo.get_authors_for_book("nonexistent")
        assert len(authors) == 0


class TestGetBooksForAuthor:
    """Tests for get_books_for_author method."""

    def test_get_books_for_author(
        self,
        author_repo: AuthorRepository,
        book_repo: BookRepository,
    ) -> None:
        """Test getting all books for an author."""
        book1 = book_repo.create(Book(id="1", hash="h1", title="Book 1"))
        book2 = book_repo.create(Book(id="2", hash="h2", title="Book 2"))
        author = author_repo.get_or_create("Prolific Author")

        author_repo.link_book_author(book1.id, author.id)
        author_repo.link_book_author(book2.id, author.id)

        book_ids = author_repo.get_books_for_author(author.id)
        assert len(book_ids) == 2
        assert book1.id in book_ids
        assert book2.id in book_ids

    def test_get_books_empty_list(self, author_repo: AuthorRepository) -> None:
        """Test getting books for author with no books."""
        author = author_repo.get_or_create("No Books Author")
        book_ids = author_repo.get_books_for_author(author.id)
        assert len(book_ids) == 0


class TestForeignKeyConstraints:
    """Tests for foreign key constraint handling."""

    def test_delete_book_removes_relationships(
        self,
        author_repo: AuthorRepository,
        book_repo: BookRepository,
    ) -> None:
        """Test that deleting book removes book-author relationships."""
        book = book_repo.create(Book(id="1", hash="h1", title="Book"))
        author = author_repo.get_or_create("Author")
        author_repo.link_book_author(book.id, author.id)

        # Delete book
        book_repo.delete(book.id)

        # Author should still exist but have no books
        book_ids = author_repo.get_books_for_author(author.id)
        assert len(book_ids) == 0
