"""Tests for database schema definitions."""
import sqlite3
import pytest
from zlibrary_downloader import schema


def test_schema_version_constant():
    """Test that schema version is defined."""
    assert isinstance(schema.SCHEMA_VERSION, int)
    assert schema.SCHEMA_VERSION >= 1


def test_all_tables_list():
    """Test that ALL_TABLES contains all expected tables."""
    assert len(schema.ALL_TABLES) == 9
    assert schema.SCHEMA_VERSION_TABLE in schema.ALL_TABLES
    assert schema.BOOKS_TABLE in schema.ALL_TABLES
    assert schema.AUTHORS_TABLE in schema.ALL_TABLES
    assert schema.BOOK_AUTHORS_TABLE in schema.ALL_TABLES
    assert schema.READING_LISTS_TABLE in schema.ALL_TABLES
    assert schema.LIST_BOOKS_TABLE in schema.ALL_TABLES
    assert schema.SAVED_BOOKS_TABLE in schema.ALL_TABLES
    assert schema.DOWNLOADS_TABLE in schema.ALL_TABLES
    assert schema.SEARCH_HISTORY_TABLE in schema.ALL_TABLES


def test_all_indexes_list():
    """Test that ALL_INDEXES contains expected indexes."""
    assert len(schema.ALL_INDEXES) == 5
    # Books indexes
    assert any("idx_books_title" in idx for idx in schema.ALL_INDEXES)
    assert any("idx_books_language" in idx for idx in schema.ALL_INDEXES)
    assert any("idx_books_year" in idx for idx in schema.ALL_INDEXES)
    # Downloads indexes
    assert any("idx_downloads_book_id" in idx for idx in schema.ALL_INDEXES)
    assert any("idx_downloads_downloaded_at" in idx for idx in schema.ALL_INDEXES)


def test_schema_creates_tables_successfully():
    """Test that all table definitions are valid SQLite syntax."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create all tables
    for table_sql in schema.ALL_TABLES:
        cursor.execute(table_sql)

    # Create all indexes
    for index_sql in schema.ALL_INDEXES:
        cursor.execute(index_sql)

    conn.commit()

    # Verify all tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row[0] for row in cursor.fetchall()}

    expected_tables = {
        'schema_version', 'books', 'authors', 'book_authors',
        'reading_lists', 'list_books', 'saved_books',
        'downloads', 'search_history'
    }
    assert expected_tables.issubset(tables)

    conn.close()


def test_books_table_columns():
    """Test that books table has all required columns."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()
    cursor.execute(schema.BOOKS_TABLE)

    cursor.execute("PRAGMA table_info(books);")
    columns = {row[1] for row in cursor.fetchall()}

    expected_columns = {
        'id', 'hash', 'title', 'year', 'publisher', 'language',
        'extension', 'size', 'filesize', 'cover_url', 'description',
        'created_at', 'updated_at'
    }
    assert expected_columns == columns

    conn.close()


def test_foreign_key_constraints():
    """Test that foreign key constraints are properly defined."""
    conn = sqlite3.connect(":memory:")
    conn.execute("PRAGMA foreign_keys = ON;")
    cursor = conn.cursor()

    # Create all tables
    for table_sql in schema.ALL_TABLES:
        cursor.execute(table_sql)

    # Test book_authors foreign key
    cursor.execute("INSERT INTO books (id, hash, title) VALUES ('1', 'abc', 'Test');")
    cursor.execute("INSERT INTO authors (name) VALUES ('Author');")
    cursor.execute("INSERT INTO book_authors (book_id, author_id) VALUES ('1', 1);")

    # Verify constraint on delete cascade
    cursor.execute("DELETE FROM books WHERE id = '1';")
    cursor.execute("SELECT * FROM book_authors WHERE book_id = '1';")
    assert len(cursor.fetchall()) == 0

    conn.close()


def test_unique_constraints():
    """Test that unique constraints work correctly."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create necessary tables
    cursor.execute(schema.AUTHORS_TABLE)
    cursor.execute(schema.READING_LISTS_TABLE)

    # Test authors unique constraint
    cursor.execute("INSERT INTO authors (name) VALUES ('John Doe');")
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("INSERT INTO authors (name) VALUES ('John Doe');")

    # Test reading_lists unique constraint
    cursor.execute("INSERT INTO reading_lists (name) VALUES ('My List');")
    with pytest.raises(sqlite3.IntegrityError):
        cursor.execute("INSERT INTO reading_lists (name) VALUES ('My List');")

    conn.close()


def test_indexes_create_successfully():
    """Test that all index definitions are valid SQLite syntax."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    # Create tables first
    cursor.execute(schema.BOOKS_TABLE)
    cursor.execute(schema.DOWNLOADS_TABLE)

    # Create indexes
    for index_sql in schema.ALL_INDEXES:
        cursor.execute(index_sql)

    # Verify indexes exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index';")
    indexes = {row[0] for row in cursor.fetchall()}

    expected_indexes = {
        'idx_books_title', 'idx_books_language', 'idx_books_year',
        'idx_downloads_book_id', 'idx_downloads_downloaded_at'
    }
    assert expected_indexes.issubset(indexes)

    conn.close()


def test_default_values():
    """Test that default values are properly set."""
    conn = sqlite3.connect(":memory:")
    cursor = conn.cursor()

    cursor.execute(schema.BOOKS_TABLE)
    cursor.execute(schema.SAVED_BOOKS_TABLE)

    # Insert book and saved_book with minimal data
    cursor.execute("INSERT INTO books (id, hash, title) VALUES ('1', 'abc', 'Test');")
    cursor.execute("INSERT INTO saved_books (book_id) VALUES ('1');")

    # Verify defaults
    cursor.execute("SELECT priority, saved_at FROM saved_books WHERE book_id = '1';")
    row = cursor.fetchone()
    assert row[0] == 0  # Default priority
    assert row[1] is not None  # Default timestamp

    conn.close()
