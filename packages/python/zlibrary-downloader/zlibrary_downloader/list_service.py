"""Service layer for reading list operations.

This module provides the ListService class that orchestrates reading list
operations across ListRepository and BookRepository, handling business logic
and providing user-friendly error messages.
"""

import sqlite3
from typing import List

from .list_repository import ReadingListRepository
from .book_repository import BookRepository
from .models import ReadingList, Book


class ListService:
    """
    Service layer for reading list operations.

    Orchestrates list operations across repositories and provides
    business logic with clear error handling.

    Attributes:
        list_repo: ReadingListRepository instance
        book_repo: BookRepository instance
    """

    def __init__(
        self, list_repo: ReadingListRepository, book_repo: BookRepository
    ) -> None:
        """
        Initialize ListService.

        Args:
            list_repo: ReadingListRepository instance
            book_repo: BookRepository instance
        """
        self.list_repo = list_repo
        self.book_repo = book_repo

    def create_list(self, name: str, description: str = "") -> ReadingList:
        """
        Create a new reading list.

        Args:
            name: List name (must be unique)
            description: Optional list description

        Returns:
            ReadingList: The created reading list

        Raises:
            ValueError: If name is empty or list exists
        """
        if not name or not name.strip():
            raise ValueError("List name cannot be empty")

        # Check if list already exists
        existing = self.list_repo.get_list_by_name(name)
        if existing:
            raise ValueError(
                f"List '{name}' already exists. "
                "Choose a different name or use 'db list-show' to view it."
            )

        try:
            return self.list_repo.create_list(name, description)
        except sqlite3.IntegrityError as e:
            raise ValueError(f"Failed to create list '{name}': {e}")

    def add_book_to_list(self, list_name: str, book_id: str) -> None:
        """
        Add a book to a reading list.

        Args:
            list_name: Name of the list to add book to
            book_id: ID of the book to add

        Raises:
            ValueError: If list or book not found
        """
        # Verify list exists
        reading_list = self.list_repo.get_list_by_name(list_name)
        if not reading_list:
            raise ValueError(
                f"List '{list_name}' not found. "
                "Use 'db lists' to see available lists."
            )

        # Verify book exists
        book = self.book_repo.get_by_id(book_id)
        if not book:
            raise ValueError(
                f"Book {book_id} not found. " "Use 'db browse' to see available books."
            )

        if reading_list.id is None:
            raise ValueError(f"Internal error: list '{list_name}' has no ID")

        self.list_repo.add_book(reading_list.id, book_id)

    def remove_book_from_list(self, list_name: str, book_id: str) -> bool:
        """
        Remove a book from a reading list.

        Args:
            list_name: Name of the list to remove book from
            book_id: ID of the book to remove

        Returns:
            bool: True if book was removed, False if not in list

        Raises:
            ValueError: If list not found
        """
        reading_list = self.list_repo.get_list_by_name(list_name)
        if not reading_list:
            raise ValueError(
                f"List '{list_name}' not found. "
                "Use 'db lists' to see available lists."
            )

        if reading_list.id is None:
            raise ValueError(f"Internal error: list '{list_name}' has no ID")

        return self.list_repo.remove_book(reading_list.id, book_id)

    def delete_list(self, list_name: str) -> bool:
        """
        Delete a reading list.

        Args:
            list_name: Name of the list to delete

        Returns:
            bool: True if list was deleted, False if not found
        """
        reading_list = self.list_repo.get_list_by_name(list_name)
        if not reading_list:
            return False

        if reading_list.id is None:
            return False

        return self.list_repo.delete_list(reading_list.id)

    def get_all_lists(self) -> List[ReadingList]:
        """
        Get all reading lists.

        Returns:
            List[ReadingList]: All reading lists ordered by name
        """
        return self.list_repo.list_all()

    def get_list_with_books(self, list_name: str) -> tuple[ReadingList, List[Book]]:
        """
        Get a reading list with all its books.

        Args:
            list_name: Name of the list to retrieve

        Returns:
            tuple: (ReadingList, List[Book]) - list and its books

        Raises:
            ValueError: If list not found
        """
        reading_list = self.list_repo.get_list_by_name(list_name)
        if not reading_list:
            raise ValueError(
                f"List '{list_name}' not found. "
                "Use 'db lists' to see available lists."
            )

        if reading_list.id is None:
            raise ValueError(f"Internal error: list '{list_name}' has no ID")

        books = self.list_repo.get_books(reading_list.id)
        return reading_list, books
