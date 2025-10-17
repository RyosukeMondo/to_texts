"""
Unit tests for the ListService class.

Tests cover business logic using mocked repository dependencies,
ensuring service layer validation, error handling, and proper
orchestration of repository operations.
"""

from unittest.mock import Mock

import pytest

from zlibrary_downloader.list_service import ListService
from zlibrary_downloader.list_repository import ReadingListRepository
from zlibrary_downloader.book_repository import BookRepository
from zlibrary_downloader.models import ReadingList, Book


@pytest.fixture
def mock_list_repo() -> Mock:
    """Create mock ReadingListRepository."""
    return Mock(spec=ReadingListRepository)


@pytest.fixture
def mock_book_repo() -> Mock:
    """Create mock BookRepository."""
    return Mock(spec=BookRepository)


@pytest.fixture
def list_service(mock_list_repo: Mock, mock_book_repo: Mock) -> ListService:
    """Create ListService with mocked dependencies."""
    return ListService(mock_list_repo, mock_book_repo)


@pytest.fixture
def sample_list() -> ReadingList:
    """Create a sample reading list for testing."""
    return ReadingList(id=1, name="My Reading List", description="Test list")


@pytest.fixture
def sample_book() -> Book:
    """Create a sample book for testing."""
    return Book(id="12345", hash="abc123", title="Test Book")


class TestCreateList:
    """Tests for creating reading lists."""

    def test_create_list_success(
        self, list_service: ListService, mock_list_repo: Mock, sample_list: ReadingList
    ) -> None:
        """Test successfully creating a reading list."""
        mock_list_repo.get_list_by_name.return_value = None
        mock_list_repo.create_list.return_value = sample_list

        result = list_service.create_list("My Reading List", "Test list")

        assert result == sample_list
        mock_list_repo.get_list_by_name.assert_called_once_with("My Reading List")
        mock_list_repo.create_list.assert_called_once_with("My Reading List", "Test list")

    def test_create_list_empty_name(self, list_service: ListService) -> None:
        """Test creating list with empty name raises error."""
        with pytest.raises(ValueError) as exc_info:
            list_service.create_list("")

        assert "name cannot be empty" in str(exc_info.value)

    def test_create_list_duplicate_name(
        self, list_service: ListService, mock_list_repo: Mock, sample_list: ReadingList
    ) -> None:
        """Test creating list with duplicate name raises error."""
        mock_list_repo.get_list_by_name.return_value = sample_list

        with pytest.raises(ValueError) as exc_info:
            list_service.create_list("My Reading List")

        assert "already exists" in str(exc_info.value)


class TestAddBookToList:
    """Tests for adding books to lists."""

    def test_add_book_success(
        self,
        list_service: ListService,
        mock_list_repo: Mock,
        mock_book_repo: Mock,
        sample_list: ReadingList,
        sample_book: Book,
    ) -> None:
        """Test successfully adding a book to a list."""
        mock_list_repo.get_list_by_name.return_value = sample_list
        mock_book_repo.get_by_id.return_value = sample_book

        list_service.add_book_to_list("My Reading List", "12345")

        mock_list_repo.get_list_by_name.assert_called_once_with("My Reading List")
        mock_book_repo.get_by_id.assert_called_once_with("12345")
        mock_list_repo.add_book.assert_called_once_with(1, "12345")

    def test_add_book_list_not_found(
        self, list_service: ListService, mock_list_repo: Mock
    ) -> None:
        """Test adding book to nonexistent list raises error."""
        mock_list_repo.get_list_by_name.return_value = None

        with pytest.raises(ValueError) as exc_info:
            list_service.add_book_to_list("Nonexistent List", "12345")

        assert "not found" in str(exc_info.value)

    def test_add_book_book_not_found(
        self,
        list_service: ListService,
        mock_list_repo: Mock,
        mock_book_repo: Mock,
        sample_list: ReadingList,
    ) -> None:
        """Test adding nonexistent book raises error."""
        mock_list_repo.get_list_by_name.return_value = sample_list
        mock_book_repo.get_by_id.return_value = None

        with pytest.raises(ValueError) as exc_info:
            list_service.add_book_to_list("My Reading List", "nonexistent")

        assert "Book" in str(exc_info.value)
        assert "not found" in str(exc_info.value)


class TestRemoveBookFromList:
    """Tests for removing books from lists."""

    def test_remove_book_success(
        self,
        list_service: ListService,
        mock_list_repo: Mock,
        sample_list: ReadingList,
    ) -> None:
        """Test successfully removing a book from a list."""
        mock_list_repo.get_list_by_name.return_value = sample_list
        mock_list_repo.remove_book.return_value = True

        result = list_service.remove_book_from_list("My Reading List", "12345")

        assert result is True
        mock_list_repo.remove_book.assert_called_once_with(1, "12345")

    def test_remove_book_list_not_found(
        self, list_service: ListService, mock_list_repo: Mock
    ) -> None:
        """Test removing book from nonexistent list raises error."""
        mock_list_repo.get_list_by_name.return_value = None

        with pytest.raises(ValueError) as exc_info:
            list_service.remove_book_from_list("Nonexistent List", "12345")

        assert "not found" in str(exc_info.value)


class TestDeleteList:
    """Tests for deleting lists."""

    def test_delete_list_success(
        self,
        list_service: ListService,
        mock_list_repo: Mock,
        sample_list: ReadingList,
    ) -> None:
        """Test successfully deleting a list."""
        mock_list_repo.get_list_by_name.return_value = sample_list
        mock_list_repo.delete_list.return_value = True

        result = list_service.delete_list("My Reading List")

        assert result is True
        mock_list_repo.delete_list.assert_called_once_with(1)

    def test_delete_list_not_found(
        self, list_service: ListService, mock_list_repo: Mock
    ) -> None:
        """Test deleting nonexistent list returns False."""
        mock_list_repo.get_list_by_name.return_value = None

        result = list_service.delete_list("Nonexistent List")

        assert result is False


class TestGetAllLists:
    """Tests for getting all lists."""

    def test_get_all_lists_empty(
        self, list_service: ListService, mock_list_repo: Mock
    ) -> None:
        """Test getting all lists when none exist."""
        mock_list_repo.list_all.return_value = []

        result = list_service.get_all_lists()

        assert len(result) == 0

    def test_get_all_lists_with_data(
        self, list_service: ListService, mock_list_repo: Mock, sample_list: ReadingList
    ) -> None:
        """Test getting all lists with data."""
        mock_list_repo.list_all.return_value = [sample_list]

        result = list_service.get_all_lists()

        assert len(result) == 1
        assert result[0] == sample_list


class TestGetListWithBooks:
    """Tests for getting list with books."""

    def test_get_list_with_books_success(
        self,
        list_service: ListService,
        mock_list_repo: Mock,
        sample_list: ReadingList,
        sample_book: Book,
    ) -> None:
        """Test successfully getting list with books."""
        mock_list_repo.get_list_by_name.return_value = sample_list
        mock_list_repo.get_books.return_value = [sample_book]

        reading_list, books = list_service.get_list_with_books("My Reading List")

        assert reading_list == sample_list
        assert len(books) == 1
        assert books[0] == sample_book

    def test_get_list_with_books_not_found(
        self, list_service: ListService, mock_list_repo: Mock
    ) -> None:
        """Test getting nonexistent list raises error."""
        mock_list_repo.get_list_by_name.return_value = None

        with pytest.raises(ValueError) as exc_info:
            list_service.get_list_with_books("Nonexistent List")

        assert "not found" in str(exc_info.value)
