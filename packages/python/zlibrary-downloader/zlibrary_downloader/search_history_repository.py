"""Repository for search history operations.

This module provides the SearchHistoryRepository class for recording and
querying search history using parameterized queries and SearchHistory dataclass.
"""

import sqlite3
from datetime import datetime
from typing import List

from .db_manager import DatabaseManager
from .models import SearchHistory


class SearchHistoryRepository:
    """
    Repository for search history operations.

    Provides methods to record searches and query search history.
    All operations use parameterized queries.

    Attributes:
        db_manager: DatabaseManager instance for database access
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize SearchHistoryRepository.

        Args:
            db_manager: DatabaseManager instance for database access
        """
        self.db_manager = db_manager

    def record_search(self, search_query: str, search_filters: str = "") -> SearchHistory:
        """
        Record a search query with optional filters.

        Args:
            search_query: The search query text
            search_filters: JSON string of search filters (optional)

        Returns:
            SearchHistory: The recorded search history with ID
        """
        search = SearchHistory(search_query=search_query, search_filters=search_filters)

        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO search_history (
                search_query, search_filters, found_at
            ) VALUES (?, ?, ?)
            """,
            (
                search.search_query,
                search.search_filters,
                search.searched_at.isoformat(),
            ),
        )
        conn.commit()
        search.id = cursor.lastrowid
        return search

    def get_history(self, limit: int = 100) -> List[SearchHistory]:
        """
        Get recent search history.

        Args:
            limit: Maximum number of results (default: 100)

        Returns:
            List[SearchHistory]: Recent searches, newest first
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            """
            SELECT id, search_query, search_filters, found_at
            FROM search_history
            ORDER BY found_at DESC
            LIMIT ?
            """,
            (limit,),
        )
        return [self._row_to_search(row) for row in cursor.fetchall()]

    def _row_to_search(self, row: sqlite3.Row) -> SearchHistory:
        """
        Convert database row to SearchHistory instance.

        Args:
            row: Database row from search_history table

        Returns:
            SearchHistory: SearchHistory instance from row data
        """
        return SearchHistory(
            id=row["id"],
            search_query=row["search_query"],
            search_filters=row["search_filters"],
            searched_at=datetime.fromisoformat(row["found_at"]),
        )
