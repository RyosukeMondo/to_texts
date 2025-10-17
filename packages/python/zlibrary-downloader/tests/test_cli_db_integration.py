"""
Integration tests for CLI database operations.

Tests end-to-end workflows with database features:
- Search with --save-db stores books and authors
- Browse database with various filters
- Show book displays complete details
- Save/unsave books with metadata
- Create and manage reading lists
- Download tracking records correctly
- Export/import functionality

Uses temp database and mocked Zlibrary client for isolated testing.
Target: >80% coverage of integration paths
"""

import argparse
import json
import os
from pathlib import Path
from typing import Any, Dict
from unittest.mock import Mock, patch

import pytest

from zlibrary_downloader import db_commands
from zlibrary_downloader.db_manager import DatabaseManager
from zlibrary_downloader.book_repository import BookRepository
from zlibrary_downloader.author_repository import AuthorRepository
from zlibrary_downloader.search_service import SearchService
from zlibrary_downloader.models import Book


@pytest.fixture
def temp_db_path(tmp_path: Path) -> str:
    """Create a temporary database path for testing."""
    db_file = tmp_path / "test_books.db"
    return str(db_file)


@pytest.fixture
def sample_search_results() -> list[Dict[str, Any]]:
    """Provide sample search results for testing."""
    return [
        {
            "id": "12345",
            "title": "Python Testing Guide",
            "author": "John Doe, Jane Smith",
            "year": "2024",
            "publisher": "Tech Publisher",
            "language": "english",
            "extension": "pdf",
            "size": "2.5 MB",
        },
        {
            "id": "67890",
            "title": "Advanced SQLite",
            "author": "Bob Wilson",
            "year": "2023",
            "publisher": "DB Press",
            "language": "english",
            "extension": "epub",
            "size": "1.8 MB",
        },
    ]


class TestSearchAndStore:
    """Test search with database storage integration."""

    def test_search_with_save_db_stores_books(
        self, temp_db_path: str, sample_search_results: list[Dict[str, Any]]
    ):
        """Test search with --save-db flag stores results in database."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            # Initialize database
            db_manager = DatabaseManager()
            db_manager.initialize_schema()

            # Mock client - add hash to results
            enhanced_results = []
            for book in sample_search_results:
                book_copy = book.copy()
                book_copy["hash"] = f"hash_{book['id']}"
                enhanced_results.append(book_copy)

            mock_client = Mock()
            mock_client.search.return_value = {"success": True, "books": enhanced_results}

            # Create service and search
            book_repo = BookRepository(db_manager)
            author_repo = AuthorRepository(db_manager)
            search_history_repo = Mock()  # Mock search history
            search_service = SearchService(book_repo, author_repo, search_history_repo)

            results = search_service.search_and_store(mock_client, "python testing")

            # Verify books stored
            assert len(results) == 2
            stored_books = book_repo.search()
            assert len(stored_books) == 2

            # Verify authors extracted and stored
            book1_authors = author_repo.get_authors_for_book("12345")
            assert len(book1_authors) == 2
            assert book1_authors[0].name == "John Doe"
            assert book1_authors[1].name == "Jane Smith"

            book2_authors = author_repo.get_authors_for_book("67890")
            assert len(book2_authors) == 1
            assert book2_authors[0].name == "Bob Wilson"


class TestBrowseDatabase:
    """Test database browsing with filters."""

    def test_browse_shows_all_books(self, temp_db_path: str, capsys):
        """Test browse command displays stored books."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            # Setup database with books
            db_manager = DatabaseManager()
            db_manager.initialize_schema()
            book_repo = BookRepository(db_manager)
            author_repo = AuthorRepository(db_manager)

            # Add test books
            book1 = Book(
                id="1",
                hash="hash1",
                title="Test Book 1",
                year="2024",
                language="english",
                extension="pdf",
            )
            book2 = Book(
                id="2",
                hash="hash2",
                title="Test Book 2",
                year="2023",
                language="spanish",
                extension="epub",
            )
            book_repo.create(book1)
            book_repo.create(book2)

            # Add authors
            author1 = author_repo.get_or_create("Author One")
            author_repo.link_book_author("1", author1.id, 0)

            # Test browse command
            args = argparse.Namespace(
                query=None,
                language=None,
                year_from=None,
                year_to=None,
                format=None,
                author=None,
                limit=50,
            )
            db_commands.db_browse_command(args)

            captured = capsys.readouterr()
            assert "Found 2 books" in captured.out
            assert "Test Book 1" in captured.out
            assert "Test Book 2" in captured.out

    def test_browse_with_language_filter(self, temp_db_path: str, capsys):
        """Test browse with language filter."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()
            book_repo = BookRepository(db_manager)

            book1 = Book(
                id="1", hash="hash1", title="English Book", language="english", extension="pdf"
            )
            book2 = Book(
                id="2", hash="hash2", title="Spanish Book", language="spanish", extension="pdf"
            )
            book_repo.create(book1)
            book_repo.create(book2)

            args = argparse.Namespace(
                query=None,
                language="english",
                year_from=None,
                year_to=None,
                format=None,
                author=None,
                limit=50,
            )
            db_commands.db_browse_command(args)

            captured = capsys.readouterr()
            assert "Found 1 books" in captured.out
            assert "English Book" in captured.out
            assert "Spanish Book" not in captured.out


class TestShowBookDetails:
    """Test showing detailed book information."""

    def test_show_displays_complete_details(self, temp_db_path: str, capsys):
        """Test show command displays book with all details."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()
            book_repo = BookRepository(db_manager)
            author_repo = AuthorRepository(db_manager)

            book = Book(
                id="123",
                hash="hash123",
                title="Complete Book",
                year="2024",
                publisher="Test Pub",
                language="english",
                extension="pdf",
                size="2.5 MB",
                description="A test book",
            )
            book_repo.create(book)

            author = author_repo.get_or_create("Test Author")
            author_repo.link_book_author("123", author.id, 0)

            args = argparse.Namespace(book_id="123")
            db_commands.db_show_command(args)

            captured = capsys.readouterr()
            assert "Complete Book" in captured.out
            assert "Test Author" in captured.out
            assert "2024" in captured.out
            assert "Test Pub" in captured.out

    def test_show_nonexistent_book_shows_error(self, temp_db_path: str, capsys):
        """Test show command handles nonexistent book gracefully."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()

            args = argparse.Namespace(book_id="nonexistent")
            db_commands.db_show_command(args)

            captured = capsys.readouterr()
            assert "❌" in captured.out
            assert "not found" in captured.out.lower()


class TestSaveUnsaveBooks:
    """Test saving and unsaving books functionality."""

    def test_save_book_with_metadata(self, temp_db_path: str, capsys):
        """Test saving book with notes, tags, and priority."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()
            book_repo = BookRepository(db_manager)

            book = Book(id="123", hash="hash123", title="Book to Save", extension="pdf")
            book_repo.create(book)

            args = argparse.Namespace(
                book_id="123", notes="Important read", tags="python,testing", priority=5
            )
            db_commands.db_save_command(args)

            captured = capsys.readouterr()
            assert "saved successfully" in captured.out

    def test_list_saved_books(self, temp_db_path: str, capsys):
        """Test listing saved books shows metadata."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()
            book_repo = BookRepository(db_manager)

            book = Book(id="123", hash="hash123", title="Saved Book", extension="pdf")
            book_repo.create(book)

            # Save book
            conn = db_manager.get_connection()
            conn.execute(
                "INSERT INTO saved_books (book_id, notes, tags, priority) " "VALUES (?, ?, ?, ?)",
                ("123", "Test notes", "tag1,tag2", 3),
            )
            conn.commit()

            args = argparse.Namespace()
            db_commands.db_saved_command(args)

            captured = capsys.readouterr()
            assert "Saved Book" in captured.out
            assert "Test notes" in captured.out
            assert "tag1,tag2" in captured.out
            assert "Priority: 3" in captured.out

    def test_unsave_book_removes_from_collection(self, temp_db_path: str, capsys):
        """Test unsaving book removes it from saved collection."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()
            book_repo = BookRepository(db_manager)

            book = Book(id="123", hash="hash123", title="Book", extension="pdf")
            book_repo.create(book)

            conn = db_manager.get_connection()
            conn.execute("INSERT INTO saved_books (book_id) VALUES (?)", ("123",))
            conn.commit()

            args = argparse.Namespace(book_id="123")
            db_commands.db_unsave_command(args)

            captured = capsys.readouterr()
            assert "removed from saved books" in captured.out


class TestReadingLists:
    """Test reading list management."""

    def test_create_list(self, temp_db_path: str, capsys):
        """Test creating reading list."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()

            args = argparse.Namespace(name="My List", description="Test list")
            db_commands.db_list_create_command(args)

            captured = capsys.readouterr()
            assert "Created reading list: My List" in captured.out

    def test_add_book_to_list(self, temp_db_path: str, capsys):
        """Test adding book to reading list."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()
            book_repo = BookRepository(db_manager)

            # Create book and list
            book = Book(id="123", hash="hash123", title="Book", extension="pdf")
            book_repo.create(book)

            conn = db_manager.get_connection()
            conn.execute("INSERT INTO reading_lists (name) VALUES (?)", ("My List",))
            conn.commit()

            args = argparse.Namespace(name="My List", book_id="123")
            db_commands.db_list_add_command(args)

            captured = capsys.readouterr()
            assert "Added book 123 to list 'My List'" in captured.out

    def test_show_list_with_books(self, temp_db_path: str, capsys):
        """Test showing reading list displays books."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()
            book_repo = BookRepository(db_manager)

            book = Book(id="123", hash="hash123", title="List Book", extension="pdf")
            book_repo.create(book)

            conn = db_manager.get_connection()
            cursor = conn.execute(
                "INSERT INTO reading_lists (name, description) VALUES (?, ?)",
                ("Test List", "For testing"),
            )
            list_id = cursor.lastrowid
            conn.execute(
                "INSERT INTO list_books (list_id, book_id, position) " "VALUES (?, ?, ?)",
                (list_id, "123", 1),
            )
            conn.commit()

            args = argparse.Namespace(name="Test List")
            db_commands.db_list_show_command(args)

            captured = capsys.readouterr()
            assert "Test List" in captured.out
            assert "For testing" in captured.out
            assert "List Book" in captured.out


class TestExportImport:
    """Test export and import functionality."""

    def test_export_to_json(self, temp_db_path: str, tmp_path: Path):
        """Test exporting books to JSON file."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()
            book_repo = BookRepository(db_manager)
            author_repo = AuthorRepository(db_manager)

            book = Book(
                id="123",
                hash="hash123",
                title="Export Book",
                year="2024",
                extension="pdf",
                language="english",
            )
            book_repo.create(book)

            author = author_repo.get_or_create("Export Author")
            author_repo.link_book_author("123", author.id, 0)

            export_file = tmp_path / "export.json"
            args = argparse.Namespace(format="json", output=str(export_file))
            db_commands.db_export_command(args)

            # Verify file created and contents
            assert export_file.exists()
            with open(export_file, "r") as f:
                data = json.load(f)
            assert len(data) == 1
            assert data[0]["title"] == "Export Book"
            assert "Export Author" in data[0]["authors"]

    def test_import_from_json(self, temp_db_path: str, tmp_path: Path, capsys):
        """Test importing books from JSON file."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()

            # Create import file
            import_data = [
                {
                    "id": "999",
                    "hash": "hash999",
                    "title": "Imported Book",
                    "year": "2024",
                    "language": "english",
                    "extension": "pdf",
                    "authors": ["Import Author 1", "Import Author 2"],
                }
            ]
            import_file = tmp_path / "import.json"
            with open(import_file, "w") as f:
                json.dump(import_data, f)

            args = argparse.Namespace(input=str(import_file))
            db_commands.db_import_command(args)

            # Verify import
            book_repo = BookRepository(db_manager)
            author_repo = AuthorRepository(db_manager)

            book = book_repo.get_by_id("999")
            assert book is not None
            assert book.title == "Imported Book"

            authors = author_repo.get_authors_for_book("999")
            assert len(authors) == 2

            captured = capsys.readouterr()
            assert "Successfully imported 1 books" in captured.out


class TestDatabaseUtilities:
    """Test database utility commands."""

    def test_init_command(self, temp_db_path: str, capsys):
        """Test database initialization command."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            args = argparse.Namespace()
            db_commands.db_init_command(args)

            captured = capsys.readouterr()
            assert "initialized successfully" in captured.out
            assert Path(temp_db_path).exists()

    def test_stats_command(self, temp_db_path: str, capsys):
        """Test database statistics display."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()
            book_repo = BookRepository(db_manager)

            # Add some books
            book1 = Book(id="1", hash="hash1", title="Book 1", language="english", extension="pdf")
            book2 = Book(id="2", hash="hash2", title="Book 2", language="spanish", extension="epub")
            book_repo.create(book1)
            book_repo.create(book2)

            args = argparse.Namespace()
            db_commands.db_stats_command(args)

            captured = capsys.readouterr()
            assert "Database Statistics" in captured.out
            assert "Total books: 2" in captured.out
            assert "Top languages:" in captured.out

    def test_vacuum_command(self, temp_db_path: str, capsys):
        """Test database vacuum/optimize command."""
        with patch.dict(os.environ, {"ZLIBRARY_DB_PATH": temp_db_path}):
            db_manager = DatabaseManager()
            db_manager.initialize_schema()

            args = argparse.Namespace()
            db_commands.db_vacuum_command(args)

            captured = capsys.readouterr()
            assert "Optimizing database" in captured.out
            assert "optimized successfully" in captured.out
