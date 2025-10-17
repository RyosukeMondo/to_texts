# Database Features Guide

Complete guide to using the Z-Library Downloader's local database for cataloging, organizing, and tracking your book collection.

## Quick Start

```bash
# 1. Initialize database
zlibrary-downloader db init

# 2. Search and store results
zlibrary-downloader search --title "Python Programming" --save-db

# 3. Browse your catalog
zlibrary-downloader db browse --language english --format pdf
```

## Command Reference

### Core Commands

**db init** - Initialize database (creates `~/.zlibrary/books.db`)

**db browse** - Browse books with optional filters
```bash
zlibrary-downloader db browse [--query TEXT] [--language LANG]
  [--year-from YYYY] [--year-to YYYY] [--format FMT] [--author NAME] [--limit N]
```

**db show** - View detailed book information
```bash
zlibrary-downloader db show <book-id>
```

### Saved Books

**db save** - Add book to saved collection with metadata
```bash
zlibrary-downloader db save <book-id> [--notes "text"] [--tags "tag1,tag2"] [--priority 1-5]
```

**db unsave** - Remove from saved collection
```bash
zlibrary-downloader db unsave <book-id>
```

**db saved** - List all saved books
```bash
zlibrary-downloader db saved
```

### Reading Lists

**db list-create** - Create reading list
```bash
zlibrary-downloader db list-create "List Name" [--description "text"]
```

**db lists** - View all reading lists with book counts

**db list-show** - Display books in a list
```bash
zlibrary-downloader db list-show "List Name"
```

**db list-add** - Add book to list
```bash
zlibrary-downloader db list-add "List Name" <book-id>
```

**db list-remove** - Remove book from list
```bash
zlibrary-downloader db list-remove "List Name" <book-id>
```

**db list-delete** - Delete reading list (prompts for confirmation)
```bash
zlibrary-downloader db list-delete "List Name"
```

### Download Tracking

**db downloads** - View download history
```bash
zlibrary-downloader db downloads [--recent DAYS] [--credential NAME] [--limit N]
```

Downloads are automatically tracked when database is initialized.

### Database Utilities

**db stats** - Display database statistics (total books, languages, formats, downloads, size)

**db export** - Export books to JSON/CSV
```bash
zlibrary-downloader db export [--format json|csv] [--output FILE]
```

**db import** - Import books from JSON
```bash
zlibrary-downloader db import --input FILE
```

**db vacuum** - Optimize database (reclaim space, rebuild indexes)

## Common Workflows

### Building a Library Catalog

```bash
# Search and store multiple topics
zlibrary-downloader search --title "Python" --save-db
zlibrary-downloader search --title "JavaScript" --save-db
zlibrary-downloader search --title "Data Science" --save-db

# Browse by category
zlibrary-downloader db browse --language english --limit 100

# Create topic lists
zlibrary-downloader db list-create "Python Books"
zlibrary-downloader db list-create "Web Development"

# Add books to lists
zlibrary-downloader db list-add "Python Books" <book-id>
```

### Managing Reading Queue

```bash
# Create priority list
zlibrary-downloader db list-create "Reading Queue" --description "Books to read next"

# Save with priority
zlibrary-downloader db save <book-id> --priority 5 --tags "urgent,learning"

# View saved books
zlibrary-downloader db saved

# Add to queue
zlibrary-downloader db list-add "Reading Queue" <book-id>
```

### Backup and Restore

```bash
# Export catalog
zlibrary-downloader db export --output backup_$(date +%Y%m%d).json

# Restore on new machine
zlibrary-downloader db init
zlibrary-downloader db import --input backup_20241017.json
```

## Troubleshooting

### Database Locked
**Error:** `database is locked`

**Solutions:**
1. Close other zlibrary-downloader instances
2. Wait and retry
3. Restart terminal
4. Remove lock files: `rm ~/.zlibrary/books.db-wal ~/.zlibrary/books.db-shm`

### Database Corruption
**Error:** `database disk image is malformed`

**Solutions:**
```bash
# Try vacuum first
zlibrary-downloader db vacuum

# If that fails, export and reimport
zlibrary-downloader db export --output backup.json
rm ~/.zlibrary/books.db
zlibrary-downloader db init
zlibrary-downloader db import --input backup.json
```

### Permission Denied
**Error:** `Permission denied: /home/user/.zlibrary/books.db`

**Solution:**
```bash
chmod 600 ~/.zlibrary/books.db
chmod 700 ~/.zlibrary/
```

### Book Not Found After Search
**Problem:** Searched with --save-db but can't find books

**Solutions:**
1. Verify search returned results
2. Check database initialized: `zlibrary-downloader db init`
3. Verify with stats: `zlibrary-downloader db stats`
4. Check ZLIBRARY_DB_PATH environment variable

### Duplicate Books
**Problem:** Same book appearing multiple times

**Explanation:** Different Z-Library book IDs represent different editions/versions (expected behavior)

**Solutions:**
- Use filters to narrow results: `--year-from`, `--language`
- Check details: `db show <book-id>`

### Import Fails
**Error:** `Invalid JSON format: expected list of books`

**Solution:** Ensure JSON is array of book objects:
```json
[{"id": "abc123", "title": "Book Title", "year": "2020", ...}]
```

### Performance Issues
**Problem:** Slow queries on large database (>10,000 books)

**Solutions:**
1. Use specific filters in browse
2. Reduce --limit value
3. Run vacuum: `zlibrary-downloader db vacuum`
4. Indexes are auto-created by init

## Advanced Topics

### Custom Database Location
```bash
export ZLIBRARY_DB_PATH="/path/to/custom/books.db"
zlibrary-downloader db init
```
Add to `.bashrc`/`.zshrc` to persist.

### Maintenance Schedule

**Weekly:** Review saved books (`db saved`), update lists

**Monthly:** Check stats (`db stats`), export backup

**Quarterly:** Vacuum database, review downloads

### Programmatic Access

SQLite database - access with any SQLite tool:
```bash
sqlite3 ~/.zlibrary/books.db "SELECT title, year FROM books WHERE language='english' LIMIT 10"
```

Schema: See `docs/zlibrary-database-design.md`

### Integration Examples

**Export to spreadsheet:**
```bash
zlibrary-downloader db export --format csv --output books.csv
# Open in Excel, Google Sheets, etc.
```

**Automated backups (cron):**
```bash
0 0 * * 0 zlibrary-downloader db export --output ~/backups/books_$(date +\%Y\%m\%d).json
```

**Filter and save:**
```bash
zlibrary-downloader db browse --language english --year-from 2020 --format pdf > recent_pdfs.txt
```

## Environment Variables

- `ZLIBRARY_DB_PATH` - Custom database location (default: `~/.zlibrary/books.db`)

## Database Schema

The database uses SQLite with the following tables:
- `books` - Book metadata
- `authors` - Author information
- `book_authors` - Book-author relationships (many-to-many)
- `reading_lists` - User reading lists
- `list_books` - List membership with ordering
- `saved_books` - Saved books with notes, tags, priority
- `downloads` - Download tracking
- `search_history` - Search query history

Full schema documentation: `docs/zlibrary-database-design.md`
