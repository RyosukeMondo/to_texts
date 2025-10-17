"""Performance tests for database operations."""

import time
from typing import Tuple
from zlibrary_downloader.models import Book
from zlibrary_downloader.db_manager import DatabaseManager
from zlibrary_downloader.book_repository import BookRepository
from zlibrary_downloader.author_repository import AuthorRepository


def create_test_book(book_id: int) -> Tuple[Book, str]:
    """Create a test book with given ID and return book + author name."""
    book = Book(
        id=str(book_id),
        hash=f"hash{book_id}",
        title=f"Test Book {book_id}",
        year=str(2000 + (book_id % 24)),
        publisher=f"Publisher {book_id % 10}",
        language="english" if book_id % 3 == 0 else "spanish",
        extension="pdf" if book_id % 2 == 0 else "epub",
        size=f"{book_id} KB",
        filesize=1024 * book_id,
        cover_url=f"http://example.com/cover{book_id}.jpg",
        description=f"Test description for book {book_id}",
    )
    author_name = f"Author {book_id % 100}"
    return book, author_name


def setup_large_dataset(
    book_repo: BookRepository, author_repo: AuthorRepository, count: int
) -> None:
    """Populate database with test books."""
    for i in range(count):
        book, author_name = create_test_book(i)
        book_repo.create(book)
        author = author_repo.get_or_create(author_name)
        if author.id is not None:
            author_repo.link_book_author(book.id, author.id, 0)


def test_bulk_insert_performance() -> None:
    """Test bulk insert of 100 books completes in <1s."""
    db_manager = DatabaseManager(":memory:")
    db_manager.initialize_schema()
    book_repo = BookRepository(db_manager)
    author_repo = AuthorRepository(db_manager)

    books_data = [create_test_book(i) for i in range(100)]

    start = time.time()
    for book, author_name in books_data:
        book_repo.create(book)
        author = author_repo.get_or_create(author_name)
        if author.id is not None:
            author_repo.link_book_author(book.id, author.id, 0)
    duration = time.time() - start

    db_manager.close()
    assert duration < 1.0, f"Bulk insert took {duration:.3f}s, expected <1s"


def test_search_performance_large_db() -> None:
    """Test search in 10000 books completes in <200ms."""
    db_manager = DatabaseManager(":memory:")
    db_manager.initialize_schema()
    book_repo = BookRepository(db_manager)
    author_repo = AuthorRepository(db_manager)

    setup_large_dataset(book_repo, author_repo, 10000)

    start = time.time()
    results = book_repo.search(query="Test")
    duration = time.time() - start

    db_manager.close()
    assert duration < 0.2, f"Search took {duration:.3f}s, expected <200ms"
    assert len(results) > 0


def test_browse_with_filters_performance() -> None:
    """Test browse with complex filters completes in <200ms."""
    db_manager = DatabaseManager(":memory:")
    db_manager.initialize_schema()
    book_repo = BookRepository(db_manager)
    author_repo = AuthorRepository(db_manager)

    setup_large_dataset(book_repo, author_repo, 10000)

    start = time.time()
    _ = book_repo.search(language="english", year_from="2010", year_to="2020", extension="pdf")
    duration = time.time() - start

    db_manager.close()
    assert duration < 0.2, f"Filtered browse took {duration:.3f}s, expected <200ms"


def test_upsert_performance() -> None:
    """Test upsert of existing books is fast."""
    db_manager = DatabaseManager(":memory:")
    db_manager.initialize_schema()
    book_repo = BookRepository(db_manager)

    # Create initial books
    books_data = [create_test_book(i) for i in range(100)]
    books = [book for book, _ in books_data]
    for book in books:
        book_repo.create(book)

    # Upsert same books with modified data
    for book in books:
        book.title = f"Updated {book.title}"

    start = time.time()
    for book in books:
        book_repo.upsert(book)
    duration = time.time() - start

    db_manager.close()
    assert duration < 1.0, f"Upsert took {duration:.3f}s, expected <1s"
