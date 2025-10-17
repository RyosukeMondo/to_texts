"""
Unit tests for the DownloadService class.

Tests cover business logic using mocked repository dependencies,
ensuring service layer validation, error handling, and proper
orchestration of repository operations.
"""

from unittest.mock import Mock

import pytest

from zlibrary_downloader.download_service import DownloadService
from zlibrary_downloader.download_repository import DownloadRepository
from zlibrary_downloader.models import Download


@pytest.fixture
def mock_download_repo() -> Mock:
    """Create mock DownloadRepository."""
    return Mock(spec=DownloadRepository)


@pytest.fixture
def download_service(mock_download_repo: Mock) -> DownloadService:
    """Create DownloadService with mocked dependencies."""
    return DownloadService(mock_download_repo)


@pytest.fixture
def sample_download() -> Download:
    """Create a sample download for testing."""
    return Download(
        id=1,
        book_id="12345",
        filename="test_book.pdf",
        file_path="/downloads/test_book.pdf",
        file_size=1048576,
        status="completed",
    )


class TestRecordDownload:
    """Tests for recording downloads."""

    def test_record_download_success(
        self,
        download_service: DownloadService,
        mock_download_repo: Mock,
        sample_download: Download,
    ) -> None:
        """Test successfully recording a download."""
        mock_download_repo.record_download.return_value = sample_download

        result = download_service.record_download(
            book_id="12345",
            filename="test_book.pdf",
            file_path="/downloads/test_book.pdf",
            credential_id=1,
            file_size=1048576,
        )

        assert result == sample_download
        mock_download_repo.record_download.assert_called_once_with(
            book_id="12345",
            filename="test_book.pdf",
            file_path="/downloads/test_book.pdf",
            credential_id=1,
            file_size=1048576,
            status="completed",
            error_msg=None,
        )

    def test_record_download_empty_book_id(
        self, download_service: DownloadService
    ) -> None:
        """Test recording download with empty book_id raises error."""
        with pytest.raises(ValueError) as exc_info:
            download_service.record_download(
                book_id="", filename="test.pdf", file_path="/downloads/test.pdf"
            )

        assert "Book ID cannot be empty" in str(exc_info.value)

    def test_record_download_empty_filename(
        self, download_service: DownloadService
    ) -> None:
        """Test recording download with empty filename raises error."""
        with pytest.raises(ValueError) as exc_info:
            download_service.record_download(
                book_id="12345", filename="", file_path="/downloads/test.pdf"
            )

        assert "Filename cannot be empty" in str(exc_info.value)

    def test_record_download_empty_path(
        self, download_service: DownloadService
    ) -> None:
        """Test recording download with empty path raises error."""
        with pytest.raises(ValueError) as exc_info:
            download_service.record_download(
                book_id="12345", filename="test.pdf", file_path=""
            )

        assert "File path cannot be empty" in str(exc_info.value)


class TestGetDownloadHistory:
    """Tests for getting download history."""

    def test_get_history_default_params(
        self,
        download_service: DownloadService,
        mock_download_repo: Mock,
        sample_download: Download,
    ) -> None:
        """Test getting history with default parameters."""
        mock_download_repo.get_history.return_value = [sample_download]

        result = download_service.get_download_history()

        assert len(result) == 1
        assert result[0] == sample_download
        mock_download_repo.get_history.assert_called_once_with(
            limit=100, recent_days=None, credential_id=None
        )

    def test_get_history_with_filters(
        self,
        download_service: DownloadService,
        mock_download_repo: Mock,
        sample_download: Download,
    ) -> None:
        """Test getting history with filters."""
        mock_download_repo.get_history.return_value = [sample_download]

        result = download_service.get_download_history(
            limit=50, recent_days=7, credential_id=1
        )

        assert len(result) == 1
        mock_download_repo.get_history.assert_called_once_with(
            limit=50, recent_days=7, credential_id=1
        )

    def test_get_history_invalid_limit_zero(
        self, download_service: DownloadService
    ) -> None:
        """Test getting history with zero limit raises error."""
        with pytest.raises(ValueError) as exc_info:
            download_service.get_download_history(limit=0)

        assert "greater than 0" in str(exc_info.value)

    def test_get_history_invalid_limit_negative(
        self, download_service: DownloadService
    ) -> None:
        """Test getting history with negative limit raises error."""
        with pytest.raises(ValueError) as exc_info:
            download_service.get_download_history(limit=-10)

        assert "greater than 0" in str(exc_info.value)

    def test_get_history_limit_too_large(
        self, download_service: DownloadService
    ) -> None:
        """Test getting history with limit over 1000 raises error."""
        with pytest.raises(ValueError) as exc_info:
            download_service.get_download_history(limit=2000)

        assert "cannot exceed 1000" in str(exc_info.value)

    def test_get_history_negative_recent_days(
        self, download_service: DownloadService
    ) -> None:
        """Test getting history with negative recent_days raises error."""
        with pytest.raises(ValueError) as exc_info:
            download_service.get_download_history(recent_days=-5)

        assert "cannot be negative" in str(exc_info.value)


class TestCheckIfDownloaded:
    """Tests for checking if book was downloaded."""

    def test_check_if_downloaded_true(
        self,
        download_service: DownloadService,
        mock_download_repo: Mock,
        sample_download: Download,
    ) -> None:
        """Test checking if book was downloaded returns True."""
        mock_download_repo.get_for_book.return_value = [sample_download]

        result = download_service.check_if_downloaded("12345")

        assert result is True
        mock_download_repo.get_for_book.assert_called_once_with("12345")

    def test_check_if_downloaded_false(
        self, download_service: DownloadService, mock_download_repo: Mock
    ) -> None:
        """Test checking if book not downloaded returns False."""
        mock_download_repo.get_for_book.return_value = []

        result = download_service.check_if_downloaded("12345")

        assert result is False

    def test_check_if_downloaded_empty_book_id(
        self, download_service: DownloadService
    ) -> None:
        """Test checking with empty book_id raises error."""
        with pytest.raises(ValueError) as exc_info:
            download_service.check_if_downloaded("")

        assert "Book ID cannot be empty" in str(exc_info.value)
