"""
Data models for Z-Library downloader database.

This module defines the data structures for managing book metadata, authors,
reading lists, downloads, and search history, including serialization.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, Any


@dataclass
class Book:
    """
    Represents a book from Z-Library.

    Attributes:
        id: Z-Library book ID (primary key)
        hash: Book hash identifier
        title: Book title
        year: Publication year
        publisher: Publisher name
        language: Book language
        extension: File format extension (e.g., pdf, epub)
        size: Human-readable file size (e.g., "10.5 MB")
        filesize: File size in bytes
        cover_url: URL to book cover image
        description: Book description
        created_at: Timestamp when record was created
        updated_at: Timestamp when record was last updated
    """

    id: str
    hash: str
    title: str
    year: Optional[str] = None
    publisher: Optional[str] = None
    language: Optional[str] = None
    extension: Optional[str] = None
    size: Optional[str] = None
    filesize: Optional[int] = None
    cover_url: Optional[str] = None
    description: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the book to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the book
        """
        return {
            "id": self.id,
            "hash": self.hash,
            "title": self.title,
            "year": self.year,
            "publisher": self.publisher,
            "language": self.language,
            "extension": self.extension,
            "size": self.size,
            "filesize": self.filesize,
            "cover_url": self.cover_url,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Book":
        """
        Deserialize a book from a dictionary.

        Args:
            data: Dictionary containing book data

        Returns:
            Book: New Book instance
        """
        created_at = datetime.now()
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])

        updated_at = datetime.now()
        if data.get("updated_at"):
            updated_at = datetime.fromisoformat(data["updated_at"])

        return cls(
            id=data["id"],
            hash=data["hash"],
            title=data["title"],
            year=data.get("year"),
            publisher=data.get("publisher"),
            language=data.get("language"),
            extension=data.get("extension"),
            size=data.get("size"),
            filesize=data.get("filesize"),
            cover_url=data.get("cover_url"),
            description=data.get("description"),
            created_at=created_at,
            updated_at=updated_at,
        )


@dataclass
class Author:
    """
    Represents a book author.

    Attributes:
        id: Database-generated author ID
        name: Author name
    """

    name: str
    id: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the author to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the author
        """
        return {
            "id": self.id,
            "name": self.name,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Author":
        """
        Deserialize an author from a dictionary.

        Args:
            data: Dictionary containing author data

        Returns:
            Author: New Author instance
        """
        return cls(
            name=data["name"],
            id=data.get("id"),
        )


@dataclass
class ReadingList:
    """
    Represents a user-created reading list.

    Attributes:
        name: List name (unique)
        description: List description
        id: Database-generated list ID
        created_at: Timestamp when list was created
    """

    name: str
    description: str = ""
    id: Optional[int] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the reading list to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the reading list
        """
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ReadingList":
        """
        Deserialize a reading list from a dictionary.

        Args:
            data: Dictionary containing reading list data

        Returns:
            ReadingList: New ReadingList instance
        """
        created_at = datetime.now()
        if data.get("created_at"):
            created_at = datetime.fromisoformat(data["created_at"])

        return cls(
            name=data["name"],
            description=data.get("description", ""),
            id=data.get("id"),
            created_at=created_at,
        )


@dataclass
class Download:
    """
    Represents a book download record.

    Attributes:
        book_id: ID of the downloaded book
        filename: Name of the downloaded file
        file_path: Path where file was saved
        id: Database-generated download ID
        credential_id: ID of credential used for download
        downloaded_at: Timestamp when download occurred
        file_size: Size of downloaded file in bytes
        status: Download status (completed, failed, etc.)
        error_msg: Error message if download failed
    """

    book_id: str
    filename: str
    file_path: str
    id: Optional[int] = None
    credential_id: Optional[int] = None
    downloaded_at: datetime = field(default_factory=datetime.now)
    file_size: Optional[int] = None
    status: str = "completed"
    error_msg: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the download to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the download
        """
        return {
            "id": self.id,
            "book_id": self.book_id,
            "credential_id": self.credential_id,
            "filename": self.filename,
            "file_path": self.file_path,
            "downloaded_at": self.downloaded_at.isoformat(),
            "file_size": self.file_size,
            "status": self.status,
            "error_msg": self.error_msg,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Download":
        """
        Deserialize a download from a dictionary.

        Args:
            data: Dictionary containing download data

        Returns:
            Download: New Download instance
        """
        downloaded_at = datetime.now()
        if data.get("downloaded_at"):
            downloaded_at = datetime.fromisoformat(data["downloaded_at"])

        return cls(
            book_id=data["book_id"],
            filename=data["filename"],
            file_path=data["file_path"],
            id=data.get("id"),
            credential_id=data.get("credential_id"),
            downloaded_at=downloaded_at,
            file_size=data.get("file_size"),
            status=data.get("status", "completed"),
            error_msg=data.get("error_msg"),
        )


@dataclass
class SearchHistory:
    """
    Represents a search history record.

    Attributes:
        search_query: The search query text
        search_filters: JSON string of search filters
        id: Database-generated history ID
        searched_at: Timestamp when search was performed
    """

    search_query: str
    search_filters: str = ""
    id: Optional[int] = None
    searched_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the search history to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the search history
        """
        return {
            "id": self.id,
            "search_query": self.search_query,
            "search_filters": self.search_filters,
            "searched_at": self.searched_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchHistory":
        """
        Deserialize a search history from a dictionary.

        Args:
            data: Dictionary containing search history data

        Returns:
            SearchHistory: New SearchHistory instance
        """
        searched_at = datetime.now()
        if data.get("searched_at"):
            searched_at = datetime.fromisoformat(data["searched_at"])

        return cls(
            search_query=data["search_query"],
            search_filters=data.get("search_filters", ""),
            id=data.get("id"),
            searched_at=searched_at,
        )
