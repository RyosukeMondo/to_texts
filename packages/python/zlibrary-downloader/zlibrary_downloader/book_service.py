"""Service layer for book operations.

This module provides the BookService class that orchestrates book operations
across BookRepository and AuthorRepository, handling business logic and
providing user-friendly error messages.
"""

from typing import List, Optional, Any
from dataclasses import dataclass

from .book_repository import BookRepository
from .author_repository import AuthorRepository
from .models import Book, Author


@dataclass
class BookDetails:
    """
    Enriched book details with authors.

    Attributes:
        book: Book instance
        authors: List of authors for the book
    """

    book: Book
    authors: List[Author]


@dataclass
class SavedBook:
    """
    Saved book with metadata.

    Attributes:
        book: Book instance
        authors: List of authors
        notes: User notes
        tags: User tags
        priority: Priority level
        saved_at: When book was saved
    """

    book: Book
    authors: List[Author]
    notes: Optional[str] = None
    tags: Optional[str] = None
    priority: int = 0
    saved_at: Optional[str] = None


class BookService:
    """
    Service layer for book operations.

    Orchestrates book operations across repositories and provides
    business logic with clear error handling.

    Attributes:
        book_repo: BookRepository instance
        author_repo: AuthorRepository instance
    """

    def __init__(self, book_repo: BookRepository, author_repo: AuthorRepository) -> None:
        """
        Initialize BookService.

        Args:
            book_repo: BookRepository instance
            author_repo: AuthorRepository instance
        """
        self.book_repo = book_repo
        self.author_repo = author_repo

    def get_book_details(self, book_id: str) -> BookDetails:
        """
        Get book details with authors.

        Args:
            book_id: Book ID to retrieve

        Returns:
            BookDetails: Book with authors

        Raises:
            ValueError: If book not found
        """
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise ValueError(
                f"Book not found: {book_id}. " "Use 'db browse' to see available books."
            )

        authors = self.author_repo.get_authors_for_book(book_id)
        return BookDetails(book=book, authors=authors)

    def browse_books(
        self,
        query: Optional[str] = None,
        language: Optional[str] = None,
        year_from: Optional[str] = None,
        year_to: Optional[str] = None,
        extension: Optional[str] = None,
        author: Optional[str] = None,
        limit: int = 100,
    ) -> List[Book]:
        """
        Browse books with optional filters.

        Args:
            query: Text to search in title
            language: Filter by language
            year_from: Filter by minimum year
            year_to: Filter by maximum year
            extension: Filter by file extension
            author: Filter by author name
            limit: Maximum number of results (default: 100)

        Returns:
            List[Book]: List of matching books

        Raises:
            ValueError: If limit is invalid
        """
        if limit <= 0:
            raise ValueError("Limit must be greater than 0")

        if limit > 1000:
            raise ValueError("Limit cannot exceed 1000")

        return self.book_repo.search(
            query=query,
            language=language,
            year_from=year_from,
            year_to=year_to,
            extension=extension,
            author=author,
            limit=limit,
        )

    def save_book(
        self,
        book_id: str,
        notes: Optional[str] = None,
        tags: Optional[str] = None,
        priority: int = 0,
    ) -> None:
        """
        Save a book to saved books.

        Args:
            book_id: Book ID to save
            notes: Optional user notes
            tags: Optional user tags
            priority: Priority level (default: 0)

        Raises:
            ValueError: If book not found or priority invalid
        """
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise ValueError(
                f"Cannot save book {book_id}: book not found. "
                "Use 'db browse' to see available books."
            )

        if priority < 0:
            raise ValueError("Priority cannot be negative")

        conn = self.book_repo.db_manager.get_connection()
        conn.execute(
            """
            INSERT OR REPLACE INTO saved_books
                (book_id, notes, tags, priority)
            VALUES (?, ?, ?, ?)
            """,
            (book_id, notes, tags, priority),
        )
        conn.commit()

    def unsave_book(self, book_id: str) -> bool:
        """
        Remove a book from saved books.

        Args:
            book_id: Book ID to unsave

        Returns:
            bool: True if book was unsaved, False if not saved
        """
        conn = self.book_repo.db_manager.get_connection()
        cursor = conn.execute("DELETE FROM saved_books WHERE book_id = ?", (book_id,))
        conn.commit()
        return cursor.rowcount > 0

    def get_saved_books(self) -> List[SavedBook]:
        """
        Get all saved books with metadata.

        Returns:
            List[SavedBook]: List of saved books with details
        """
        conn = self.book_repo.db_manager.get_connection()
        cursor = conn.execute(
            """
            SELECT b.id, b.hash, b.title, b.year, b.publisher,
                   b.language, b.extension, b.size, b.filesize,
                   b.cover_url, b.description, b.created_at,
                   b.updated_at, sb.notes, sb.tags, sb.priority,
                   sb.saved_at
            FROM saved_books sb
            JOIN books b ON sb.book_id = b.id
            ORDER BY sb.priority DESC, sb.saved_at DESC
            """
        )

        saved_books: List[SavedBook] = []
        for row in cursor.fetchall():
            book = self._row_to_book(row)
            authors = self.author_repo.get_authors_for_book(book.id)

            saved_books.append(
                SavedBook(
                    book=book,
                    authors=authors,
                    notes=row["notes"],
                    tags=row["tags"],
                    priority=row["priority"],
                    saved_at=row["saved_at"],
                )
            )

        return saved_books

    def _row_to_book(self, row: Any) -> Book:
        """
        Convert database row to Book instance.

        Args:
            row: Database row from books table

        Returns:
            Book: Book instance created from row data
        """
        from datetime import datetime

        return Book(
            id=row["id"],
            hash=row["hash"],
            title=row["title"],
            year=row["year"],
            publisher=row["publisher"],
            language=row["language"],
            extension=row["extension"],
            size=row["size"],
            filesize=row["filesize"],
            cover_url=row["cover_url"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
