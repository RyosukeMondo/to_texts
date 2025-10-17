"""
Unit tests for the DatabaseManager class.

Tests cover connection management, schema initialization, transaction support,
error handling, and cleanup using in-memory SQLite for fast testing.
"""

import sqlite3
from pathlib import Path
from unittest.mock import patch

import pytest

from zlibrary_downloader.db_manager import DatabaseManager
from zlibrary_downloader import schema


class TestDatabaseManagerInitialization:
    """Tests for DatabaseManager initialization."""

    def test_init_with_default_path(self) -> None:
        """Test initialization with default database path."""
        manager = DatabaseManager()
        expected_path = Path.home() / ".zlibrary" / "books.db"
        assert manager.db_path == expected_path
        assert manager.connection is None

    def test_init_with_custom_path(self, tmp_path: Path) -> None:
        """Test initialization with custom database path."""
        db_path = tmp_path / "custom.db"
        manager = DatabaseManager(db_path=db_path)
        assert manager.db_path == db_path
        assert manager.connection is None

    def test_init_with_env_var(self, tmp_path: Path) -> None:
        """Test initialization with ZLIBRARY_DB_PATH environment variable."""
        db_path = tmp_path / "env.db"
        with patch.dict("os.environ", {"ZLIBRARY_DB_PATH": str(db_path)}):
            manager = DatabaseManager()
            assert manager.db_path == db_path


class TestConnectionManagement:
    """Tests for database connection management."""

    def test_get_connection_creates_new_connection(self) -> None:
        """Test that get_connection creates new in-memory connection."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        conn = manager.get_connection()
        assert conn is not None
        assert isinstance(conn, sqlite3.Connection)
        assert manager.connection is conn

    def test_get_connection_returns_existing(self) -> None:
        """Test that get_connection returns existing connection."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        conn1 = manager.get_connection()
        conn2 = manager.get_connection()
        assert conn1 is conn2

    def test_get_connection_enables_foreign_keys(self) -> None:
        """Test that foreign key constraints are enabled."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        conn = manager.get_connection()
        cursor = conn.execute("PRAGMA foreign_keys")
        result = cursor.fetchone()
        assert result[0] == 1  # Foreign keys enabled

    def test_get_connection_enables_wal_mode(self) -> None:
        """Test that WAL mode is enabled."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        conn = manager.get_connection()
        cursor = conn.execute("PRAGMA journal_mode")
        result = cursor.fetchone()
        # In-memory database may use memory mode instead
        assert result[0] in ("wal", "memory")

    def test_get_connection_sets_row_factory(self) -> None:
        """Test that row factory is set to sqlite3.Row."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        conn = manager.get_connection()
        assert conn.row_factory == sqlite3.Row

    def test_close_connection(self) -> None:
        """Test closing database connection."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        manager.get_connection()
        assert manager.connection is not None

        manager.close()
        assert manager.connection is None


class TestSchemaInitialization:
    """Tests for database schema initialization."""

    def test_initialize_schema_creates_all_tables(self) -> None:
        """Test that initialize_schema creates all tables."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        manager.initialize_schema()

        conn = manager.get_connection()
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {row[0] for row in cursor.fetchall()}

        expected_tables = {
            "schema_version",
            "books",
            "authors",
            "book_authors",
            "reading_lists",
            "list_books",
            "saved_books",
            "downloads",
            "search_history",
        }
        assert expected_tables.issubset(tables)

    def test_initialize_schema_creates_indexes(self) -> None:
        """Test that initialize_schema creates all indexes."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        manager.initialize_schema()

        conn = manager.get_connection()
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
        indexes = {row[0] for row in cursor.fetchall()}

        # Check for expected indexes
        assert "idx_books_title" in indexes
        assert "idx_books_language" in indexes
        assert "idx_books_year" in indexes
        assert "idx_downloads_book_id" in indexes

    def test_initialize_schema_records_version(self) -> None:
        """Test that schema version is recorded."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        manager.initialize_schema()

        conn = manager.get_connection()
        cursor = conn.execute("SELECT version FROM schema_version")
        result = cursor.fetchone()
        assert result[0] == schema.SCHEMA_VERSION

    def test_initialize_schema_is_idempotent(self) -> None:
        """Test that schema initialization can be called multiple times."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        manager.initialize_schema()
        manager.initialize_schema()  # Should not raise

        conn = manager.get_connection()
        cursor = conn.execute("SELECT COUNT(*) FROM schema_version")
        result = cursor.fetchone()
        assert result[0] == 1  # Only one version record


class TestTransactionSupport:
    """Tests for transaction support."""

    def test_execute_transaction_commits_on_success(self) -> None:
        """Test that execute_transaction commits on success."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        manager.initialize_schema()

        def insert_book(conn: sqlite3.Connection) -> str:
            conn.execute(
                "INSERT INTO books (id, hash, title) VALUES (?, ?, ?)", ("1", "hash1", "Test Book")
            )
            return "success"

        result = manager.execute_transaction(insert_book)
        assert result == "success"

        # Verify data was committed
        conn = manager.get_connection()
        cursor = conn.execute("SELECT title FROM books WHERE id = ?", ("1",))
        row = cursor.fetchone()
        assert row[0] == "Test Book"

    def test_execute_transaction_rollback_on_error(self) -> None:
        """Test that execute_transaction rolls back on error."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        manager.initialize_schema()

        def failing_insert(conn: sqlite3.Connection) -> None:
            conn.execute(
                "INSERT INTO books (id, hash, title) VALUES (?, ?, ?)", ("1", "hash1", "Test Book")
            )
            raise ValueError("Test error")

        with pytest.raises(ValueError, match="Test error"):
            manager.execute_transaction(failing_insert)

        # Verify data was rolled back
        conn = manager.get_connection()
        cursor = conn.execute("SELECT COUNT(*) FROM books")
        result = cursor.fetchone()
        assert result[0] == 0

    def test_execute_transaction_returns_value(self) -> None:
        """Test that execute_transaction returns function value."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        manager.initialize_schema()

        def get_count(conn: sqlite3.Connection) -> int:
            cursor = conn.execute("SELECT COUNT(*) FROM books")
            result = cursor.fetchone()
            return int(result[0]) if result else 0

        count = manager.execute_transaction(get_count)
        assert count == 0


class TestErrorHandling:
    """Tests for error handling scenarios."""

    def test_get_connection_raises_on_invalid_path(self) -> None:
        """Test that get_connection raises RuntimeError on invalid path."""
        # Use an invalid path that will cause sqlite3.connect to fail
        db_path = Path("/invalid/path/that/does/not/exist/books.db")

        manager = DatabaseManager(db_path=db_path)

        # Mock mkdir to succeed but sqlite3.connect to fail
        with patch("pathlib.Path.mkdir"):
            with patch("sqlite3.connect", side_effect=sqlite3.Error("Connection failed")):
                with pytest.raises(RuntimeError, match="Failed to connect"):
                    manager.get_connection()

    def test_initialize_schema_raises_on_bad_sql(self) -> None:
        """Test that initialize_schema handles SQL errors."""
        manager = DatabaseManager(db_path=Path(":memory:"))
        manager.get_connection()

        # Patch schema to include bad SQL
        with patch("zlibrary_downloader.schema.ALL_TABLES", ["INVALID SQL"]):
            with pytest.raises(RuntimeError, match="Failed to initialize"):
                manager.initialize_schema()


class TestContextManager:
    """Tests for context manager support."""

    def test_context_manager_closes_connection(self) -> None:
        """Test that context manager closes connection on exit."""
        manager = DatabaseManager(db_path=Path(":memory:"))

        with manager:
            manager.get_connection()
            assert manager.connection is not None

        assert manager.connection is None

    def test_context_manager_closes_on_exception(self) -> None:
        """Test that connection is closed even on exception."""
        manager = DatabaseManager(db_path=Path(":memory:"))

        with pytest.raises(ValueError):
            with manager:
                manager.get_connection()
                assert manager.connection is not None
                raise ValueError("Test error")

        assert manager.connection is None
