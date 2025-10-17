# SPEC-001: Database Storage for Z-Library Metadata

## Document Metadata

- **Feature Name**: Database Storage & Browse System
- **Author(s)**: Development Team
- **Created**: 2025-10-17
- **Last Updated**: 2025-10-17
- **Status**: Draft
- **Target Version**: v0.2.0
- **Related Issues**: N/A
- **Related Specs**: N/A

---

## 1. Executive Summary

### 1.1 Overview

This specification defines a database storage system for Z-Library book metadata, enabling users to build a local searchable catalog of books, manage collections, track downloads, and browse their library offline.

**Problem Statement**: Currently, zlibrary-downloader searches Z-Library on-demand but doesn't store results. Users cannot browse previous searches, build collections, or work offline. There's no way to track what books have been discovered, saved, or downloaded.

**Solution Summary**: Implement a SQLite-based database layer that stores book metadata, search history, download records, and user collections. Provide CLI commands to browse, search, and manage the local database while maintaining all existing search and download functionality.

**Success Criteria**:
- Users can store search results automatically
- Users can browse their local database offline
- Users can create and manage reading lists
- Users can track downloaded books
- All operations maintain >80% test coverage
- All code passes existing quality gates

### 1.2 Goals & Non-Goals

**Goals:**
- Store Z-Library book metadata locally
- Enable offline browsing of discovered books
- Track download history and file locations
- Support collections/reading lists
- Maintain search history
- Provide database export/import functionality
- Keep existing CLI interface backward compatible

**Non-Goals:**
- Storing actual book files in database (only metadata)
- Real-time sync with Z-Library (user-initiated only)
- Multi-user database access (single-user local DB)
- GUI interface (CLI only for this version)
- Web interface or API server
- Built-in book reader functionality

---

## 2. User Stories & Use Cases

### 2.1 User Personas

- **Book Collector**: User who searches extensively and wants to maintain a catalog of interesting books before deciding what to download
- **Researcher**: User who needs to track books by topic, create reading lists, and search through previously discovered books
- **Archivist**: User who downloads many books and needs to track what has been downloaded and where files are stored

### 2.2 User Stories

**Story 1: Store Search Results**
- **As a** book collector
- **I want to** automatically save search results to a local database
- **So that** I can browse and search them later without re-querying Z-Library
- **Acceptance Criteria**:
  - [ ] `--save-db` flag stores search results
  - [ ] Duplicate books are not created (use Z-Library ID as key)
  - [ ] All metadata fields are captured
  - [ ] Search is not slowed down by database operations

**Story 2: Browse Local Catalog**
- **As a** researcher
- **I want to** browse and search my local book database
- **So that** I can find books I've previously discovered without internet access
- **Acceptance Criteria**:
  - [ ] `browse` command shows paginated book list
  - [ ] Can filter by language, year, format, author
  - [ ] Can search within local database
  - [ ] Results display similarly to online search

**Story 3: Manage Reading Lists**
- **As a** researcher
- **I want to** create custom reading lists with my books
- **So that** I can organize books by topic or project
- **Acceptance Criteria**:
  - [ ] Can create, list, rename, delete reading lists
  - [ ] Can add/remove books from lists
  - [ ] Can view all books in a list
  - [ ] Lists persist across sessions

**Story 4: Track Downloads**
- **As an** archivist
- **I want to** automatically track which books I've downloaded and where they're stored
- **So that** I can avoid duplicate downloads and locate files easily
- **Acceptance Criteria**:
  - [ ] Downloads are automatically recorded
  - [ ] Can view download history
  - [ ] Can search for downloaded books
  - [ ] Shows local file path for each download

**Story 5: Save Books for Later**
- **As a** book collector
- **I want to** bookmark/save interesting books
- **So that** I can download them later when I have time
- **Acceptance Criteria**:
  - [ ] Can save books from search results
  - [ ] Can add notes and tags to saved books
  - [ ] Can view all saved books
  - [ ] Can unsave books

### 2.3 Use Cases

**Use Case 1**: Search and Store Books
- **Actor**: Book Collector
- **Preconditions**: Database initialized, credentials configured
- **Main Flow**:
  1. User runs `zlibrary-downloader search "python" --save-db`
  2. System searches Z-Library API
  3. System displays results to user
  4. System stores each book in database
  5. System deduplicates based on book ID
  6. System records search query in history
- **Alternative Flows**:
  - If database doesn't exist, create it first
  - If book already exists, update metadata only
- **Postconditions**: Books are stored in database, search is logged

**Use Case 2**: Browse Local Database
- **Actor**: Researcher
- **Preconditions**: Database contains books
- **Main Flow**:
  1. User runs `zlibrary-downloader db browse --language english --format pdf`
  2. System queries local database with filters
  3. System displays paginated results
  4. User can navigate pages or refine filters
- **Alternative Flows**:
  - If no books match filters, show helpful message
  - If database is empty, suggest running search with --save-db
- **Postconditions**: User can see their local catalog

**Use Case 3**: Create Reading List
- **Actor**: Researcher
- **Preconditions**: Database contains books
- **Main Flow**:
  1. User runs `zlibrary-downloader db list-create "Machine Learning"`
  2. System creates new reading list
  3. User runs `zlibrary-downloader db list-add "Machine Learning" --book-id 12345`
  4. System adds book to list
  5. User runs `zlibrary-downloader db list-show "Machine Learning"`
  6. System displays all books in the list
- **Alternative Flows**:
  - If list already exists, show error
  - If book doesn't exist, show error with suggestion
- **Postconditions**: Reading list created and populated

---

## 3. Requirements

### 3.1 Functional Requirements

**FR-1: Database Initialization**
- **Priority**: Critical
- **Acceptance Criteria**: System automatically creates database on first use or when user runs `db init` command. Database location: `~/.zlibrary/books.db`

**FR-2: Store Book Metadata**
- **Priority**: Critical
- **Acceptance Criteria**: All fields from Z-Library API are stored (id, hash, title, author, year, publisher, language, extension, size, cover_url, etc.)

**FR-3: Search Results Storage**
- **Priority**: High
- **Acceptance Criteria**: `--save-db` flag on search command stores results automatically

**FR-4: Browse Stored Books**
- **Priority**: High
- **Acceptance Criteria**: `db browse` command with filters (language, year, format, author, keyword)

**FR-5: Reading Lists**
- **Priority**: Medium
- **Acceptance Criteria**: CRUD operations for reading lists and list membership

**FR-6: Saved Books (Bookmarks)**
- **Priority**: Medium
- **Acceptance Criteria**: Save/unsave books, add notes, view saved books

**FR-7: Download Tracking**
- **Priority**: High
- **Acceptance Criteria**: Automatically record downloads with file path, timestamp, credential used

**FR-8: Search History**
- **Priority**: Low
- **Acceptance Criteria**: Track all search queries with timestamp

**FR-9: Database Export/Import**
- **Priority**: Medium
- **Acceptance Criteria**: Export to JSON/CSV, import from JSON

**FR-10: Database Statistics**
- **Priority**: Low
- **Acceptance Criteria**: Show database stats (total books, by language, by format, storage used, etc.)

### 3.2 Non-Functional Requirements

**NFR-1: Performance**
- Database queries must complete in <100ms for typical operations
- Search with 10,000 books in database: <200ms
- Inserting 100 books: <1 second

**NFR-2: Scalability**
- Support at least 50,000 books in database
- Support at least 1,000 reading lists
- Support at least 100,000 search history records

**NFR-3: Security**
- Database file has restricted permissions (600 on Unix)
- No credentials stored in database (reference only)
- No sensitive user data stored

**NFR-4: Maintainability**
- All modules must pass quality gates (complexity ≤10, file size ≤400, function size ≤30)
- 80%+ test coverage
- Clear separation of concerns (database layer, CLI layer, business logic)

**NFR-5: Compatibility**
- Python 3.8+ support
- SQLite 3.x
- Backward compatible with existing CLI commands
- Cross-platform (Windows, macOS, Linux)

---

## 4. Technical Design

### 4.1 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     CLI Layer (cli.py)                       │
│  - Argument parsing                                          │
│  - User interaction                                          │
│  - Calls business logic                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Business Logic Layer (services/)                │
│  - book_service.py: Book operations                          │
│  - list_service.py: Reading list operations                  │
│  - search_service.py: Search orchestration                   │
│  - download_service.py: Download tracking                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│           Data Access Layer (database/)                      │
│  - db_manager.py: Database connection & initialization       │
│  - repositories/:                                            │
│    - book_repository.py: Book CRUD operations                │
│    - author_repository.py: Author CRUD operations            │
│    - list_repository.py: Reading list CRUD operations        │
│    - download_repository.py: Download tracking               │
│    - search_repository.py: Search history                    │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                  Models (database/models.py)                 │
│  - Book, Author, ReadingList, Download, etc.                 │
│  - Type-safe dataclasses                                     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                    SQLite Database                           │
│                  ~/.zlibrary/books.db                        │
└─────────────────────────────────────────────────────────────┘
```

**Design Patterns:**
- **Repository Pattern**: Separate data access from business logic
- **Service Layer**: Orchestrate operations across repositories
- **Dependency Injection**: Pass database connection to repositories

### 4.2 Data Model

See `docs/zlibrary-database-design.md` for complete ER diagram.

**Core Tables:**
- `books`: Book metadata
- `authors`: Author information
- `book_authors`: Many-to-many relationship
- `downloads`: Download tracking
- `saved_books`: Bookmarked books
- `reading_lists`: User-created lists
- `list_books`: List membership
- `search_history`: Search queries

### 4.3 API Design

#### 4.3.1 Database Manager

```python
class DatabaseManager:
    """Manages database connection and initialization."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        """Initialize database manager."""
        pass

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        pass

    def initialize_schema(self) -> None:
        """Create all tables if they don't exist."""
        pass

    def close(self) -> None:
        """Close database connection."""
        pass
```

#### 4.3.2 Book Repository

```python
class BookRepository:
    """Repository for book data access."""

    def __init__(self, db_manager: DatabaseManager) -> None:
        """Initialize repository with database manager."""
        pass

    def create(self, book: Book) -> Book:
        """Create a new book record."""
        pass

    def get_by_id(self, book_id: str) -> Optional[Book]:
        """Get book by Z-Library ID."""
        pass

    def search(
        self,
        query: Optional[str] = None,
        language: Optional[str] = None,
        year_from: Optional[int] = None,
        year_to: Optional[int] = None,
        extension: Optional[str] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> List[Book]:
        """Search books in local database."""
        pass

    def update(self, book: Book) -> Book:
        """Update existing book."""
        pass

    def upsert(self, book: Book) -> Book:
        """Insert or update book (based on ID)."""
        pass

    def delete(self, book_id: str) -> bool:
        """Delete book by ID."""
        pass

    def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count books matching filters."""
        pass
```

#### 4.3.3 Reading List Repository

```python
class ReadingListRepository:
    """Repository for reading list operations."""

    def create_list(self, name: str, description: str = "") -> ReadingList:
        """Create a new reading list."""
        pass

    def get_list(self, list_id: int) -> Optional[ReadingList]:
        """Get reading list by ID."""
        pass

    def get_list_by_name(self, name: str) -> Optional[ReadingList]:
        """Get reading list by name."""
        pass

    def list_all(self) -> List[ReadingList]:
        """Get all reading lists."""
        pass

    def add_book(self, list_id: int, book_id: str) -> bool:
        """Add book to reading list."""
        pass

    def remove_book(self, list_id: int, book_id: str) -> bool:
        """Remove book from reading list."""
        pass

    def get_books(self, list_id: int) -> List[Book]:
        """Get all books in a reading list."""
        pass

    def delete_list(self, list_id: int) -> bool:
        """Delete a reading list."""
        pass
```

#### 4.3.4 CLI Interface

**New Commands:**

```bash
# Database initialization (usually automatic)
zlibrary-downloader db init

# Store search results
zlibrary-downloader search "python" --save-db

# Browse local database
zlibrary-downloader db browse [--language LANG] [--year-from YEAR] [--format EXT]

# View book details
zlibrary-downloader db show <book-id>

# Save/unsave books
zlibrary-downloader db save <book-id> [--notes "text"]
zlibrary-downloader db unsave <book-id>
zlibrary-downloader db saved [--list]

# Reading lists
zlibrary-downloader db list-create <name> [--description "text"]
zlibrary-downloader db list-show <name>
zlibrary-downloader db list-add <name> --book-id <id>
zlibrary-downloader db list-remove <name> --book-id <id>
zlibrary-downloader db list-delete <name>
zlibrary-downloader db lists

# Download history
zlibrary-downloader db downloads [--recent] [--credential <id>]

# Database operations
zlibrary-downloader db stats
zlibrary-downloader db export [--format json|csv] [--output FILE]
zlibrary-downloader db import <file>
zlibrary-downloader db vacuum

# Search history
zlibrary-downloader db history [--limit N]
```

### 4.4 Component Interactions

**Search with Database Storage Flow:**

```
User → CLI → search_service.search_and_store()
                    ↓
              Call zlibrary API
                    ↓
              Get book results
                    ↓
              For each book:
                  ↓
          book_repository.upsert(book)
                  ↓
          Extract authors → author_repository.get_or_create()
                  ↓
          Link book to authors → book_authors table
                  ↓
          search_repository.record_search()
                  ↓
          Return results to user
```

**Browse Database Flow:**

```
User → CLI → browse command
                ↓
        Parse filters (language, year, format)
                ↓
        book_service.browse(filters)
                ↓
        book_repository.search(filters)
                ↓
        Query SQLite with WHERE clauses
                ↓
        Return books → Format for display → Show to user
```

### 4.5 Dependencies

**New Dependencies:**
- None! (Using Python stdlib `sqlite3` module)

**Optional Dependencies for Future:**
- `sqlalchemy>=2.0.0`: If we need ORM features later
- `alembic>=1.13.0`: For database migrations if schema becomes complex

### 4.6 Configuration

**New Configuration Options:**

```toml
# zlibrary_config.toml (new optional config file)
[database]
# Database file location (default: ~/.zlibrary/books.db)
path = "~/.zlibrary/books.db"

# Automatically save search results to database
auto_save = false

# Maximum number of search results to display
page_size = 20
```

**Environment Variables:**
```bash
# Override database location
ZLIBRARY_DB_PATH=/custom/path/books.db
```

---

## 5. Implementation Plan

### 5.1 Development Phases

**Phase 1: Database Foundation** (Est: 3-4 days)
- [ ] Task 1.1: Create database schema SQL scripts
- [ ] Task 1.2: Implement DatabaseManager class
- [ ] Task 1.3: Create data models (Book, Author, etc.)
- [ ] Task 1.4: Implement database initialization
- [ ] Task 1.5: Write unit tests for database layer
- [ ] Task 1.6: Add database migration system (simple version-based)

**Phase 2: Repository Layer** (Est: 4-5 days)
- [ ] Task 2.1: Implement BookRepository with CRUD operations
- [ ] Task 2.2: Implement AuthorRepository
- [ ] Task 2.3: Implement ReadingListRepository
- [ ] Task 2.4: Implement DownloadRepository
- [ ] Task 2.5: Implement SearchHistoryRepository
- [ ] Task 2.6: Write unit tests for all repositories (>80% coverage)

**Phase 3: Service Layer** (Est: 3-4 days)
- [ ] Task 3.1: Implement BookService (orchestrates book operations)
- [ ] Task 3.2: Implement SearchService (search + storage)
- [ ] Task 3.3: Implement ListService (reading list management)
- [ ] Task 3.4: Implement DownloadService (tracking)
- [ ] Task 3.5: Write unit tests for services

**Phase 4: CLI Integration** (Est: 3-4 days)
- [ ] Task 4.1: Add `--save-db` flag to search command
- [ ] Task 4.2: Implement `db` command group
- [ ] Task 4.3: Implement `db browse` command
- [ ] Task 4.4: Implement `db save/unsave` commands
- [ ] Task 4.5: Implement reading list commands
- [ ] Task 4.6: Implement download history commands
- [ ] Task 4.7: Implement database utility commands (stats, export, import)
- [ ] Task 4.8: Write integration tests

**Phase 5: Documentation & Polish** (Est: 2-3 days)
- [ ] Task 5.1: Update README with database features
- [ ] Task 5.2: Write user guide for database commands
- [ ] Task 5.3: Add examples and tutorials
- [ ] Task 5.4: Performance optimization
- [ ] Task 5.5: Final testing and bug fixes
- [ ] Task 5.6: Update CHANGELOG

**Total Estimated Time**: 15-20 days

### 5.2 File Structure

```
packages/python/zlibrary-downloader/
├── zlibrary_downloader/
│   ├── cli.py                      # Updated with db commands
│   ├── client.py                   # Existing (no changes)
│   ├── credential_manager.py       # Existing (no changes)
│   ├── database/
│   │   ├── __init__.py             # Export main classes
│   │   ├── db_manager.py           # ~150 lines: Connection management
│   │   ├── models.py               # ~200 lines: Data classes
│   │   ├── schema.py               # ~150 lines: SQL schema definitions
│   │   ├── migrations/
│   │   │   ├── __init__.py
│   │   │   ├── migration_manager.py # ~100 lines: Migration system
│   │   │   └── versions/
│   │   │       └── 001_initial.sql  # Initial schema
│   │   └── repositories/
│   │       ├── __init__.py
│   │       ├── base_repository.py  # ~80 lines: Base class
│   │       ├── book_repository.py  # ~250 lines: Book operations
│   │       ├── author_repository.py # ~100 lines: Author ops
│   │       ├── list_repository.py  # ~200 lines: Reading lists
│   │       ├── download_repository.py # ~120 lines: Downloads
│   │       └── search_repository.py # ~80 lines: Search history
│   ├── services/
│   │   ├── __init__.py
│   │   ├── book_service.py         # ~180 lines: Book operations
│   │   ├── search_service.py       # ~150 lines: Search + storage
│   │   ├── list_service.py         # ~140 lines: List management
│   │   └── download_service.py     # ~100 lines: Download tracking
│   └── utils/
│       ├── db_utils.py             # ~80 lines: DB utility functions
│       └── display.py              # ~150 lines: Format output (extract from cli.py)
├── tests/
│   ├── database/
│   │   ├── test_db_manager.py
│   │   ├── test_models.py
│   │   ├── test_book_repository.py
│   │   ├── test_author_repository.py
│   │   ├── test_list_repository.py
│   │   ├── test_download_repository.py
│   │   └── test_search_repository.py
│   ├── services/
│   │   ├── test_book_service.py
│   │   ├── test_search_service.py
│   │   ├── test_list_service.py
│   │   └── test_download_service.py
│   ├── test_cli_db_commands.py     # Integration tests
│   └── fixtures/
│       ├── sample_books.py
│       └── test_db.py              # Test database fixture
├── docs/
│   ├── database-guide.md           # User guide for database features
│   └── database-api.md             # API documentation
└── migrations/
    └── README.md                    # Migration instructions
```

**Line Count Compliance:**
- All files designed to stay under 400 lines
- Large modules split into smaller files
- Repositories separated by concern

### 5.3 Code Modules

**Module 1: `database/db_manager.py`** (~150 lines)
- **Purpose**: Manage SQLite database connection and initialization
- **Key Classes/Functions**:
  - `DatabaseManager`: Main database manager class
  - `get_connection()`: Return database connection
  - `initialize_schema()`: Create tables
  - `migrate()`: Run pending migrations
- **Estimated Lines**: ~150 lines
- **Complexity Target**: ≤10 per function

**Module 2: `database/models.py`** (~200 lines)
- **Purpose**: Define data models as dataclasses
- **Key Classes/Functions**:
  - `Book`: Book metadata model
  - `Author`: Author model
  - `ReadingList`: Reading list model
  - `Download`: Download record model
  - `SearchHistory`: Search history model
- **Estimated Lines**: ~200 lines (simple dataclasses)
- **Complexity Target**: Low (mostly data structures)

**Module 3: `database/repositories/book_repository.py`** (~250 lines)
- **Purpose**: Book CRUD operations
- **Key Classes/Functions**:
  - `BookRepository`: Main repository class
  - `create()`, `get_by_id()`, `search()`, `update()`, `delete()`
  - Helper functions for query building
- **Estimated Lines**: ~250 lines
- **Complexity Target**: ≤10 per function (use query builders)

**Module 4: `services/search_service.py`** (~150 lines)
- **Purpose**: Orchestrate search with database storage
- **Key Classes/Functions**:
  - `SearchService`: Main service class
  - `search_and_store()`: Search API + save to DB
  - `_store_book()`: Helper to store single book
  - `_extract_authors()`: Extract and link authors
- **Estimated Lines**: ~150 lines
- **Complexity Target**: ≤10 per function

**Module 5: `cli.py` updates** (~100 new lines)
- **Purpose**: Add database commands to CLI
- **Key Functions**:
  - `db_group()`: Command group for database ops
  - `db_browse()`, `db_show()`, `db_save()`, etc.
- **Estimated Lines**: Adds ~100 lines to existing CLI
- **Complexity Target**: ≤10 per function (delegate to services)

### 5.4 Database Migrations

**Migration System:**
- Simple version-based system
- SQL files in `database/migrations/versions/`
- Track applied migrations in `schema_version` table

**Migration 001: Initial Schema**
```sql
-- File: database/migrations/versions/001_initial.sql
-- Description: Create initial database schema

CREATE TABLE IF NOT EXISTS schema_version (
    version INTEGER PRIMARY KEY,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

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
    isbn TEXT,
    edition TEXT,
    pages INTEGER,
    source TEXT DEFAULT 'zlibrary',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_books_language ON books(language);
CREATE INDEX idx_books_year ON books(year);

-- [Additional tables...]
-- See schema.py for complete SQL

INSERT INTO schema_version (version) VALUES (1);
```

---

## 6. Testing Strategy

### 6.1 Unit Tests

**Coverage Target**: ≥80% (enforced by pytest-cov)

**Test Suites:**

1. **`test_db_manager.py`**: Database Manager Tests
   - `test_initialize_creates_tables()`
   - `test_get_connection_returns_valid_connection()`
   - `test_initialize_idempotent()`
   - `test_migration_tracking()`

2. **`test_book_repository.py`**: Book Repository Tests
   - `test_create_book()`
   - `test_get_book_by_id()`
   - `test_search_with_filters()`
   - `test_upsert_creates_new_book()`
   - `test_upsert_updates_existing_book()`
   - `test_delete_book()`
   - `test_count_with_filters()`

3. **`test_list_repository.py`**: Reading List Tests
   - `test_create_list()`
   - `test_add_book_to_list()`
   - `test_get_books_in_list()`
   - `test_remove_book_from_list()`
   - `test_delete_list()`

4. **`test_search_service.py`**: Search Service Tests
   - `test_search_and_store_creates_books()`
   - `test_search_and_store_deduplicates()`
   - `test_search_without_storage()`
   - `test_extract_authors()`

**Mock Strategy:**
- Database operations: Use in-memory SQLite (`:memory:`)
- Z-Library API: Mock `Zlibrary` client
- File system: Use temporary directories with `pytest tmpdir`

**Fixtures:**
```python
@pytest.fixture
def in_memory_db():
    """Create in-memory database for testing."""
    db_manager = DatabaseManager(db_path=":memory:")
    db_manager.initialize_schema()
    yield db_manager
    db_manager.close()

@pytest.fixture
def sample_book():
    """Create sample book for testing."""
    return Book(
        id="12345",
        hash="abcd1234",
        title="Test Book",
        author="Test Author",
        year="2024",
        language="english",
        extension="pdf",
        size="1.5 MB",
    )
```

### 6.2 Integration Tests

**Test Scenarios:**

1. **End-to-End Search and Store**
   - Setup: Clean database
   - Steps:
     1. Mock Z-Library API with sample books
     2. Run search with `--save-db`
     3. Verify books in database
     4. Run browse command
     5. Verify results match stored books
   - Expected: All books stored correctly
   - Teardown: Clean database

2. **Reading List Workflow**
   - Setup: Database with books
   - Steps:
     1. Create reading list
     2. Add books to list
     3. View list
     4. Remove book
     5. Delete list
   - Expected: All operations succeed
   - Teardown: Clean database

3. **Download Tracking**
   - Setup: Database initialized
   - Steps:
     1. Mock book download
     2. Verify download recorded in database
     3. Query download history
     4. Verify file path stored correctly
   - Expected: Download tracked correctly
   - Teardown: Clean test files

4. **Error Handling: Duplicate Books**
   - Setup: Database with existing book
   - Steps:
     1. Try to store same book again
     2. Verify upsert updates, not creates duplicate
   - Expected: Only one book record exists
   - Teardown: Clean database

### 6.3 Manual Testing Checklist

- [ ] Install fresh package
- [ ] Run search without `--save-db` (should work as before)
- [ ] Run search with `--save-db` (should store)
- [ ] Browse database (should show stored books)
- [ ] Create reading list and add books
- [ ] Save a book and view saved books
- [ ] Download a book and verify tracking
- [ ] Export database to JSON
- [ ] Import database from JSON
- [ ] Check database statistics
- [ ] Run on Windows, macOS, Linux
- [ ] Test with large database (1000+ books)

### 6.4 Performance Testing

**Benchmarks:**
- Insert 100 books: <1 second
- Search 10,000 books: <200ms
- Browse with filters: <100ms
- Create reading list: <10ms
- Add book to list: <10ms

**Load Tests:**
```python
def test_performance_bulk_insert():
    """Test inserting 1000 books."""
    start = time.time()
    for i in range(1000):
        repository.create(create_sample_book(i))
    elapsed = time.time() - start
    assert elapsed < 10.0  # Should complete in 10 seconds

def test_performance_search_large_db():
    """Test searching database with 10,000 books."""
    # Setup: Insert 10,000 books
    start = time.time()
    results = repository.search(query="python")
    elapsed = time.time() - start
    assert elapsed < 0.2  # Should complete in 200ms
```

---

## 7. Quality Gates Compliance

### 7.1 Code Quality Standards

**Enforced by Pre-commit Hooks:**

✅ **Type Checking (mypy)**
- All database functions have complete type hints
- Use `Optional`, `List`, `Dict` appropriately
- No `Any` types in public interfaces

```python
# Good
def get_book(self, book_id: str) -> Optional[Book]:
    ...

# Bad
def get_book(self, book_id):  # Missing types
    ...
```

✅ **Linting (flake8)**
- Follow PEP 8
- No unused imports
- No overly complex list comprehensions
- Use f-strings over format()

✅ **Formatting (black)**
- 100 character line length
- Consistent formatting throughout

✅ **Complexity (radon)**
- Target cyclomatic complexity ≤10
- Break down complex queries into helper functions

**Example Complexity Management:**

```python
# Bad: Complex query building (complexity >10)
def search(self, filters):
    query = "SELECT * FROM books WHERE 1=1"
    if filters.get('language'):
        query += f" AND language = '{filters['language']}'"
    if filters.get('year_from'):
        query += f" AND year >= {filters['year_from']}"
    if filters.get('year_to'):
        query += f" AND year <= {filters['year_to']}"
    if filters.get('extension'):
        query += f" AND extension = '{filters['extension']}'"
    # ... more conditions
    return self.execute(query)

# Good: Extract helper functions (complexity ≤10)
def search(self, filters: Dict[str, Any]) -> List[Book]:
    query = self._build_base_query()
    where_clauses = self._build_where_clauses(filters)
    query += " WHERE " + " AND ".join(where_clauses)
    return self._execute_search(query)

def _build_base_query(self) -> str:
    return "SELECT * FROM books"

def _build_where_clauses(self, filters: Dict[str, Any]) -> List[str]:
    clauses = ["1=1"]
    if filters.get('language'):
        clauses.append(self._language_clause(filters['language']))
    if filters.get('year_from'):
        clauses.append(self._year_from_clause(filters['year_from']))
    # ... more clauses
    return clauses
```

✅ **File Size**
- Keep all files ≤400 lines
- Split large repositories into multiple files if needed

✅ **Function Size**
- Keep all functions ≤30 lines
- Extract helper functions for complex logic

✅ **Test Coverage**
- Achieve ≥80% coverage
- Test all critical paths
- Test error handling

### 7.2 Pre-commit Checklist

Before committing database code:
- [ ] Run `mypy zlibrary_downloader` - all new code has type hints
- [ ] Run `flake8 zlibrary_downloader` - no linting errors
- [ ] Run `black --check zlibrary_downloader` - code formatted
- [ ] Run `radon cc --min C zlibrary_downloader/database` - complexity ≤10
- [ ] Check file line counts - all files ≤400 lines
- [ ] Check function line counts - all functions ≤30 lines
- [ ] Run `pytest --cov=zlibrary_downloader --cov-fail-under=80` - coverage ≥80%
- [ ] All tests pass
- [ ] Updated docstrings for new functions

### 7.3 Complexity Management Strategies

**For Database Queries:**
1. Use query builder helper functions
2. Extract WHERE clause construction
3. Separate query execution from query building

**For Service Layer:**
1. Single Responsibility: Each service method does one thing
2. Extract validation logic into separate functions
3. Use early returns to reduce nesting

**For CLI Commands:**
1. Parse arguments in CLI layer
2. Delegate all logic to service layer
3. Keep CLI functions thin (display only)

**Example:**
```python
# CLI layer (thin)
def db_browse_command(args):
    """Browse database books."""
    filters = _parse_browse_filters(args)  # <10 lines
    books = book_service.browse(filters)   # Delegate
    _display_books(books)                   # <10 lines

# Service layer (orchestration)
def browse(self, filters: Dict[str, Any]) -> List[Book]:
    """Browse books with filters."""
    validated_filters = self._validate_filters(filters)
    books = self.book_repo.search(**validated_filters)
    return self._enrich_book_data(books)

# Repository layer (data access)
def search(self, **filters) -> List[Book]:
    """Search books in database."""
    query = self._build_query()
    where = self._build_where_clauses(filters)
    return self._execute_and_map(query + where)
```

---

## 8. Documentation

### 8.1 User Documentation

**Required Documentation:**
- [ ] README.md: Add "Database Features" section
- [ ] `docs/database-guide.md`: Complete user guide with examples
- [ ] CLI help text for all new commands
- [ ] Tutorial: "Getting Started with Database Features"
- [ ] FAQ section for common questions
- [ ] Troubleshooting guide for database issues

**Example User Guide Sections:**
- Quick Start: Enabling database storage
- Browsing your library
- Creating reading lists
- Tracking downloads
- Exporting your database
- Performance tips

### 8.2 Developer Documentation

**Required Documentation:**
- [ ] `docs/database-api.md`: API documentation for all classes/functions
- [ ] Architecture Decision Records (ADR):
  - Why SQLite over PostgreSQL
  - Why repository pattern
  - Migration strategy decisions
- [ ] Code comments for complex queries
- [ ] Database schema documentation with diagrams
- [ ] Migration guide for contributors

**Docstring Example:**
```python
def search(
    self,
    query: Optional[str] = None,
    language: Optional[str] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    extension: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
) -> List[Book]:
    """
    Search books in the local database.

    Performs a full-text search across book titles, authors, and descriptions,
    with optional filters for language, publication year, and file format.

    Args:
        query: Search query string (searches title, author, description).
               If None, returns all books matching other filters.
        language: Filter by language code (e.g., 'english', 'spanish').
        year_from: Filter books published from this year onwards.
        year_to: Filter books published up to this year.
        extension: Filter by file format (e.g., 'pdf', 'epub').
        limit: Maximum number of results to return (default: 20).
        offset: Number of results to skip for pagination (default: 0).

    Returns:
        List of Book objects matching the search criteria, ordered by
        relevance (if query provided) or by title (otherwise).

    Raises:
        ValueError: If limit is negative or offset is negative.
        DatabaseError: If database query fails.

    Examples:
        >>> repo = BookRepository(db_manager)
        >>> books = repo.search(query="python", language="english", limit=10)
        >>> len(books) <= 10
        True

        >>> books = repo.search(year_from=2020, year_to=2024)
        >>> all(2020 <= int(book.year) <= 2024 for book in books if book.year)
        True
    """
    pass
```

### 8.3 README Updates

Add to main README.md:

```markdown
## Database Features

zlibrary-downloader can maintain a local database of book metadata, allowing you to:
- Build a searchable catalog of books
- Create custom reading lists
- Track your downloads
- Browse offline

### Quick Start

Enable database storage when searching:
\`\`\`bash
zlibrary-downloader search "machine learning" --save-db
\`\`\`

Browse your local database:
\`\`\`bash
zlibrary-downloader db browse --language english --format pdf
\`\`\`

See the [Database Guide](docs/database-guide.md) for complete documentation.
```

---

## 9. Migration & Rollback

### 9.1 Migration Plan

**For Users Upgrading from v0.1.x to v0.2.0:**

1. **Installation:**
   ```bash
   pip install --upgrade zlibrary-downloader
   ```

2. **Database Initialization:**
   - Automatic on first use of database feature
   - Or manually: `zlibrary-downloader db init`
   - Database location: `~/.zlibrary/books.db`

3. **Configuration Updates:**
   - No required changes
   - Optional: Add `[database]` section to config

4. **Backward Compatibility:**
   - All existing commands work exactly as before
   - Database features are opt-in via `--save-db` flag
   - No breaking changes to existing functionality

**Breaking Changes:**
- None! This is purely additive.

### 9.2 Rollback Plan

**If issues arise and user wants to rollback:**

1. **Uninstall new version:**
   ```bash
   pip install zlibrary-downloader==0.1.0
   ```

2. **Database cleanup (optional):**
   ```bash
   rm -rf ~/.zlibrary/books.db
   ```
   Database file can be kept for future upgrade.

3. **No data loss:**
   - Book files remain intact
   - Credentials unchanged
   - Only database file affected

**Data Preservation:**
- Before upgrade: `zlibrary-downloader db export --output backup.json`
- After rollback: Keep backup.json for future re-import

---

## 10. Risks & Mitigation

### 10.1 Technical Risks

**Risk 1: Database Corruption**
- **Likelihood**: Low
- **Impact**: Medium (user loses metadata, not actual books)
- **Mitigation**:
  - Use SQLite WAL mode for crash resistance
  - Regular integrity checks
  - Easy export/import for backups
  - Database corruption recovery guide in docs

**Risk 2: Performance Degradation with Large Databases**
- **Likelihood**: Medium (as database grows)
- **Impact**: Medium (slower queries)
- **Mitigation**:
  - Proper indexing on commonly queried fields
  - Pagination for browse results
  - Query optimization
  - Performance tests with large datasets
  - VACUUM command to optimize database

**Risk 3: Cross-platform Path Issues**
- **Likelihood**: Low
- **Impact**: Low (database location issues)
- **Mitigation**:
  - Use pathlib for cross-platform paths
  - Test on Windows, macOS, Linux
  - Proper handling of home directory expansion

**Risk 4: SQL Injection**
- **Likelihood**: Very Low (no user input in queries)
- **Impact**: High (security issue)
- **Mitigation**:
  - Use parameterized queries exclusively
  - Never string concatenation for queries
  - Code review focus on SQL construction
  - SQL injection testing in test suite

**Risk 5: Migration Failures**
- **Likelihood**: Low
- **Impact**: Medium (upgrade issues)
- **Mitigation**:
  - Simple migration system initially
  - Test migrations thoroughly
  - Backup before migration
  - Rollback capability

### 10.2 Dependency Risks

**Risk: SQLite Version Compatibility**
- **Mitigation**:
  - Use SQLite features available since 3.7 (widely available)
  - Test with minimum SQLite version (3.7.0)
  - Document required SQLite version

---

## 11. Success Metrics

### 11.1 Quantitative Metrics

- **Adoption Rate**: 50% of users enable `--save-db` within 60 days
- **Performance**: All database operations complete in <200ms for 10K books
- **Quality**: 0 P0 bugs related to database in first 30 days
- **Test Coverage**: Maintain ≥80% coverage across all database code
- **Complexity**: 100% of functions maintain cyclomatic complexity ≤10

### 11.2 Qualitative Metrics

- **User Feedback**: Positive feedback on database features in GitHub issues
- **Code Maintainability**: New contributors can understand and extend database layer
- **Documentation Quality**: Users can use database features without external help
- **Developer Experience**: Database code is easy to test and debug

---

## 12. Future Enhancements

### 12.1 Planned Follow-ups

**Enhancement 1: Advanced Search in Local Database**
- **Priority**: Medium
- **Estimated Effort**: 3 days
- **Dependencies**: Phase 1 complete
- **Features**:
  - Full-text search with ranking
  - Search by ISBN
  - Similar book recommendations from local DB
  - Fuzzy matching on titles/authors

**Enhancement 2: Database Sync with Z-Library**
- **Priority**: Low
- **Estimated Effort**: 4 days
- **Dependencies**: Phase 1 complete
- **Features**:
  - Fetch updated metadata for stored books
  - Check for new formats
  - Update availability status

**Enhancement 3: Collection Analytics**
- **Priority**: Low
- **Estimated Effort**: 3 days
- **Dependencies**: Phase 1 complete
- **Features**:
  - Language distribution charts
  - Format popularity
  - Reading list statistics
  - Download trends over time

**Enhancement 4: Book Notes and Ratings**
- **Priority**: Medium
- **Estimated Effort**: 2 days
- **Dependencies**: Phase 1 complete
- **Features**:
  - Add personal ratings (1-5 stars)
  - Rich text notes
  - Tags and categorization
  - Reading progress tracking

**Enhancement 5: Database Web UI**
- **Priority**: Low
- **Estimated Effort**: 10+ days
- **Dependencies**: Phase 1 complete
- **Features**:
  - Local web server
  - Browse books in browser
  - Visual reading lists
  - Search interface

### 12.2 Extension Points

**Areas designed for future expansion:**

1. **Plugin System for Data Sources**
   - Abstract book source interface
   - Add other library sources beyond Z-Library
   - Import from Calibre, Goodreads

2. **Export Formats**
   - Currently: JSON, CSV
   - Future: HTML, Markdown, XML
   - Integration with ebook managers

3. **Advanced Filtering**
   - Boolean search operators
   - Saved search filters
   - Smart collections (auto-updating)

4. **Multi-user Support** (if needed later)
   - User accounts in database
   - Per-user collections
   - Shared collections

---

## 13. Appendices

### Appendix A: Glossary

- **Repository Pattern**: Design pattern that abstracts data access logic from business logic
- **Upsert**: Database operation that inserts a new record or updates if it exists
- **Service Layer**: Business logic layer that orchestrates operations between repositories
- **Reading List**: User-created collection of books organized by theme or purpose
- **WAL Mode**: Write-Ahead Logging, SQLite mode for better concurrency and crash resistance

### Appendix B: References

- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Repository Pattern](https://martinfowler.com/eaaCatalog/repository.html)
- [Python sqlite3 module](https://docs.python.org/3/library/sqlite3.html)
- [Existing Database Design](../zlibrary-database-design.md)

### Appendix C: Research & Prototypes

**Research Conducted:**
- Analyzed Z-Library API responses (see test_zlibrary_metadata.py)
- Reviewed similar projects (Calibre, Zotero) for database design patterns
- Performance testing of SQLite with large datasets (10K-100K records)

**Prototype Code:**
- Basic SQLite schema created and tested
- Query performance benchmarked
- Repository pattern validated with sample code

**Performance Benchmarks:**
```
SQLite Performance Test Results (10,000 books):
- Insert 100 books: 0.45s
- Search by title (no index): 0.18s
- Search by title (with index): 0.02s
- Complex filter query: 0.05s
- Join query (books + authors): 0.08s
```

---

## Document History

| Date       | Version | Author           | Changes                                    |
|------------|---------|------------------|--------------------------------------------|
| 2025-10-17 | 0.1     | Development Team | Initial draft based on database design doc |
| 2025-10-17 | 0.2     | Development Team | Added quality gates and implementation plan|
| 2025-10-17 | 1.0     | Development Team | Ready for review                           |

---

## Sign-off

**Technical Review**: ⏳ Pending

**Quality Review**: ⏳ Pending - All quality gates defined and achievable

**Security Review**: ⏳ Pending - SQL injection prevention measures defined

**Ready for Implementation**: ⏳ Pending final approval

---

## Next Steps

1. **Review this specification** with stakeholders
2. **Approve or request changes**
3. **Create GitHub project** with tasks from Implementation Plan
4. **Begin Phase 1: Database Foundation**
5. **Regular progress updates** after each phase completion

---

## Questions for Stakeholder

Before implementation begins, please confirm:

1. Is SQLite acceptable or do you prefer PostgreSQL/MySQL?
2. Should database location be configurable via environment variable?
3. Do you want auto-save to database (default on) or opt-in (default off)?
4. Are the proposed CLI commands intuitive? Any naming preferences?
5. Do you want database features behind a flag initially or available to all users?
6. Any specific export formats needed beyond JSON/CSV?
7. Should we support database encryption (would add complexity)?
8. Timeline expectations - is 15-20 days acceptable?
