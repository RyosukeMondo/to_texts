"""Repository for book database operations.

This module provides the BookRepository class for CRUD operations on books,
using parameterized queries for security and the Book dataclass for type safety.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional, Any

from .db_manager import DatabaseManager
from .models import Book


class BookRepository:
    """
    Repository for book database operations.

    Provides CRUD operations for books with search and filtering capabilities.
    All operations use parameterized queries to prevent SQL injection.

    Attributes:
        db_manager: DatabaseManager instance for database access
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize BookRepository.

        Args:
            db_manager: DatabaseManager instance for database access
        """
        self.db_manager = db_manager

    def create(self, book: Book) -> Book:
        """
        Create a new book record.

        Args:
            book: Book instance to create

        Returns:
            Book: The created book instance

        Raises:
            sqlite3.IntegrityError: If book with same ID already exists
        """
        conn = self.db_manager.get_connection()
        conn.execute(
            """
            INSERT INTO books (
                id, hash, title, year, publisher, language,
                extension, size, filesize, cover_url, description,
                created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                book.id,
                book.hash,
                book.title,
                book.year,
                book.publisher,
                book.language,
                book.extension,
                book.size,
                book.filesize,
                book.cover_url,
                book.description,
                book.created_at.isoformat(),
                book.updated_at.isoformat(),
            ),
        )
        conn.commit()
        return book

    def get_by_id(self, book_id: str) -> Optional[Book]:
        """
        Get a book by its ID.

        Args:
            book_id: Book ID to retrieve

        Returns:
            Optional[Book]: Book instance if found, None otherwise
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            """
            SELECT id, hash, title, year, publisher, language,
                   extension, size, filesize, cover_url, description,
                   created_at, updated_at
            FROM books WHERE id = ?
            """,
            (book_id,),
        )
        row = cursor.fetchone()
        return self._row_to_book(row) if row else None

    def search(
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
        Search for books with optional filters.

        Args:
            query: Text to search in title (LIKE pattern)
            language: Filter by language
            year_from: Filter by minimum year
            year_to: Filter by maximum year
            extension: Filter by file extension
            author: Filter by author name
            limit: Maximum number of results

        Returns:
            List[Book]: List of matching books
        """
        where_clauses, params = self._build_search_where(
            query, language, year_from, year_to, extension, author
        )

        sql = """
            SELECT DISTINCT b.id, b.hash, b.title, b.year, b.publisher,
                   b.language, b.extension, b.size, b.filesize, b.cover_url,
                   b.description, b.created_at, b.updated_at
            FROM books b
        """

        if author:
            sql += """
                LEFT JOIN book_authors ba ON b.id = ba.book_id
                LEFT JOIN authors a ON ba.author_id = a.id
            """

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " ORDER BY b.title LIMIT ?"
        params.append(limit)

        conn = self.db_manager.get_connection()
        cursor = conn.execute(sql, params)
        return [self._row_to_book(row) for row in cursor.fetchall()]

    def _build_search_where(
        self,
        query: Optional[str],
        language: Optional[str],
        year_from: Optional[str],
        year_to: Optional[str],
        extension: Optional[str],
        author: Optional[str],
    ) -> tuple[List[str], List[Any]]:
        """
        Build WHERE clause for search query.

        Args:
            query: Text search query
            language: Language filter
            year_from: Minimum year filter
            year_to: Maximum year filter
            extension: Extension filter
            author: Author name filter

        Returns:
            tuple: (list of WHERE clauses, list of parameters)
        """
        clauses: List[str] = []
        params: List[Any] = []

        if query:
            clauses.append("b.title LIKE ?")
            params.append(f"%{query}%")

        if language:
            clauses.append("b.language = ?")
            params.append(language)

        if year_from:
            clauses.append("b.year >= ?")
            params.append(year_from)

        if year_to:
            clauses.append("b.year <= ?")
            params.append(year_to)

        if extension:
            clauses.append("b.extension = ?")
            params.append(extension)

        if author:
            clauses.append("a.name LIKE ?")
            params.append(f"%{author}%")

        return clauses, params

    def update(self, book: Book) -> Book:
        """
        Update an existing book record.

        Args:
            book: Book instance with updated data

        Returns:
            Book: The updated book instance
        """
        book.updated_at = datetime.now()
        conn = self.db_manager.get_connection()
        conn.execute(
            """
            UPDATE books SET
                hash = ?, title = ?, year = ?, publisher = ?,
                language = ?, extension = ?, size = ?, filesize = ?,
                cover_url = ?, description = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                book.hash,
                book.title,
                book.year,
                book.publisher,
                book.language,
                book.extension,
                book.size,
                book.filesize,
                book.cover_url,
                book.description,
                book.updated_at.isoformat(),
                book.id,
            ),
        )
        conn.commit()
        return book

    def upsert(self, book: Book) -> Book:
        """
        Insert book or update if it already exists.

        Args:
            book: Book instance to insert or update

        Returns:
            Book: The inserted or updated book instance
        """
        existing = self.get_by_id(book.id)
        if existing:
            return self.update(book)
        else:
            return self.create(book)

    def delete(self, book_id: str) -> bool:
        """
        Delete a book by ID.

        Args:
            book_id: ID of book to delete

        Returns:
            bool: True if book was deleted, False if not found
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute("DELETE FROM books WHERE id = ?", (book_id,))
        conn.commit()
        return cursor.rowcount > 0

    def count(
        self,
        language: Optional[str] = None,
        year_from: Optional[str] = None,
        year_to: Optional[str] = None,
        extension: Optional[str] = None,
    ) -> int:
        """
        Count books matching optional filters.

        Args:
            language: Filter by language
            year_from: Filter by minimum year
            year_to: Filter by maximum year
            extension: Filter by file extension

        Returns:
            int: Number of matching books
        """
        where_clauses, params = self._build_count_where(language, year_from, year_to, extension)

        sql = "SELECT COUNT(*) FROM books"
        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        conn = self.db_manager.get_connection()
        cursor = conn.execute(sql, params)
        result = cursor.fetchone()
        return int(result[0]) if result else 0

    def _build_count_where(
        self,
        language: Optional[str],
        year_from: Optional[str],
        year_to: Optional[str],
        extension: Optional[str],
    ) -> tuple[List[str], List[Any]]:
        """
        Build WHERE clause for count query.

        Args:
            language: Language filter
            year_from: Minimum year filter
            year_to: Maximum year filter
            extension: Extension filter

        Returns:
            tuple: (list of WHERE clauses, list of parameters)
        """
        clauses: List[str] = []
        params: List[Any] = []

        if language:
            clauses.append("language = ?")
            params.append(language)

        if year_from:
            clauses.append("year >= ?")
            params.append(year_from)

        if year_to:
            clauses.append("year <= ?")
            params.append(year_to)

        if extension:
            clauses.append("extension = ?")
            params.append(extension)

        return clauses, params

    def _row_to_book(self, row: sqlite3.Row) -> Book:
        """
        Convert database row to Book instance.

        Args:
            row: Database row from books table

        Returns:
            Book: Book instance created from row data
        """
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
