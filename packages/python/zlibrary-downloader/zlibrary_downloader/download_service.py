"""Service layer for download tracking operations.

This module provides the DownloadService class that orchestrates download
tracking operations using DownloadRepository, handling business logic
and providing user-friendly error messages.
"""

from typing import List, Optional

from .download_repository import DownloadRepository
from .models import Download


class DownloadService:
    """
    Service layer for download tracking operations.

    Orchestrates download tracking operations and provides
    business logic with clear error handling.

    Attributes:
        download_repo: DownloadRepository instance
    """

    def __init__(self, download_repo: DownloadRepository) -> None:
        """
        Initialize DownloadService.

        Args:
            download_repo: DownloadRepository instance
        """
        self.download_repo = download_repo

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
            Download: The recorded download instance

        Raises:
            ValueError: If book_id, filename, or file_path is empty
        """
        if not book_id or not book_id.strip():
            raise ValueError("Book ID cannot be empty")

        if not filename or not filename.strip():
            raise ValueError("Filename cannot be empty")

        if not file_path or not file_path.strip():
            raise ValueError("File path cannot be empty")

        return self.download_repo.record_download(
            book_id=book_id,
            filename=filename,
            file_path=file_path,
            credential_id=credential_id,
            file_size=file_size,
            status=status,
            error_msg=error_msg,
        )

    def get_download_history(
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

        Raises:
            ValueError: If limit is invalid or recent_days is negative
        """
        if limit <= 0:
            raise ValueError("Limit must be greater than 0")

        if limit > 1000:
            raise ValueError("Limit cannot exceed 1000")

        if recent_days is not None and recent_days < 0:
            raise ValueError("Recent days cannot be negative")

        return self.download_repo.get_history(
            limit=limit, recent_days=recent_days, credential_id=credential_id
        )

    def check_if_downloaded(self, book_id: str) -> bool:
        """
        Check if a book has been downloaded.

        Args:
            book_id: Book ID to check

        Returns:
            bool: True if book has been downloaded, False otherwise

        Raises:
            ValueError: If book_id is empty
        """
        if not book_id or not book_id.strip():
            raise ValueError("Book ID cannot be empty")

        downloads = self.download_repo.get_for_book(book_id)
        return len(downloads) > 0
