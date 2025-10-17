"""
Unit tests for the SearchHistoryRepository class.

Tests cover recording searches, querying history, and SQL injection
prevention using in-memory SQLite.
"""

from pathlib import Path

import pytest

from zlibrary_downloader.db_manager import DatabaseManager
from zlibrary_downloader.search_history_repository import SearchHistoryRepository


@pytest.fixture
def db_manager() -> DatabaseManager:
    """Create in-memory database manager with initialized schema."""
    manager = DatabaseManager(db_path=Path(":memory:"))
    manager.initialize_schema()
    return manager


@pytest.fixture
def search_repo(db_manager: DatabaseManager) -> SearchHistoryRepository:
    """Create SearchHistoryRepository with in-memory database."""
    return SearchHistoryRepository(db_manager)


class TestRecordSearch:
    """Tests for recording searches."""

    def test_record_search_basic(self, search_repo: SearchHistoryRepository) -> None:
        """Test recording a basic search query."""
        result = search_repo.record_search(search_query="python programming")

        assert result.id is not None
        assert result.search_query == "python programming"
        assert result.search_filters == ""

    def test_record_search_with_filters(self, search_repo: SearchHistoryRepository) -> None:
        """Test recording search with JSON filters."""
        filters_json = '{"language": "English", "year": "2023"}'
        result = search_repo.record_search(search_query="python", search_filters=filters_json)

        assert result.search_query == "python"
        assert result.search_filters == filters_json

    def test_record_search_sql_injection_prevention(
        self, search_repo: SearchHistoryRepository
    ) -> None:
        """Test that recording search prevents SQL injection."""
        injection = "'; DROP TABLE search_history; --"
        result = search_repo.record_search(search_query=injection)

        assert result.id is not None
        assert result.search_query == injection

        # Verify table still exists by querying
        history = search_repo.get_history()
        assert len(history) == 1


class TestGetHistory:
    """Tests for retrieving search history."""

    def test_get_history_empty(self, search_repo: SearchHistoryRepository) -> None:
        """Test getting history when no searches exist."""
        result = search_repo.get_history()
        assert len(result) == 0

    def test_get_history_all_searches(self, search_repo: SearchHistoryRepository) -> None:
        """Test getting all search history."""
        search_repo.record_search(search_query="query1")
        search_repo.record_search(search_query="query2")
        search_repo.record_search(search_query="query3")

        result = search_repo.get_history()
        assert len(result) == 3

    def test_get_history_ordered_newest_first(self, search_repo: SearchHistoryRepository) -> None:
        """Test that history is returned newest first."""
        search_repo.record_search(search_query="old query")
        search_repo.record_search(search_query="middle query")
        search_repo.record_search(search_query="new query")

        result = search_repo.get_history()
        assert result[0].search_query == "new query"
        assert result[1].search_query == "middle query"
        assert result[2].search_query == "old query"

    def test_get_history_with_limit(self, search_repo: SearchHistoryRepository) -> None:
        """Test limiting number of history results."""
        for i in range(10):
            search_repo.record_search(search_query=f"query {i}")

        result = search_repo.get_history(limit=5)
        assert len(result) == 5

    def test_get_history_default_limit(self, search_repo: SearchHistoryRepository) -> None:
        """Test that default limit is 100."""
        # Create more than 100 searches
        for i in range(150):
            search_repo.record_search(search_query=f"query {i}")

        result = search_repo.get_history()
        assert len(result) == 100


class TestRowConversion:
    """Tests for database row conversion."""

    def test_row_to_search_preserves_all_fields(self, search_repo: SearchHistoryRepository) -> None:
        """Test that row conversion preserves all search history fields."""
        filters_json = '{"language": "English"}'
        original = search_repo.record_search(search_query="test query", search_filters=filters_json)

        retrieved = search_repo.get_history()[0]

        assert retrieved.id == original.id
        assert retrieved.search_query == original.search_query
        assert retrieved.search_filters == original.search_filters
        # Compare timestamps within reasonable delta
        delta = abs((retrieved.searched_at - original.searched_at).total_seconds())
        assert delta < 1  # Less than 1 second difference


class TestFiltersHandling:
    """Tests for handling various filter formats."""

    def test_empty_filters(self, search_repo: SearchHistoryRepository) -> None:
        """Test handling empty filters string."""
        search = search_repo.record_search(search_query="test", search_filters="")
        assert search.search_filters == ""

    def test_complex_json_filters(self, search_repo: SearchHistoryRepository) -> None:
        """Test handling complex JSON filters."""
        complex_filters = (
            '{"language": "English", "year_from": "2020", ' '"year_to": "2023", "extension": "pdf"}'
        )
        search_repo.record_search(search_query="advanced search", search_filters=complex_filters)

        retrieved = search_repo.get_history()[0]
        assert retrieved.search_filters == complex_filters
