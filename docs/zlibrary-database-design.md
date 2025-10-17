# Z-Library Database Design & Enhancement Plan

## Executive Summary

This document outlines the available metadata from Z-Library API, proposes a database schema for storing and managing book records, and recommends features for enhancing the zlibrary-downloader tool.

## Table of Contents

1. [Available Metadata from Z-Library API](#available-metadata)
2. [Entity-Relationship Diagram](#er-diagram)
3. [Database Schema Proposal](#database-schema)
4. [Recommended Features](#recommended-features)
5. [Implementation Roadmap](#implementation-roadmap)

---

## Available Metadata from Z-Library API

### 1. Search Results (`search()` method)

The search endpoint returns a list of books with the following metadata:

```json
{
  "success": true,
  "books": [
    {
      "id": "12345",
      "hash": "abcd1234",
      "title": "Book Title",
      "author": "Author Name",
      "year": "2024",
      "publisher": "Publisher Name",
      "language": "english",
      "extension": "pdf",
      "size": "1.5 MB",
      "cover": "https://example.com/cover.jpg",
      "filesize": "1024000"
    }
  ]
}
```

### 2. Detailed Book Info (`getBookInfo()` method)

The book info endpoint provides additional detailed metadata for a specific book:

- **Note**: This requires testing with actual API to capture all fields
- Expected additional fields might include:
  - Description/synopsis
  - ISBN
  - Edition information
  - Categories/tags
  - Pages count
  - Additional file formats available

### 3. Similar Books (`getSimilar()` method)

Returns books similar to a given book - useful for recommendation features.

### 4. Book Formats (`getBookForamt()` method)

Returns all available file formats for a specific book.

### 5. User Profile (`getProfile()` method)

```json
{
  "success": true,
  "user": {
    "id": "123456",
    "email": "user@example.com",
    "name": "User Name",
    "kindle_email": "user@kindle.com",
    "remix_userkey": "key_xyz",
    "downloads_limit": 10,
    "downloads_today": 3
  }
}
```

### 6. User History Endpoints

- **Downloaded Books** (`getUserDownloaded()`): Books the user has downloaded
- **Saved Books** (`getUserSaved()`): Books the user has saved/bookmarked
- **Recommended Books** (`getUserRecommended()`): Personalized recommendations

### 7. Discovery Endpoints

- **Most Popular** (`getMostPopular()`): Trending books
- **Recently Added** (`getRecently()`): Latest additions to library

### 8. Metadata Endpoints

- **Languages** (`getLanguages()`): Available language filters
- **Extensions** (`getExtensions()`): Available file format filters

---

## Entity-Relationship Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                     Z-LIBRARY DATABASE SCHEMA                        │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐         ┌──────────────────────┐
│       Books          │         │      Authors         │
├──────────────────────┤         ├──────────────────────┤
│ PK id (TEXT)         │────┐    │ PK id (INTEGER)      │
│    hash (TEXT)       │    │    │    name (TEXT)       │
│    title (TEXT)      │    │    │    created_at        │
│    year (TEXT)       │    │    │    updated_at        │
│    publisher (TEXT)  │    │    └──────────────────────┘
│    language (TEXT)   │    │              │
│    extension (TEXT)  │    │              │
│    size (TEXT)       │    │    ┌─────────▼──────────┐
│    filesize (INT)    │    └───►│   BookAuthors      │
│    cover_url (TEXT)  │         │  (Junction Table)  │
│    description (TEXT)│         ├────────────────────┤
│    isbn (TEXT)       │         │ FK book_id         │
│    edition (TEXT)    │         │ FK author_id       │
│    pages (INTEGER)   │         │    author_order    │
│    created_at        │         │    created_at      │
│    updated_at        │         └────────────────────┘
│    source (TEXT)     │
└──────────────────────┘
         │
         │
         ├────────────────────────────┐
         │                            │
         ▼                            ▼
┌──────────────────────┐    ┌──────────────────────┐
│   SearchHistory      │    │     Downloads        │
├──────────────────────┤    ├──────────────────────┤
│ PK id (INTEGER)      │    │ PK id (INTEGER)      │
│ FK book_id (TEXT)    │    │ FK book_id (TEXT)    │
│    search_query      │    │ FK credential_id     │
│    search_filters    │    │    filename (TEXT)   │
│    found_at          │    │    file_path (TEXT)  │
│    rank_position     │    │    downloaded_at     │
│    created_at        │    │    file_size (INT)   │
└──────────────────────┘    │    status (TEXT)     │
                            │    error_msg (TEXT)  │
                            └──────────────────────┘
         │                            │
         │                            │
         ▼                            ▼
┌──────────────────────┐    ┌──────────────────────┐
│    Categories        │    │    Credentials       │
├──────────────────────┤    ├──────────────────────┤
│ PK id (INTEGER)      │    │ PK id (INTEGER)      │
│    name (TEXT)       │    │    identifier (TEXT) │
│    parent_id (INT)   │    │    email (TEXT)      │
│    created_at        │    │    status (TEXT)     │
└──────────────────────┘    │    downloads_left    │
         │                  │    last_used         │
         │                  │    created_at        │
┌────────▼──────────┐       │    updated_at        │
│  BookCategories   │       └──────────────────────┘
│ (Junction Table)  │
├───────────────────┤                 │
│ FK book_id        │                 │
│ FK category_id    │                 ▼
│    created_at     │       ┌──────────────────────┐
└───────────────────┘       │    SavedBooks        │
                            ├──────────────────────┤
         │                  │ PK id (INTEGER)      │
         │                  │ FK book_id (TEXT)    │
         ▼                  │    saved_at          │
┌──────────────────────┐    │    notes (TEXT)      │
│   SimilarBooks       │    │    tags (TEXT)       │
├──────────────────────┤    │    priority (INT)    │
│ PK id (INTEGER)      │    │    created_at        │
│ FK book_id (TEXT)    │    │    updated_at        │
│ FK similar_book_id   │    └──────────────────────┘
│    similarity_score  │
│    discovered_at     │              │
│    created_at        │              │
└──────────────────────┘              ▼
                            ┌──────────────────────┐
         │                  │   ReadingLists       │
         │                  ├──────────────────────┤
         ▼                  │ PK id (INTEGER)      │
┌──────────────────────┐    │    name (TEXT)       │
│   BookFormats        │    │    description       │
├──────────────────────┤    │    created_at        │
│ PK id (INTEGER)      │    │    updated_at        │
│ FK book_id (TEXT)    │    └──────────────────────┘
│    format (TEXT)     │              │
│    available (BOOL)  │              │
│    size (TEXT)       │    ┌─────────▼──────────┐
│    created_at        │    │  ListBooks         │
│    updated_at        │    │  (Junction Table)  │
└──────────────────────┘    ├────────────────────┤
                            │ FK list_id         │
                            │ FK book_id         │
                            │    position        │
                            │    added_at        │
                            └────────────────────┘
```

---

## Database Schema Proposal

### Core Tables

#### 1. **Books** (Main entity)

```sql
CREATE TABLE books (
    id TEXT PRIMARY KEY,              -- Z-Library book ID
    hash TEXT NOT NULL,               -- Z-Library book hash
    title TEXT NOT NULL,
    year TEXT,
    publisher TEXT,
    language TEXT,
    extension TEXT,                   -- Primary file format
    size TEXT,                        -- Human-readable size (e.g., "1.5 MB")
    filesize INTEGER,                 -- Size in bytes
    cover_url TEXT,
    description TEXT,                 -- From getBookInfo()
    isbn TEXT,
    edition TEXT,
    pages INTEGER,
    source TEXT DEFAULT 'zlibrary',   -- Source of the book data
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_language ON books(language);
CREATE INDEX idx_books_year ON books(year);
CREATE INDEX idx_books_created_at ON books(created_at);
```

#### 2. **Authors**

```sql
CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_authors_name ON authors(name);
```

#### 3. **BookAuthors** (Junction table for many-to-many relationship)

```sql
CREATE TABLE book_authors (
    book_id TEXT NOT NULL,
    author_id INTEGER NOT NULL,
    author_order INTEGER DEFAULT 0,   -- For books with multiple authors
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

CREATE INDEX idx_book_authors_book ON book_authors(book_id);
CREATE INDEX idx_book_authors_author ON book_authors(author_id);
```

### Feature Tables

#### 4. **Downloads** (Track downloaded books)

```sql
CREATE TABLE downloads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL,
    credential_id INTEGER,            -- Which credential was used
    filename TEXT NOT NULL,
    file_path TEXT NOT NULL,          -- Local file path
    downloaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    file_size INTEGER,
    status TEXT DEFAULT 'completed',  -- completed, failed, deleted
    error_msg TEXT,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (credential_id) REFERENCES credentials(id) ON DELETE SET NULL
);

CREATE INDEX idx_downloads_book ON downloads(book_id);
CREATE INDEX idx_downloads_date ON downloads(downloaded_at);
CREATE INDEX idx_downloads_status ON downloads(status);
```

#### 5. **SearchHistory** (Track search queries and results)

```sql
CREATE TABLE search_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT,                     -- NULL for searches, populated when book is found
    search_query TEXT NOT NULL,
    search_filters TEXT,              -- JSON string of filters applied
    found_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    rank_position INTEGER,            -- Position in search results
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE SET NULL
);

CREATE INDEX idx_search_history_query ON search_history(search_query);
CREATE INDEX idx_search_history_date ON search_history(found_at);
```

#### 6. **SavedBooks** (User's saved/bookmarked books)

```sql
CREATE TABLE saved_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL UNIQUE,
    saved_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,                       -- User notes about the book
    tags TEXT,                        -- Comma-separated tags
    priority INTEGER DEFAULT 0,       -- User-defined priority (0-5)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE INDEX idx_saved_books_date ON saved_books(saved_at);
CREATE INDEX idx_saved_books_priority ON saved_books(priority);
```

#### 7. **ReadingLists** (User-created collections)

```sql
CREATE TABLE reading_lists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

#### 8. **ListBooks** (Junction table for lists and books)

```sql
CREATE TABLE list_books (
    list_id INTEGER NOT NULL,
    book_id TEXT NOT NULL,
    position INTEGER DEFAULT 0,       -- Order in the list
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (list_id, book_id),
    FOREIGN KEY (list_id) REFERENCES reading_lists(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);

CREATE INDEX idx_list_books_list ON list_books(list_id);
CREATE INDEX idx_list_books_position ON list_books(list_id, position);
```

### Relationship Tables

#### 9. **Categories** (Book categories/genres)

```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    parent_id INTEGER,                -- For hierarchical categories
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE INDEX idx_categories_parent ON categories(parent_id);
```

#### 10. **BookCategories** (Junction table)

```sql
CREATE TABLE book_categories (
    book_id TEXT NOT NULL,
    category_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (book_id, category_id),
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

CREATE INDEX idx_book_categories_book ON book_categories(book_id);
CREATE INDEX idx_book_categories_category ON book_categories(category_id);
```

#### 11. **SimilarBooks** (Track similar books)

```sql
CREATE TABLE similar_books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL,
    similar_book_id TEXT NOT NULL,
    similarity_score REAL,            -- If provided by API
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    FOREIGN KEY (similar_book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE(book_id, similar_book_id)
);

CREATE INDEX idx_similar_books_book ON similar_books(book_id);
```

#### 12. **BookFormats** (Available formats for each book)

```sql
CREATE TABLE book_formats (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id TEXT NOT NULL,
    format TEXT NOT NULL,             -- pdf, epub, mobi, etc.
    available BOOLEAN DEFAULT 1,
    size TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
    UNIQUE(book_id, format)
);

CREATE INDEX idx_book_formats_book ON book_formats(book_id);
CREATE INDEX idx_book_formats_format ON book_formats(format);
```

### System Tables

#### 13. **Credentials** (Track credential usage)

```sql
CREATE TABLE credentials (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identifier TEXT NOT NULL UNIQUE,
    email TEXT,
    status TEXT DEFAULT 'valid',      -- valid, invalid, exhausted
    downloads_left INTEGER,
    last_used TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

---

## Recommended Features

Based on the database schema, here are recommended features to implement:

### Phase 1: Core Database Features

1. **Search & Store**
   - Search by title/keyword and automatically store results in database
   - Deduplicate books based on ID/hash
   - Update existing records with new information

2. **Browse Interface**
   - Browse all books in local database
   - Filter by language, year, format, author
   - Full-text search across title, author, description
   - Sort by various fields (date added, title, year)

3. **CRUD Operations**
   - View detailed book information
   - Update book metadata (notes, tags, priority)
   - Delete books from database
   - Merge duplicate entries

### Phase 2: Collection Management

4. **Saved Books / Wishlist**
   - Save books for later download
   - Add personal notes and tags
   - Set priority levels
   - Track when books were saved

5. **Reading Lists**
   - Create custom reading lists
   - Add/remove books from lists
   - Reorder books within lists
   - Share lists (export/import)

6. **Download Management**
   - Track all downloaded books
   - Link to local file paths
   - Track download dates and credentials used
   - Identify missing files
   - Re-download deleted files

### Phase 3: Discovery & Analytics

7. **Search History**
   - Track all search queries
   - See which books were found for each search
   - Identify trending searches
   - Quick re-run of previous searches

8. **Similar Books Discovery**
   - Fetch and store similar books
   - Build recommendation network
   - "Books like this" feature

9. **Analytics Dashboard**
   - Total books in database
   - Download statistics by date/format/language
   - Most searched authors/topics
   - Collection growth over time
   - Storage space used

### Phase 4: Advanced Features

10. **Bulk Operations**
    - Bulk import from search results
    - Batch download with rate limiting
    - Bulk tagging and categorization
    - Export database to various formats

11. **Sync & Backup**
    - Export database to JSON/CSV
    - Import from backups
    - Sync with Z-Library (fetch updates)
    - Backup to cloud storage

12. **Integration Features**
    - Export reading lists to Kindle/Calibre
    - Import from Goodreads
    - Generate book reports
    - API for external tools

---

## Implementation Roadmap

### Step 1: Test API Responses (CURRENT)

Run the test script to capture actual metadata:

```bash
python test_zlibrary_metadata.py
```

Review the output to:
- Confirm all available fields
- Identify any additional metadata not captured in this design
- Update database schema if needed

### Step 2: Choose Database Technology

**Recommended**: SQLite
- Lightweight, serverless
- Built into Python
- Perfect for local application
- Easy to backup and migrate

**Alternative**: PostgreSQL
- If multi-user access needed
- Better for large-scale deployments
- More complex setup

### Step 3: Create Database Layer

1. Create SQLAlchemy models or use raw SQL
2. Implement database initialization
3. Create migration system
4. Build CRUD operations

### Step 4: Integrate with Existing CLI

1. Add `--save-to-db` flag to search command
2. Add `browse` command for database exploration
3. Add `list` command for viewing saved books
4. Add `sync` command for updating from Z-Library

### Step 5: Build Features Incrementally

Follow the phases outlined in "Recommended Features" section.

---

## Next Steps

1. **Run the test script** to capture actual API responses
2. **Review the ER diagram** and confirm it meets your needs
3. **Decide which features** you want to implement first
4. **Choose database technology** (SQLite recommended)
5. **Start implementation** with Phase 1 features

---

## Questions for Discussion

1. Do you want to include user profile/credentials in the database?
2. Should we track multiple versions of the same book (different formats)?
3. Do you need multi-user support or single-user local database?
4. Should we track file integrity (checksums)?
5. Any specific queries or reports you want to generate?

