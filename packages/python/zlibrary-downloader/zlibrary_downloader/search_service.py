"""Service for search operations with database integration.

This module provides the SearchService class that orchestrates search operations
with optional database storage, extracting and linking authors to books.
"""

import json
import re
from typing import List, Dict, Any

from .book_repository import BookRepository
from .author_repository import AuthorRepository
from .search_history_repository import SearchHistoryRepository
from .models import Book
from .client import Zlibrary


class SearchService:
    """
    Service for search operations with database storage.

    Orchestrates search with Z-Library API and stores results in database,
    extracting authors and creating proper relationships.

    Attributes:
        book_repo: BookRepository instance for book operations
        author_repo: AuthorRepository instance for author operations
        search_repo: SearchHistoryRepository for recording searches
    """

    def __init__(
        self,
        book_repo: BookRepository,
        author_repo: AuthorRepository,
        search_repo: SearchHistoryRepository,
    ):
        """
        Initialize SearchService.

        Args:
            book_repo: BookRepository instance
            author_repo: AuthorRepository instance
            search_repo: SearchHistoryRepository instance
        """
        self.book_repo = book_repo
        self.author_repo = author_repo
        self.search_repo = search_repo

    def search_and_store(self, client: Zlibrary, query: str, **filters: Any) -> List[Book]:
        """
        Search Z-Library and store results in database.

        Performs search via client, transforms results to Book objects,
        extracts and links authors, and records search history.

        Args:
            client: Zlibrary client instance
            query: Search query string
            **filters: Additional search filters (yearFrom, yearTo, etc.)

        Returns:
            List[Book]: List of stored books from search results
        """
        response = client.search(message=query, **filters)

        if not response.get("success", False):
            return []

        books_data = response.get("books", [])
        stored_books: List[Book] = []

        for book_data in books_data:
            try:
                book = self._store_book(book_data)
                stored_books.append(book)
            except Exception as e:
                print(f"Error storing book {book_data.get('id')}: {e}")
                continue

        filters_json = json.dumps(filters) if filters else ""
        self.search_repo.record_search(query, filters_json)

        return stored_books

    def _store_book(self, book_data: Dict[str, Any]) -> Book:
        """
        Store a book and its authors from API response.

        Extracts book data, creates/updates book record,
        extracts authors, and creates relationships.

        Args:
            book_data: Book data dictionary from API

        Returns:
            Book: Stored book instance

        Raises:
            ValueError: If required book data is missing
        """
        if not book_data.get("id") or not book_data.get("hash"):
            raise ValueError("Missing required book ID or hash")

        book = self._book_from_api_data(book_data)
        book = self.book_repo.upsert(book)

        author_str = book_data.get("author", "")
        if author_str:
            authors = self._extract_authors(author_str)
            self._link_authors_to_book(book.id, authors)

        return book

    def _book_from_api_data(self, data: Dict[str, Any]) -> Book:
        """
        Convert API book data to Book dataclass.

        Args:
            data: Book data from Z-Library API

        Returns:
            Book: Book instance from API data
        """
        return Book(
            id=str(data["id"]),
            hash=data["hash"],
            title=data.get("title", "Unknown"),
            year=data.get("year"),
            publisher=data.get("publisher"),
            language=data.get("language"),
            extension=data.get("extension"),
            size=data.get("size"),
            filesize=data.get("filesize"),
            cover_url=data.get("cover"),
            description=data.get("description"),
        )

    def _extract_authors(self, author_str: str) -> List[str]:
        """
        Extract author names from author string.

        Handles various formats:
        - "Author1, Author2" (comma separated)
        - "Author1 and Author2" (and separated)
        - "Author1; Author2" (semicolon separated)
        - "Author1 & Author2" (ampersand separated)

        Args:
            author_str: Author string from API

        Returns:
            List[str]: List of extracted author names
        """
        if not author_str or not author_str.strip():
            return []

        author_str = author_str.strip()
        authors: List[str] = []

        if ";" in author_str:
            authors = [a.strip() for a in author_str.split(";")]
        elif " and " in author_str.lower():
            authors = [a.strip() for a in re.split(r"\s+and\s+", author_str, flags=re.IGNORECASE)]
        elif " & " in author_str:
            authors = [a.strip() for a in author_str.split(" & ")]
        elif "," in author_str:
            authors = [a.strip() for a in author_str.split(",")]
        else:
            authors = [author_str]

        return [a for a in authors if a]

    def _link_authors_to_book(self, book_id: str, author_names: List[str]) -> None:
        """
        Link authors to book by name.

        Creates author records if needed and links to book.

        Args:
            book_id: Book ID to link authors to
            author_names: List of author names to link
        """
        for i, name in enumerate(author_names):
            try:
                author = self.author_repo.get_or_create(name)
                self.author_repo.link_book_author(book_id, author.id, order=i)  # type: ignore
            except Exception as e:
                print(f"Error linking author {name}: {e}")
                continue
