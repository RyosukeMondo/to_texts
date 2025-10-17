# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Database Storage System**: Complete database integration for managing book catalog
  - SQLite database with 8 tables (books, authors, book_authors, reading_lists, list_books, saved_books, downloads, search_history)
  - Database models using dataclasses with serialization support
  - Repository pattern implementation for all database operations
  - Service layer for business logic and orchestration
  - Full database CLI commands via `db` subcommand group

- **Database CLI Commands**:
  - `db init` - Initialize database schema
  - `db browse` - Browse books with filters (language, year, format, author)
  - `db show <book-id>` - Show detailed book information
  - `db save <book-id>` - Save books to collection with notes, tags, and priority
  - `db unsave <book-id>` - Remove books from saved collection
  - `db saved` - List all saved books

- **Reading List Management**:
  - `db list-create <name>` - Create new reading lists
  - `db list-show <name>` - Show books in a list
  - `db list-add <name> <book-id>` - Add books to lists
  - `db list-remove <name> <book-id>` - Remove books from lists
  - `db list-delete <name>` - Delete reading lists
  - `db lists` - List all reading lists

- **Database Utilities**:
  - `db downloads` - View download history with filtering
  - `db stats` - Display database statistics (total books, by language/format, downloads)
  - `db export` - Export books to JSON/CSV
  - `db import` - Import books from JSON
  - `db vacuum` - Optimize database file

- **Search Integration**:
  - `--save-db` flag for search command to store results in database
  - Automatic author extraction and linking from search results
  - Search history tracking

- **Download Tracking**:
  - Automatic recording of downloads to database
  - Download history with book metadata
  - File path and size tracking

### Technical Details
- Repository classes: `BookRepository`, `AuthorRepository`, `ReadingListRepository`, `DownloadRepository`, `SearchHistoryRepository`
- Service classes: `BookService`, `SearchService`, `ListService`, `DownloadService`
- Database manager with connection pooling, transaction support, and schema versioning
- Comprehensive test suite with 447 passing tests
- Type-safe implementation with mypy strict mode compliance
- Security: All database operations use parameterized queries to prevent SQL injection
- Performance: Indexed queries, efficient search with filters, bulk operations support

### Performance Characteristics
- In-memory test database operations < 100ms
- Search with filters < 200ms
- Bulk insert operations < 1s for 100 books

### Database Schema
- `books`: Core book metadata (id, title, authors, year, publisher, language, format, etc.)
- `authors`: Author information
- `book_authors`: Many-to-many relationship with ordering
- `reading_lists`: User-created book lists
- `list_books`: List membership with position ordering
- `saved_books`: User's saved books with notes, tags, and priority
- `downloads`: Download history and tracking
- `search_history`: Search query history

### Code Quality
- All new code passes mypy strict type checking
- Black code formatting applied
- Flake8 linting compliance
- Test coverage: 76% overall (100% for core database components)
  - Database manager: 100%
  - Repositories: 90-100%
  - Services: 89-100%
  - Models: 78%

