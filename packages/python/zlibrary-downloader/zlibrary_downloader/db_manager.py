"""Database connection manager for zlibrary-downloader.

This module provides DatabaseManager class for managing SQLite connections,
schema initialization, and transaction support following the CredentialManager pattern.
"""

import os
import sqlite3
from pathlib import Path
from typing import Any, Callable, Optional, TypeVar, Union

from . import schema

T = TypeVar("T")


class DatabaseManager:
    """
    Manages database connection lifecycle and operations.

    Handles SQLite connection to ~/.zlibrary/books.db (configurable via env var),
    provides schema initialization, transaction support, and proper cleanup.

    Attributes:
        db_path: Path to the SQLite database file or ":memory:" string
        connection: Active SQLite connection (None until initialized)
    """

    DEFAULT_DB_PATH = Path.home() / ".zlibrary" / "books.db"

    def __init__(self, db_path: Optional[Union[Path, str]] = None):
        """
        Initialize DatabaseManager.

        Args:
            db_path: Path to database file, str for :memory:, or None for default
        """
        env_db_path = os.getenv("ZLIBRARY_DB_PATH")
        if env_db_path:
            self.db_path: Union[Path, str] = Path(env_db_path)
        elif db_path:
            # Handle str for :memory: and Path for file paths
            self.db_path = db_path
        else:
            self.db_path = self.DEFAULT_DB_PATH

        self.connection: Optional[sqlite3.Connection] = None

    def _ensure_directory_exists(self) -> None:
        """Ensure database directory exists with proper permissions."""
        # Skip for in-memory databases
        if isinstance(self.db_path, str):
            return
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

    def _set_file_permissions(self) -> None:
        """Set database file permissions to 600 on Unix systems."""
        # Skip for in-memory databases
        if isinstance(self.db_path, str):
            return
        if os.name != "nt" and self.db_path.exists():
            os.chmod(self.db_path, 0o600)

    def get_connection(self) -> sqlite3.Connection:
        """
        Get or create database connection.

        Returns:
            sqlite3.Connection: Active database connection

        Raises:
            RuntimeError: If connection cannot be established
        """
        if self.connection is None:
            self._ensure_directory_exists()

            try:
                self.connection = sqlite3.connect(str(self.db_path))
                self.connection.row_factory = sqlite3.Row
                # Enable foreign key constraints
                self.connection.execute("PRAGMA foreign_keys = ON")
                # Enable WAL mode for better concurrency
                self.connection.execute("PRAGMA journal_mode = WAL")

                self._set_file_permissions()

            except sqlite3.Error as e:
                raise RuntimeError(f"Failed to connect to database: {e}")

        return self.connection

    def initialize_schema(self) -> None:
        """
        Initialize database schema using schema.py.

        Creates all tables and indexes if they don't exist.
        Records schema version in schema_version table.

        Raises:
            RuntimeError: If schema initialization fails
        """
        try:
            conn = self.get_connection()

            # Create all tables
            for table_sql in schema.ALL_TABLES:
                conn.execute(table_sql)

            # Create all indexes
            for index_sql in schema.ALL_INDEXES:
                conn.execute(index_sql)

            # Record schema version
            conn.execute(
                "INSERT OR IGNORE INTO schema_version (version) VALUES (?)",
                (schema.SCHEMA_VERSION,),
            )

            conn.commit()

        except sqlite3.Error as e:
            if self.connection:
                self.connection.rollback()
            raise RuntimeError(f"Failed to initialize schema: {e}")

    def execute_transaction(self, func: Callable[[sqlite3.Connection], T]) -> T:
        """
        Execute a function within a transaction.

        Automatically commits on success or rolls back on error.

        Args:
            func: Function that takes connection and returns a value

        Returns:
            T: Return value from func

        Raises:
            Exception: Any exception from func (after rollback)
        """
        conn = self.get_connection()

        try:
            result = func(conn)
            conn.commit()
            return result
        except Exception:
            conn.rollback()
            raise

    def close(self) -> None:
        """Close database connection if open."""
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self) -> "DatabaseManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit with automatic cleanup."""
        self.close()
