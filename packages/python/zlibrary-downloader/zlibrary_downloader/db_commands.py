"""Command handlers for database operations.

This module provides CLI command handlers for database operations,
using service layer for all operations and displaying user-friendly output.
"""

import argparse
import json
import os
from typing import Any, List, Optional

from .db_manager import DatabaseManager
from .book_service import BookService, BookDetails, SavedBook
from .book_repository import BookRepository
from .author_repository import AuthorRepository
from .list_service import ListService
from .list_repository import ReadingListRepository
from .download_service import DownloadService
from .download_repository import DownloadRepository
from .models import Book, Author


def db_init_command(args: argparse.Namespace) -> None:
    """
    Initialize the database.

    Creates database file, schema, tables, and indexes.

    Args:
        args: Command line arguments (unused)
    """
    try:
        print("Initializing database...")
        db_manager = DatabaseManager()
        db_manager.initialize_schema()
        print(f"✓ Database initialized successfully at: {db_manager.db_path}")
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        raise


def _format_book_row(book: Book, authors: Optional[List[Author]] = None) -> str:
    """
    Format a book as a single row for display.

    Args:
        book: Book to format
        authors: Optional list of authors

    Returns:
        str: Formatted book row
    """
    author_str = ", ".join(a.name for a in authors) if authors else "N/A"
    return (
        f"ID: {book.id} | {book.title} | "
        f"Author: {author_str} | Year: {book.year or 'N/A'} | "
        f"Format: {book.extension or 'N/A'}"
    )


def db_browse_command(args: argparse.Namespace) -> None:
    """
    Browse books in the database.

    Displays books matching filter criteria.

    Args:
        args: Command line arguments with filter options
    """
    try:
        db_manager = DatabaseManager()
        book_repo = BookRepository(db_manager)
        author_repo = AuthorRepository(db_manager)
        book_service = BookService(book_repo, author_repo)

        books = book_service.browse_books(
            query=getattr(args, "query", None),
            language=getattr(args, "language", None),
            year_from=(
                str(getattr(args, "year_from", ""))
                if hasattr(args, "year_from") and args.year_from
                else None
            ),
            year_to=(
                str(getattr(args, "year_to", ""))
                if hasattr(args, "year_to") and args.year_to
                else None
            ),
            extension=getattr(args, "format", None),
            author=getattr(args, "author", None),
            limit=getattr(args, "limit", 50),
        )

        if not books:
            print("No books found matching your criteria.")
            return

        print(f"\nFound {len(books)} books:\n")
        for book in books:
            authors = author_repo.get_authors_for_book(book.id)
            print(_format_book_row(book, authors))

    except Exception as e:
        print(f"❌ Error browsing books: {e}")
        raise


def _display_book_details(details: BookDetails) -> None:
    """
    Display detailed book information.

    Args:
        details: BookDetails object to display
    """
    book = details.book
    print("\n" + "=" * 60)
    print("Book Details")
    print("=" * 60)
    print(f"ID: {book.id}")
    print(f"Title: {book.title}")
    print(f"Authors: {', '.join(a.name for a in details.authors) if details.authors else 'N/A'}")
    print(f"Year: {book.year or 'N/A'}")
    print(f"Publisher: {book.publisher or 'N/A'}")
    print(f"Language: {book.language or 'N/A'}")
    print(f"Format: {book.extension or 'N/A'}")
    print(f"Size: {book.size or 'N/A'}")
    if book.description:
        print(f"Description: {book.description}")
    print("=" * 60)


def db_show_command(args: argparse.Namespace) -> None:
    """
    Show detailed book information.

    Args:
        args: Command line arguments with book_id
    """
    try:
        db_manager = DatabaseManager()
        book_repo = BookRepository(db_manager)
        author_repo = AuthorRepository(db_manager)
        book_service = BookService(book_repo, author_repo)

        details = book_service.get_book_details(str(args.book_id))
        _display_book_details(details)

    except ValueError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Error showing book details: {e}")
        raise


def db_save_command(args: argparse.Namespace) -> None:
    """
    Save a book to saved collection.

    Args:
        args: Command line arguments with book_id and metadata
    """
    try:
        db_manager = DatabaseManager()
        book_repo = BookRepository(db_manager)
        author_repo = AuthorRepository(db_manager)
        book_service = BookService(book_repo, author_repo)

        book_service.save_book(
            book_id=str(args.book_id),
            notes=getattr(args, "notes", None),
            tags=getattr(args, "tags", None),
            priority=getattr(args, "priority", 0) or 0,
        )

        print(f"✓ Book {args.book_id} saved successfully")

    except ValueError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Error saving book: {e}")
        raise


def db_unsave_command(args: argparse.Namespace) -> None:
    """
    Remove a book from saved collection.

    Args:
        args: Command line arguments with book_id
    """
    try:
        db_manager = DatabaseManager()
        book_repo = BookRepository(db_manager)
        author_repo = AuthorRepository(db_manager)
        book_service = BookService(book_repo, author_repo)

        removed = book_service.unsave_book(str(args.book_id))

        if removed:
            print(f"✓ Book {args.book_id} removed from saved books")
        else:
            print(f"Book {args.book_id} was not in saved books")

    except Exception as e:
        print(f"❌ Error removing book: {e}")
        raise


def _display_saved_book(saved: SavedBook, index: int) -> None:
    """
    Display a saved book with its metadata.

    Args:
        saved: SavedBook object to display
        index: Display index number
    """
    book = saved.book
    author_str = ", ".join(a.name for a in saved.authors) if saved.authors else "N/A"

    print(f"\n{index}. {book.title}")
    print(f"   ID: {book.id} | Authors: {author_str}")
    print(f"   Year: {book.year or 'N/A'} | Format: {book.extension or 'N/A'}")
    if saved.priority:
        print(f"   Priority: {saved.priority}")
    if saved.tags:
        print(f"   Tags: {saved.tags}")
    if saved.notes:
        print(f"   Notes: {saved.notes}")
    if saved.saved_at:
        print(f"   Saved: {saved.saved_at}")


def db_saved_command(args: argparse.Namespace) -> None:
    """
    List all saved books.

    Args:
        args: Command line arguments (unused)
    """
    try:
        db_manager = DatabaseManager()
        book_repo = BookRepository(db_manager)
        author_repo = AuthorRepository(db_manager)
        book_service = BookService(book_repo, author_repo)

        saved_books = book_service.get_saved_books()

        if not saved_books:
            print("No saved books found.")
            print("Use 'db save <book-id>' to save books.")
            return

        print(f"\nSaved Books ({len(saved_books)}):")
        for idx, saved in enumerate(saved_books, 1):
            _display_saved_book(saved, idx)

    except Exception as e:
        print(f"❌ Error listing saved books: {e}")
        raise


def db_list_create_command(args: argparse.Namespace) -> None:
    """
    Create a new reading list.

    Args:
        args: Command line arguments with list name and description
    """
    try:
        db_manager = DatabaseManager()
        list_repo = ReadingListRepository(db_manager)
        book_repo = BookRepository(db_manager)
        list_service = ListService(list_repo, book_repo)

        reading_list = list_service.create_list(
            name=args.name, description=getattr(args, "description", "") or ""
        )

        print(f"✓ Created reading list: {reading_list.name}")

    except ValueError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Error creating list: {e}")
        raise


def db_list_show_command(args: argparse.Namespace) -> None:
    """
    Show books in a reading list.

    Args:
        args: Command line arguments with list name
    """
    try:
        db_manager = DatabaseManager()
        list_repo = ReadingListRepository(db_manager)
        book_repo = BookRepository(db_manager)
        author_repo = AuthorRepository(db_manager)
        list_service = ListService(list_repo, book_repo)

        reading_list, books = list_service.get_list_with_books(args.name)

        print(f"\nReading List: {reading_list.name}")
        if reading_list.description:
            print(f"Description: {reading_list.description}")
        print(f"Created: {reading_list.created_at}")
        print(f"\nBooks ({len(books)}):\n")

        if not books:
            print("  (No books in this list)")
            print("  Use 'db list-add' to add books")
        else:
            for idx, book in enumerate(books, 1):
                authors = author_repo.get_authors_for_book(book.id)
                print(f"{idx}. {_format_book_row(book, authors)}")

    except ValueError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Error showing list: {e}")
        raise


def db_list_add_command(args: argparse.Namespace) -> None:
    """
    Add a book to a reading list.

    Args:
        args: Command line arguments with list name and book ID
    """
    try:
        db_manager = DatabaseManager()
        list_repo = ReadingListRepository(db_manager)
        book_repo = BookRepository(db_manager)
        list_service = ListService(list_repo, book_repo)

        list_service.add_book_to_list(args.name, str(args.book_id))
        print(f"✓ Added book {args.book_id} to list '{args.name}'")

    except ValueError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Error adding book to list: {e}")
        raise


def db_list_remove_command(args: argparse.Namespace) -> None:
    """
    Remove a book from a reading list.

    Args:
        args: Command line arguments with list name and book ID
    """
    try:
        db_manager = DatabaseManager()
        list_repo = ReadingListRepository(db_manager)
        book_repo = BookRepository(db_manager)
        list_service = ListService(list_repo, book_repo)

        removed = list_service.remove_book_from_list(args.name, str(args.book_id))

        if removed:
            print(f"✓ Removed book {args.book_id} from list '{args.name}'")
        else:
            print(f"Book {args.book_id} was not in list '{args.name}'")

    except ValueError as e:
        print(f"❌ {e}")
    except Exception as e:
        print(f"❌ Error removing book from list: {e}")
        raise


def db_list_delete_command(args: argparse.Namespace) -> None:
    """
    Delete a reading list with confirmation.

    Args:
        args: Command line arguments with list name
    """
    try:
        # Prompt for confirmation
        confirmation = (
            input(f"Are you sure you want to delete list '{args.name}'? (y/N): ").strip().lower()
        )

        if confirmation != "y":
            print("Cancelled")
            return

        db_manager = DatabaseManager()
        list_repo = ReadingListRepository(db_manager)
        book_repo = BookRepository(db_manager)
        list_service = ListService(list_repo, book_repo)

        deleted = list_service.delete_list(args.name)

        if deleted:
            print(f"✓ Deleted reading list: {args.name}")
        else:
            print(f"List '{args.name}' not found")

    except Exception as e:
        print(f"❌ Error deleting list: {e}")
        raise


def db_lists_command(args: argparse.Namespace) -> None:
    """
    List all reading lists with book counts.

    Args:
        args: Command line arguments (unused)
    """
    try:
        db_manager = DatabaseManager()
        list_repo = ReadingListRepository(db_manager)
        book_repo = BookRepository(db_manager)
        list_service = ListService(list_repo, book_repo)

        lists = list_service.get_all_lists()

        if not lists:
            print("No reading lists found.")
            print("Use 'db list-create' to create one.")
            return

        print(f"\nReading Lists ({len(lists)}):\n")

        for idx, reading_list in enumerate(lists, 1):
            books = list_repo.get_books(reading_list.id) if reading_list.id else []
            book_count = len(books)

            print(f"{idx}. {reading_list.name}")
            print(f"   Books: {book_count}")
            if reading_list.description:
                print(f"   Description: {reading_list.description}")
            print(f"   Created: {reading_list.created_at}")
            print()

    except Exception as e:
        print(f"❌ Error listing reading lists: {e}")
        raise


def db_downloads_command(args: argparse.Namespace) -> None:
    """
    Show download history.

    Args:
        args: Command line arguments with optional filters
    """
    try:
        db_manager = DatabaseManager()
        download_repo = DownloadRepository(db_manager)
        download_service = DownloadService(download_repo)

        recent_days = getattr(args, "recent", None)
        credential_id = getattr(args, "credential", None)

        downloads = download_service.get_download_history(
            limit=getattr(args, "limit", 50),
            recent_days=recent_days,
            credential_id=credential_id,
        )

        if not downloads:
            print("No downloads found.")
            return

        print(f"\nDownload History ({len(downloads)}):\n")

        for idx, download in enumerate(downloads, 1):
            print(f"{idx}. {download.filename}")
            print(f"   Book ID: {download.book_id}")
            print(f"   Path: {download.file_path}")
            print(f"   Size: {download.file_size} bytes")
            print(f"   Status: {download.status}")
            print(f"   Downloaded: {download.downloaded_at}")
            if credential_id or download.credential_id:
                print(f"   Credential: {download.credential_id or 'N/A'}")
            print()

    except Exception as e:
        print(f"❌ Error showing download history: {e}")
        raise


def db_stats_command(args: argparse.Namespace) -> None:
    """
    Display database statistics.

    Args:
        args: Command line arguments (unused)
    """
    try:
        db_manager = DatabaseManager()
        book_repo = BookRepository(db_manager)

        print("\n" + "=" * 60)
        print("Database Statistics")
        print("=" * 60)

        # Total books
        total_books = book_repo.count()
        print(f"Total books: {total_books}")

        # Books by language
        conn = db_manager.get_connection()
        cursor = conn.execute(
            "SELECT language, COUNT(*) as count FROM books "
            "WHERE language IS NOT NULL GROUP BY language ORDER BY count DESC LIMIT 10"
        )
        print("\nTop languages:")
        for lang, count in cursor.fetchall():
            print(f"  {lang}: {count}")

        # Books by format
        cursor = conn.execute(
            "SELECT extension, COUNT(*) as count FROM books "
            "WHERE extension IS NOT NULL GROUP BY extension ORDER BY count DESC"
        )
        print("\nFormats:")
        for ext, count in cursor.fetchall():
            print(f"  {ext}: {count}")

        # Download stats
        cursor = conn.execute("SELECT COUNT(*) FROM downloads")
        total_downloads = cursor.fetchone()[0]
        print(f"\nTotal downloads: {total_downloads}")

        # Database file size
        db_size = os.path.getsize(db_manager.db_path)
        db_size_mb = db_size / (1024 * 1024)
        print(f"Database size: {db_size_mb:.2f} MB")

        print("=" * 60)

    except Exception as e:
        print(f"❌ Error showing database stats: {e}")
        raise


def db_export_command(args: argparse.Namespace) -> None:
    """
    Export books to JSON or CSV.

    Args:
        args: Command line arguments with format and output options
    """
    try:
        db_manager = DatabaseManager()
        book_repo = BookRepository(db_manager)
        author_repo = AuthorRepository(db_manager)

        books = book_repo.search()
        output_format = getattr(args, "format", "json").lower()
        output_file = getattr(args, "output", f"books_export.{output_format}")

        print(f"Exporting {len(books)} books to {output_file}...")

        if output_format == "json":
            # Export to JSON
            export_data = []
            for book in books:
                authors = author_repo.get_authors_for_book(book.id)
                book_dict = book.to_dict()
                book_dict["authors"] = [a.name for a in authors]
                export_data.append(book_dict)

            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(export_data, f, indent=2, ensure_ascii=False)

        elif output_format == "csv":
            # Export to CSV
            import csv

            with open(output_file, "w", encoding="utf-8", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(
                    ["ID", "Title", "Authors", "Year", "Publisher", "Language", "Extension", "Size"]
                )
                for book in books:
                    authors = author_repo.get_authors_for_book(book.id)
                    author_names = "; ".join(a.name for a in authors)
                    writer.writerow(
                        [
                            book.id,
                            book.title,
                            author_names,
                            book.year or "",
                            book.publisher or "",
                            book.language or "",
                            book.extension or "",
                            book.size or "",
                        ]
                    )
        else:
            print(f"❌ Unsupported format: {output_format}")
            return

        print(f"✓ Successfully exported to {output_file}")

    except Exception as e:
        print(f"❌ Error exporting books: {e}")
        raise


def db_import_command(args: argparse.Namespace) -> None:
    """
    Import books from JSON file.

    Args:
        args: Command line arguments with input file
    """
    try:
        input_file = args.input
        if not os.path.exists(input_file):
            print(f"❌ File not found: {input_file}")
            return

        db_manager = DatabaseManager()
        book_repo = BookRepository(db_manager)
        author_repo = AuthorRepository(db_manager)

        print(f"Importing books from {input_file}...")

        with open(input_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            print("❌ Invalid JSON format: expected list of books")
            return

        imported = 0
        for item in data:
            try:
                # Extract authors separately
                author_names = item.pop("authors", [])

                # Create book from dict
                book = Book.from_dict(item)
                book_repo.upsert(book)

                # Link authors
                if author_names:
                    for order, author_name in enumerate(author_names):
                        author = author_repo.get_or_create(author_name)
                        if author.id and book.id:
                            author_repo.link_book_author(book.id, author.id, order)

                imported += 1
                if imported % 10 == 0:
                    print(f"  Imported {imported} books...")

            except Exception as e:
                print(f"  ⚠️  Failed to import book: {e}")
                continue

        print(f"✓ Successfully imported {imported} books")

    except Exception as e:
        print(f"❌ Error importing books: {e}")
        raise


def db_vacuum_command(args: argparse.Namespace) -> None:
    """
    Optimize database file.

    This command rebuilds the database file, reclaiming unused space
    and optimizing internal structures.

    Args:
        args: Command line arguments (unused)
    """
    try:
        db_manager = DatabaseManager()

        # Get size before
        size_before = os.path.getsize(db_manager.db_path)
        size_before_mb = size_before / (1024 * 1024)

        print("Optimizing database...")
        print(f"Size before: {size_before_mb:.2f} MB")

        conn = db_manager.get_connection()
        conn.execute("VACUUM")
        conn.execute("ANALYZE")

        # Get size after
        size_after = os.path.getsize(db_manager.db_path)
        size_after_mb = size_after / (1024 * 1024)
        saved_mb = (size_before - size_after) / (1024 * 1024)

        print(f"Size after: {size_after_mb:.2f} MB")
        print(f"Space saved: {saved_mb:.2f} MB")
        print("✓ Database optimized successfully")

    except Exception as e:
        print(f"❌ Error optimizing database: {e}")
        raise



def db_preview_command(args: Any) -> None:
    """Generate HTML preview of books with cover images"""
    import webbrowser
    import tempfile
    from pathlib import Path
    
    db_manager = DatabaseManager()
    book_repo = BookRepository(db_manager)
    author_repo = AuthorRepository(db_manager)
    
    # Build filters
    filters = {}
    if hasattr(args, 'language') and args.language:
        filters['language'] = args.language
    if hasattr(args, 'format') and args.format:
        filters['format'] = args.format
    if hasattr(args, 'year') and args.year:
        filters['year'] = args.year
    
    # Get books
    books = book_repo.search(**filters)
    
    # Limit results
    limit = getattr(args, 'limit', 50)
    books = books[:limit]
    
    if not books:
        print("No books found in database.")
        print("Try searching with --save-db to add books first.")
        return
    
    # Generate HTML
    html = generate_books_html(books, author_repo)
    
    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8')
    temp_file.write(html)
    temp_file.close()
    
    temp_path = Path(temp_file.name)
    print(f"\n✓ Generated preview: {temp_path}")
    print(f"  Books displayed: {len(books)}")
    
    # Open in browser
    if not getattr(args, 'no_open', False):
        print(f"  Opening in browser...")
        webbrowser.open(f'file://{temp_path}')
    else:
        print(f"\n  To view: open file://{temp_path}")


def generate_books_html(books: list, author_repo: Any) -> str:
    """Generate HTML page with book covers"""
    
    html_parts = ['''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Z-Library Books Preview</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 20px;
            min-height: 100vh;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        header {
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
            margin-bottom: 30px;
            text-align: center;
        }
        h1 {
            color: #667eea;
            font-size: 2.5rem;
            margin-bottom: 10px;
        }
        .subtitle {
            color: #666;
            font-size: 1.1rem;
        }
        .books-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 25px;
            margin-top: 20px;
        }
        .book-card {
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.15);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }
        .book-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.25);
        }
        .book-cover {
            width: 100%;
            height: 350px;
            object-fit: cover;
            background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        }
        .book-cover.no-cover {
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 3rem;
            color: #999;
        }
        .book-info {
            padding: 15px;
        }
        .book-title {
            font-size: 1rem;
            font-weight: 600;
            color: #333;
            margin-bottom: 8px;
            line-height: 1.3;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .book-author {
            font-size: 0.9rem;
            color: #667eea;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 1;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .book-meta {
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }
        .meta-tag {
            font-size: 0.75rem;
            padding: 4px 10px;
            border-radius: 12px;
            background: #f0f0f0;
            color: #555;
        }
        .meta-tag.format {
            background: #e3f2fd;
            color: #1976d2;
        }
        .meta-tag.year {
            background: #f3e5f5;
            color: #7b1fa2;
        }
        .meta-tag.language {
            background: #e8f5e9;
            color: #388e3c;
        }
        .stats {
            background: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            box-shadow: 0 5px 20px rgba(0, 0, 0, 0.1);
            text-align: center;
        }
        @media (max-width: 768px) {
            .books-grid {
                grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
                gap: 15px;
            }
            .book-cover {
                height: 220px;
            }
            h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>📚 Z-Library Books Collection</h1>
            <p class="subtitle">Browse your saved books with beautiful cover images</p>
        </header>
        
        <div class="stats">
            <strong>''' + str(len(books)) + '''</strong> books displayed
        </div>
        
        <div class="books-grid">
''']
    
    # Add book cards
    for book in books:
        # Get authors
        authors = author_repo.get_authors_for_book(book.id)
        author_names = ", ".join([a.name for a in authors]) if authors else "Unknown Author"
        
        # Build cover image or placeholder
        if book.cover_url:
            cover_html = f'<img src="{book.cover_url}" alt="{book.title}" class="book-cover" loading="lazy" onerror="this.parentElement.querySelector(\'.no-cover\').style.display=\'flex\'; this.style.display=\'none\';">'
            cover_html += '<div class="book-cover no-cover" style="display:none;">📖</div>'
        else:
            cover_html = '<div class="book-cover no-cover">📖</div>'
        
        # Build meta tags
        meta_tags = []
        if book.extension:
            meta_tags.append(f'<span class="meta-tag format">{book.extension.upper()}</span>')
        if book.year:
            meta_tags.append(f'<span class="meta-tag year">{book.year}</span>')
        if book.language:
            meta_tags.append(f'<span class="meta-tag language">{book.language}</span>')
        
        meta_html = ''.join(meta_tags)
        
        html_parts.append(f'''
            <div class="book-card">
                {cover_html}
                <div class="book-info">
                    <div class="book-title">{book.title}</div>
                    <div class="book-author">{author_names}</div>
                    <div class="book-meta">
                        {meta_html}
                    </div>
                </div>
            </div>
        ''')
    
    html_parts.append('''
        </div>
    </div>
</body>
</html>
''')
    
    return ''.join(html_parts)
