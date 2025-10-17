"""Repository for author database operations.

This module provides the AuthorRepository class for managing authors and
book-author relationships, using parameterized queries for security.
"""

from typing import List

from .db_manager import DatabaseManager
from .models import Author


class AuthorRepository:
    """
    Repository for author database operations.

    Provides operations for managing authors and book-author relationships.
    All operations use parameterized queries to prevent SQL injection.

    Attributes:
        db_manager: DatabaseManager instance for database access
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize AuthorRepository.

        Args:
            db_manager: DatabaseManager instance for database access
        """
        self.db_manager = db_manager

    def get_or_create(self, name: str) -> Author:
        """
        Get existing author or create new one.

        Handles race conditions with INSERT OR IGNORE.

        Args:
            name: Author name

        Returns:
            Author: Existing or newly created author

        Raises:
            ValueError: If name is empty
        """
        if not name or not name.strip():
            raise ValueError("Author name cannot be empty")

        name = name.strip()
        conn = self.db_manager.get_connection()

        conn.execute("INSERT OR IGNORE INTO authors (name) VALUES (?)", (name,))
        conn.commit()

        cursor = conn.execute("SELECT id, name FROM authors WHERE name = ?", (name,))
        row = cursor.fetchone()

        if not row:
            raise RuntimeError(f"Failed to get or create author: {name}")

        return Author(id=row["id"], name=row["name"])

    def link_book_author(self, book_id: str, author_id: int, order: int = 0) -> None:
        """
        Create book-author relationship.

        Args:
            book_id: Book ID
            author_id: Author ID
            order: Author order for multi-author books (default: 0)

        Raises:
            sqlite3.IntegrityError: If relationship already exists
        """
        conn = self.db_manager.get_connection()
        conn.execute(
            """
            INSERT INTO book_authors (book_id, author_id, author_order)
            VALUES (?, ?, ?)
            """,
            (book_id, author_id, order),
        )
        conn.commit()

    def get_authors_for_book(self, book_id: str) -> List[Author]:
        """
        Get all authors for a book, ordered by author_order.

        Args:
            book_id: Book ID

        Returns:
            List[Author]: List of authors for the book
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            """
            SELECT a.id, a.name
            FROM authors a
            JOIN book_authors ba ON a.id = ba.author_id
            WHERE ba.book_id = ?
            ORDER BY ba.author_order
            """,
            (book_id,),
        )
        return [Author(id=row["id"], name=row["name"]) for row in cursor.fetchall()]

    def get_books_for_author(self, author_id: int) -> List[str]:
        """
        Get all book IDs for an author.

        Args:
            author_id: Author ID

        Returns:
            List[str]: List of book IDs
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            """
            SELECT book_id
            FROM book_authors
            WHERE author_id = ?
            ORDER BY author_order
            """,
            (author_id,),
        )
        return [row["book_id"] for row in cursor.fetchall()]
