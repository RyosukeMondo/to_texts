"""Repository for reading list database operations.

This module provides the ReadingListRepository class for CRUD operations on reading lists,
using parameterized queries for security and supporting ordered book lists.
"""

import sqlite3
from datetime import datetime
from typing import List, Optional

from .db_manager import DatabaseManager
from .models import ReadingList, Book


class ReadingListRepository:
    """
    Repository for reading list database operations.

    Provides CRUD operations for reading lists and manages book membership
    with position tracking for ordered lists. All operations use parameterized
    queries to prevent SQL injection.

    Attributes:
        db_manager: DatabaseManager instance for database access
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize ReadingListRepository.

        Args:
            db_manager: DatabaseManager instance for database access
        """
        self.db_manager = db_manager

    def create_list(self, name: str, description: str = "") -> ReadingList:
        """
        Create a new reading list.

        Args:
            name: List name (must be unique)
            description: Optional list description

        Returns:
            ReadingList: The created reading list instance

        Raises:
            sqlite3.IntegrityError: If list with same name exists
        """
        conn = self.db_manager.get_connection()
        created_at = datetime.now()

        cursor = conn.execute(
            """
            INSERT INTO reading_lists (name, description, created_at)
            VALUES (?, ?, ?)
            """,
            (name, description, created_at.isoformat()),
        )
        conn.commit()

        return ReadingList(
            id=cursor.lastrowid,
            name=name,
            description=description,
            created_at=created_at,
        )

    def get_list_by_name(self, name: str) -> Optional[ReadingList]:
        """
        Get a reading list by name.

        Args:
            name: List name to search for

        Returns:
            Optional[ReadingList]: List if found, None otherwise
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            """
            SELECT id, name, description, created_at
            FROM reading_lists WHERE name = ?
            """,
            (name,),
        )
        row = cursor.fetchone()
        return self._row_to_list(row) if row else None

    def get_list_by_id(self, list_id: int) -> Optional[ReadingList]:
        """
        Get a reading list by ID.

        Args:
            list_id: List ID to retrieve

        Returns:
            Optional[ReadingList]: List if found, None otherwise
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            """
            SELECT id, name, description, created_at
            FROM reading_lists WHERE id = ?
            """,
            (list_id,),
        )
        row = cursor.fetchone()
        return self._row_to_list(row) if row else None

    def list_all(self) -> List[ReadingList]:
        """
        Get all reading lists.

        Returns:
            List[ReadingList]: All reading lists ordered by name
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            """
            SELECT id, name, description, created_at
            FROM reading_lists ORDER BY name
            """
        )
        return [self._row_to_list(row) for row in cursor.fetchall()]

    def add_book(self, list_id: int, book_id: str) -> None:
        """
        Add a book to a reading list.

        Automatically assigns next position in list. If book already exists,
        operation is silently ignored.

        Args:
            list_id: ID of the list to add book to
            book_id: ID of the book to add
        """
        conn = self.db_manager.get_connection()

        # Get next position
        cursor = conn.execute(
            "SELECT COALESCE(MAX(position), -1) + 1 FROM list_books WHERE list_id = ?",
            (list_id,),
        )
        next_position = cursor.fetchone()[0]

        # Add book with next position
        conn.execute(
            """
            INSERT OR IGNORE INTO list_books (list_id, book_id, position)
            VALUES (?, ?, ?)
            """,
            (list_id, book_id, next_position),
        )
        conn.commit()

    def remove_book(self, list_id: int, book_id: str) -> bool:
        """
        Remove a book from a reading list.

        Args:
            list_id: ID of the list to remove book from
            book_id: ID of the book to remove

        Returns:
            bool: True if book was removed, False if not in list
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            "DELETE FROM list_books WHERE list_id = ? AND book_id = ?",
            (list_id, book_id),
        )
        conn.commit()
        return cursor.rowcount > 0

    def get_books(self, list_id: int) -> List[Book]:
        """
        Get all books in a reading list.

        Books are returned in position order.

        Args:
            list_id: ID of the list to retrieve books from

        Returns:
            List[Book]: Books in the list ordered by position
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            """
            SELECT b.id, b.hash, b.title, b.year, b.publisher,
                   b.language, b.extension, b.size, b.filesize,
                   b.cover_url, b.description, b.created_at, b.updated_at
            FROM books b
            JOIN list_books lb ON b.id = lb.book_id
            WHERE lb.list_id = ?
            ORDER BY lb.position
            """,
            (list_id,),
        )
        return [self._row_to_book(row) for row in cursor.fetchall()]

    def delete_list(self, list_id: int) -> bool:
        """
        Delete a reading list.

        Also removes all book associations (CASCADE).

        Args:
            list_id: ID of list to delete

        Returns:
            bool: True if list was deleted, False if not found
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute("DELETE FROM reading_lists WHERE id = ?", (list_id,))
        conn.commit()
        return cursor.rowcount > 0

    def _row_to_list(self, row: sqlite3.Row) -> ReadingList:
        """
        Convert database row to ReadingList instance.

        Args:
            row: Database row from reading_lists table

        Returns:
            ReadingList: ReadingList instance created from row data
        """
        return ReadingList(
            id=row["id"],
            name=row["name"],
            description=row["description"] or "",
            created_at=datetime.fromisoformat(row["created_at"]),
        )

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
