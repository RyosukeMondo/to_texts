"""Database schema definitions for zlibrary-downloader.

This module contains all SQL CREATE TABLE statements for initializing
the SQLite database. Schema version tracking is included for future migrations.
"""

# Schema version for tracking database migrations
SCHEMA_VERSION = 1

# Schema version tracking table
SCHEMA_VERSION_TABLE = """
CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Books table - core entity storing Z-Library book metadata
BOOKS_TABLE = """
CREATE TABLE IF NOT EXISTS books (
    id TEXT PRIMARY KEY,
    hash TEXT NOT NULL,
    title TEXT NOT NULL,
    year TEXT,
    publisher TEXT,
    language TEXT,
    extension TEXT,
    size TEXT,
    filesize INTEGER,
    cover_url TEXT,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

BOOKS_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_books_title ON books(title);",
    "CREATE INDEX IF NOT EXISTS idx_books_language ON books(language);",
    "CREATE INDEX IF NOT EXISTS idx_books_year ON books(year);",
]

# Authors table - stores unique author names
AUTHORS_TABLE = """
CREATE TABLE IF NOT EXISTS authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);
"""

# Book-Author junction table - many-to-many relationship
BOOK_AUTHORS_TABLE = """
CREATE TABLE IF NOT EXISTS book_authors (
    book_id TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    author_order INTEGER DEFAULT 0,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);
"""

# Reading lists - user-created book collections
READING_LISTS_TABLE = """
CREATE TABLE IF NOT EXISTS reading_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# List-Book junction table - books in reading lists with ordering
LIST_BOOKS_TABLE = """
CREATE TABLE IF NOT EXISTS list_books (
    list_id INTEGER NOT NULL,
    book_id TEXT NOT NULL,
    position INTEGER DEFAULT 0,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (list_id, book_id),
    FOREIGN KEY (list_id) REFERENCES reading_lists(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);
"""

# Saved books - user bookmarks with notes and metadata
SAVED_BOOKS_TABLE = """
CREATE TABLE IF NOT EXISTS saved_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL UNIQUE,
    notes TEXT,
    tags TEXT,
    priority INTEGER DEFAULT 0,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);
"""

# Download tracking - record of all downloaded books
DOWNLOADS_TABLE = """
CREATE TABLE IF NOT EXISTS downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL,
    credential_id INTEGER,
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    status TEXT DEFAULT 'completed',
    error_msg TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);
"""

DOWNLOADS_INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_downloads_book_id ON downloads(book_id);",
    "CREATE INDEX IF NOT EXISTS idx_downloads_downloaded_at ON downloads(downloaded_at);",
]

# Search history - track user searches for analytics
SEARCH_HISTORY_TABLE = """
CREATE TABLE IF NOT EXISTS search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    search_query TEXT NOT NULL,
    search_filters TEXT,
    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# All schema statements in order
ALL_TABLES = [
    SCHEMA_VERSION_TABLE,
    BOOKS_TABLE,
    AUTHORS_TABLE,
    BOOK_AUTHORS_TABLE,
    READING_LISTS_TABLE,
    LIST_BOOKS_TABLE,
    SAVED_BOOKS_TABLE,
    DOWNLOADS_TABLE,
    SEARCH_HISTORY_TABLE,
]

ALL_INDEXES = BOOKS_INDEXES + DOWNLOADS_INDEXES
