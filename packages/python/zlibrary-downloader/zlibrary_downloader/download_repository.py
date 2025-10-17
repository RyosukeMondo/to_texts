"""Repository for download tracking operations.

This module provides the DownloadRepository class for recording and querying
download history using parameterized queries and the Download dataclass.
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Any, List, Optional

from .db_manager import DatabaseManager
from .models import Download


class DownloadRepository:
    """
    Repository for download tracking operations.

    Provides methods to record downloads and query download history
    with filtering capabilities. All operations use parameterized queries.

    Attributes:
        db_manager: DatabaseManager instance for database access
    """

    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize DownloadRepository.

        Args:
            db_manager: DatabaseManager instance for database access
        """
        self.db_manager = db_manager

    def record_download(
        self,
        book_id: str,
        filename: str,
        file_path: str,
        credential_id: Optional[int] = None,
        file_size: Optional[int] = None,
        status: str = "completed",
        error_msg: Optional[str] = None,
    ) -> Download:
        """
        Record a book download.

        Args:
            book_id: ID of the downloaded book
            filename: Name of the downloaded file
            file_path: Path where file was saved
            credential_id: ID of credential used (optional)
            file_size: Size of file in bytes (optional)
            status: Download status (default: "completed")
            error_msg: Error message if failed (optional)

        Returns:
            Download: The recorded download instance with ID
        """
        download = Download(
            book_id=book_id,
            filename=filename,
            file_path=file_path,
            credential_id=credential_id,
            file_size=file_size,
            status=status,
            error_msg=error_msg,
        )

        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            """
            INSERT INTO downloads (
                book_id, credential_id, filename, file_path,
                downloaded_at, file_size, status, error_msg
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                download.book_id,
                download.credential_id,
                download.filename,
                download.file_path,
                download.downloaded_at.isoformat(),
                download.file_size,
                download.status,
                download.error_msg,
            ),
        )
        conn.commit()
        download.id = cursor.lastrowid
        return download

    def get_history(
        self,
        limit: int = 100,
        recent_days: Optional[int] = None,
        credential_id: Optional[int] = None,
    ) -> List[Download]:
        """
        Get download history with optional filters.

        Args:
            limit: Maximum number of results (default: 100)
            recent_days: Filter downloads from last N days
            credential_id: Filter by credential ID

        Returns:
            List[Download]: List of downloads, newest first
        """
        where_clauses: List[str] = []
        params: List[Any] = []

        if recent_days is not None:
            cutoff = datetime.now() - timedelta(days=recent_days)
            where_clauses.append("downloaded_at >= ?")
            params.append(cutoff.isoformat())

        if credential_id is not None:
            where_clauses.append("credential_id = ?")
            params.append(credential_id)

        sql = """
            SELECT id, book_id, credential_id, filename, file_path,
                   downloaded_at, file_size, status, error_msg
            FROM downloads
        """

        if where_clauses:
            sql += " WHERE " + " AND ".join(where_clauses)

        sql += " ORDER BY downloaded_at DESC LIMIT ?"
        params.append(limit)

        conn = self.db_manager.get_connection()
        cursor = conn.execute(sql, params)
        return [self._row_to_download(row) for row in cursor.fetchall()]

    def get_for_book(self, book_id: str) -> List[Download]:
        """
        Get all downloads for a specific book.

        Args:
            book_id: Book ID to query

        Returns:
            List[Download]: Downloads for the book, newest first
        """
        conn = self.db_manager.get_connection()
        cursor = conn.execute(
            """
            SELECT id, book_id, credential_id, filename, file_path,
                   downloaded_at, file_size, status, error_msg
            FROM downloads
            WHERE book_id = ?
            ORDER BY downloaded_at DESC
            """,
            (book_id,),
        )
        return [self._row_to_download(row) for row in cursor.fetchall()]

    def _row_to_download(self, row: sqlite3.Row) -> Download:
        """
        Convert database row to Download instance.

        Args:
            row: Database row from downloads table

        Returns:
            Download: Download instance created from row data
        """
        return Download(
            id=row["id"],
            book_id=row["book_id"],
            credential_id=row["credential_id"],
            filename=row["filename"],
            file_path=row["file_path"],
            downloaded_at=datetime.fromisoformat(row["downloaded_at"]),
            file_size=row["file_size"],
            status=row["status"],
            error_msg=row["error_msg"],
        )
