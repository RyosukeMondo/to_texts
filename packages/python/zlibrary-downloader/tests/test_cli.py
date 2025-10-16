"""
Unit tests for zlibrary_downloader.cli module.

Tests cover the command-line interface functionality, including:
- Credential loading with CredentialManager and ClientPool
- Display of credential status
- Command-line argument parsing
- Interactive mode
- Command-line mode operations (search, download, info)
- Output formatting
- Error handling and user feedback
- Backward compatibility with .env format

Target: >80% code coverage
"""

from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from zlibrary_downloader import cli
from zlibrary_downloader.credential import Credential, CredentialStatus


class TestCredentialLoading:
    """Test suite for credential loading with new CredentialManager integration."""

    def test_load_credentials_with_toml(self, tmp_path: Path) -> None:
        """Test loading credentials from TOML file."""
        toml_content = """
[[credentials]]
identifier = "test1"
email = "test1@example.com"
password = "password1"
enabled = true
"""
        toml_file = tmp_path / "zlibrary_credentials.toml"
        toml_file.write_text(toml_content)

        with patch("zlibrary_downloader.cli.CredentialManager") as mock_cm_class:
            mock_cm = Mock()
            mock_cm_class.return_value = mock_cm

            with patch("zlibrary_downloader.cli.ZlibraryClientPool") as mock_pool_class:
                mock_pool = Mock()
                mock_pool_class.return_value = mock_pool

                # Change to tmp directory
                import os

                old_cwd = os.getcwd()
                try:
                    os.chdir(tmp_path)
                    credential_manager, client_pool = cli.load_credentials()

                    # Verify CredentialManager was initialized and load_credentials called
                    mock_cm_class.assert_called_once()
                    mock_cm.load_credentials.assert_called_once()

                    # Verify ClientPool was created with CredentialManager
                    mock_pool_class.assert_called_once_with(mock_cm)

                    assert credential_manager == mock_cm
                    assert client_pool == mock_pool
                finally:
                    os.chdir(old_cwd)

    def test_load_credentials_with_env(self, tmp_path: Path) -> None:
        """Test loading credentials from .env file (backward compatibility)."""
        env_content = """
ZLIBRARY_EMAIL=test@example.com
ZLIBRARY_PASSWORD=testpassword
"""
        env_file = tmp_path / ".env"
        env_file.write_text(env_content)

        with patch("zlibrary_downloader.cli.CredentialManager") as mock_cm_class:
            mock_cm = Mock()
            mock_cm_class.return_value = mock_cm

            with patch("zlibrary_downloader.cli.ZlibraryClientPool") as mock_pool_class:
                mock_pool = Mock()
                mock_pool_class.return_value = mock_pool

                import os

                old_cwd = os.getcwd()
                try:
                    os.chdir(tmp_path)
                    credential_manager, client_pool = cli.load_credentials()

                    mock_cm.load_credentials.assert_called_once()
                    assert credential_manager == mock_cm
                    assert client_pool == mock_pool
                finally:
                    os.chdir(old_cwd)

    def test_load_credentials_no_config_found(self, tmp_path: Path) -> None:
        """Test error handling when no credential configuration is found."""
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with patch("zlibrary_downloader.cli.CredentialManager") as mock_cm_class:
                mock_cm = Mock()
                mock_cm.load_credentials.side_effect = FileNotFoundError(
                    "No credential configuration found"
                )
                mock_cm_class.return_value = mock_cm

                with pytest.raises(SystemExit):
                    cli.load_credentials()
        finally:
            os.chdir(old_cwd)

    def test_load_credentials_invalid_config(self, tmp_path: Path) -> None:
        """Test error handling for invalid credential configuration."""
        toml_content = """
invalid toml content here
"""
        toml_file = tmp_path / "zlibrary_credentials.toml"
        toml_file.write_text(toml_content)

        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)

            with patch("zlibrary_downloader.cli.CredentialManager") as mock_cm_class:
                mock_cm = Mock()
                mock_cm.load_credentials.side_effect = ValueError("Invalid TOML")
                mock_cm_class.return_value = mock_cm

                with pytest.raises(SystemExit):
                    cli.load_credentials()
        finally:
            os.chdir(old_cwd)


class TestInitializeZlibrary:
    """Test suite for Z-Library client initialization."""

    def test_initialize_zlibrary_success(self) -> None:
        """Test successful client initialization."""
        mock_pool = Mock()
        mock_client = Mock()
        mock_pool.get_current_client.return_value = mock_client

        client = cli.initialize_zlibrary(mock_pool)

        mock_pool.get_current_client.assert_called_once()
        assert client == mock_client

    def test_initialize_zlibrary_failure(self) -> None:
        """Test client initialization failure."""
        mock_pool = Mock()
        mock_pool.get_current_client.return_value = None

        with pytest.raises(SystemExit):
            cli.initialize_zlibrary(mock_pool)


class TestDisplayCredentialStatus:
    """Test suite for credential status display."""

    def test_display_credential_status_with_single_credential(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Test displaying status with single credential."""
        mock_cm = Mock()
        credential = Credential(
            identifier="test1",
            email="test@example.com",
            password="pass",
            status=CredentialStatus.VALID,
            downloads_left=5,
        )
        mock_cm.credentials = [credential]
        mock_cm.get_available.return_value = [credential]
        mock_cm.get_current.return_value = credential

        cli.display_credential_status(mock_cm)

        captured = capsys.readouterr()
        assert "Total credentials: 1" in captured.out
        assert "Available credentials: 1" in captured.out
        assert "Current credential: test1" in captured.out
        assert "Email/password" in captured.out
        assert "Downloads remaining: 5" in captured.out

    def test_display_credential_status_with_remix_auth(self, capsys: pytest.CaptureFixture) -> None:
        """Test displaying status with remix authentication."""
        mock_cm = Mock()
        credential = Credential(
            identifier="test1",
            remix_userid="userid123",
            remix_userkey="userkey456",
            status=CredentialStatus.VALID,
            downloads_left=10,
        )
        mock_cm.credentials = [credential]
        mock_cm.get_available.return_value = [credential]
        mock_cm.get_current.return_value = credential

        cli.display_credential_status(mock_cm)

        captured = capsys.readouterr()
        assert "Remix tokens" in captured.out

    def test_display_credential_status_with_multiple_credentials(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Test displaying status with multiple credentials."""
        mock_cm = Mock()
        cred1 = Credential(
            identifier="test1",
            email="test1@example.com",
            password="pass1",
            status=CredentialStatus.VALID,
        )
        cred2 = Credential(
            identifier="test2",
            email="test2@example.com",
            password="pass2",
            status=CredentialStatus.EXHAUSTED,
        )
        mock_cm.credentials = [cred1, cred2]
        mock_cm.get_available.return_value = [cred1]
        mock_cm.get_current.return_value = cred1

        cli.display_credential_status(mock_cm)

        captured = capsys.readouterr()
        assert "Total credentials: 2" in captured.out
        assert "Available credentials: 1" in captured.out

    def test_display_credential_status_no_download_limit(
        self, capsys: pytest.CaptureFixture
    ) -> None:
        """Test displaying status when download limit is not available."""
        mock_cm = Mock()
        credential = Credential(
            identifier="test1",
            email="test@example.com",
            password="pass",
            status=CredentialStatus.VALID,
            downloads_left=None,
        )
        mock_cm.credentials = [credential]
        mock_cm.get_available.return_value = [credential]
        mock_cm.get_current.return_value = credential

        cli.display_credential_status(mock_cm)

        captured = capsys.readouterr()
        assert "Downloads remaining" not in captured.out


class TestArgumentParser:
    """Test suite for argument parsing."""

    def test_create_argument_parser(self) -> None:
        """Test argument parser creation."""
        parser = cli.create_argument_parser()
        assert parser is not None
        assert "multiple credentials" in parser.description.lower()

    def test_parser_help_text_mentions_toml(self) -> None:
        """Test that help text mentions TOML configuration."""
        parser = cli.create_argument_parser()
        assert "zlibrary_credentials.toml" in parser.epilog
        assert "TOML" in parser.epilog or "toml" in parser.epilog


class TestAutomaticRotation:
    """Test suite for automatic credential rotation after operations."""

    def test_search_books_rotates_after_success(self) -> None:
        """Test that search_books rotates to next credential after successful search."""
        mock_client = Mock()
        mock_client.search.return_value = {"books": [{"title": "Test Book"}]}

        mock_pool = Mock()
        mock_cm = Mock()
        mock_pool.credential_manager = mock_cm

        # Mock credentials
        cred1 = Credential(identifier="cred1", email="test1@example.com", password="pass1")
        cred2 = Credential(identifier="cred2", email="test2@example.com", password="pass2")
        mock_cm.get_current.return_value = cred1
        mock_cm.rotate.return_value = cred2

        result = cli.search_books(mock_client, "test query", mock_pool)

        # Verify search was called
        mock_client.search.assert_called_once()
        assert result is not None

        # Verify rotation occurred
        mock_cm.rotate.assert_called_once()

    def test_search_books_without_pool_no_rotation(self) -> None:
        """Test that search_books works without client_pool (no rotation)."""
        mock_client = Mock()
        mock_client.search.return_value = {"books": [{"title": "Test Book"}]}

        result = cli.search_books(mock_client, "test query", client_pool=None)

        mock_client.search.assert_called_once()
        assert result is not None

    def test_search_books_rotation_all_exhausted(self, capsys: pytest.CaptureFixture) -> None:
        """Test search_books handles case when all credentials are exhausted."""
        mock_client = Mock()
        mock_client.search.return_value = {"books": [{"title": "Test Book"}]}

        mock_pool = Mock()
        mock_cm = Mock()
        mock_pool.credential_manager = mock_cm

        cred1 = Credential(identifier="cred1", email="test1@example.com", password="pass1")
        mock_cm.get_current.return_value = cred1
        mock_cm.rotate.return_value = None  # All exhausted

        result = cli.search_books(mock_client, "test query", mock_pool)

        assert result is not None
        mock_cm.rotate.assert_called_once()

    def test_download_book_updates_limits_and_rotates(self, tmp_path: Path) -> None:
        """Test that download_book updates download limits and rotates credential."""
        mock_client = Mock()
        mock_client.downloadBook.return_value = ("test.pdf", b"fake pdf content")

        mock_pool = Mock()
        mock_cm = Mock()
        mock_pool.credential_manager = mock_cm

        cred1 = Credential(
            identifier="cred1", email="test1@example.com", password="pass1", downloads_left=5
        )
        cred2 = Credential(identifier="cred2", email="test2@example.com", password="pass2")

        mock_cm.get_current.return_value = cred1
        mock_cm.update_downloads_left.return_value = (True, None)
        mock_cm.rotate.return_value = cred2

        book = {"title": "Test Book", "id": "123"}
        result = cli.download_book(mock_client, book, mock_pool, str(tmp_path))

        # Verify download occurred
        mock_client.downloadBook.assert_called_once_with(book)
        assert result is not None
        assert (tmp_path / "test.pdf").exists()

        # Verify download limits updated
        mock_cm.update_downloads_left.assert_called_once_with(cred1)

        # Verify rotation occurred
        mock_cm.rotate.assert_called_once()

    def test_download_book_handles_update_failure(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test download_book handles failure to update download limits gracefully."""
        mock_client = Mock()
        mock_client.downloadBook.return_value = ("test.pdf", b"fake pdf content")

        mock_pool = Mock()
        mock_cm = Mock()
        mock_pool.credential_manager = mock_cm

        cred1 = Credential(identifier="cred1", email="test1@example.com", password="pass1")
        cred2 = Credential(identifier="cred2", email="test2@example.com", password="pass2")

        mock_cm.get_current.return_value = cred1
        mock_cm.update_downloads_left.return_value = (False, "API error")
        mock_cm.rotate.return_value = cred2

        book = {"title": "Test Book"}
        result = cli.download_book(mock_client, book, mock_pool, str(tmp_path))

        # Download should still succeed even if limit update fails
        assert result is not None
        mock_cm.rotate.assert_called_once()

    def test_download_book_exhaustion_warning(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test download_book displays warning when all credentials exhausted."""
        mock_client = Mock()
        mock_client.downloadBook.return_value = ("test.pdf", b"fake pdf content")

        mock_pool = Mock()
        mock_cm = Mock()
        mock_pool.credential_manager = mock_cm

        cred1 = Credential(identifier="cred1", email="test1@example.com", password="pass1")
        mock_cm.get_current.return_value = cred1
        mock_cm.update_downloads_left.return_value = (True, None)
        mock_cm.rotate.return_value = None  # All exhausted

        book = {"title": "Test Book"}
        result = cli.download_book(mock_client, book, mock_pool, str(tmp_path))

        assert result is not None
        captured = capsys.readouterr()
        assert "All credentials exhausted" in captured.out

    def test_download_book_without_pool_no_rotation(self, tmp_path: Path) -> None:
        """Test download_book works without client_pool (no rotation)."""
        mock_client = Mock()
        mock_client.downloadBook.return_value = ("test.pdf", b"fake pdf content")

        book = {"title": "Test Book"}
        result = cli.download_book(mock_client, book, client_pool=None, download_dir=str(tmp_path))

        mock_client.downloadBook.assert_called_once_with(book)
        assert result is not None
        assert (tmp_path / "test.pdf").exists()


class TestErrorHandlingAndRetry:
    """Test suite for error handling and retry logic."""

    def test_search_books_retry_with_next_credential(self, capsys: pytest.CaptureFixture) -> None:
        """Test search_books retries with next credential on failure."""
        # First client fails, second succeeds
        mock_client1 = Mock()
        mock_client1.search.side_effect = Exception("Network error")

        mock_client2 = Mock()
        mock_client2.search.return_value = {"books": [{"title": "Test Book"}]}

        mock_pool = Mock()
        mock_cm = Mock()
        mock_pool.credential_manager = mock_cm
        mock_pool.get_current_client.return_value = mock_client2

        cred1 = Credential(identifier="cred1", email="test1@example.com", password="pass1")
        cred2 = Credential(identifier="cred2", email="test2@example.com", password="pass2")

        mock_cm.get_current.side_effect = [cred1, cred1, cred2]
        mock_cm.get_available.return_value = [cred1, cred2]
        mock_cm.rotate.return_value = cred2

        results = cli.search_books(mock_client1, "test query", mock_pool)

        # Should succeed with second credential
        assert results is not None
        assert "books" in results

        # Verify rotation was called after failure
        mock_cm.rotate.assert_called()

        captured = capsys.readouterr()
        assert "failed" in captured.out.lower() or "trying next credential" in captured.out.lower()

    def test_search_books_all_credentials_fail(self, capsys: pytest.CaptureFixture) -> None:
        """Test search_books handles all credentials failing."""
        mock_client = Mock()
        mock_client.search.side_effect = Exception("Network error")

        mock_pool = Mock()
        mock_cm = Mock()
        mock_pool.credential_manager = mock_cm
        mock_pool.get_current_client.return_value = mock_client

        cred1 = Credential(identifier="cred1", email="test1@example.com", password="pass1")
        mock_cm.get_current.return_value = cred1
        mock_cm.get_available.return_value = [cred1]  # Only one credential

        results = cli.search_books(mock_client, "test query", mock_pool)

        # Should return None after all retries
        assert results is None

        captured = capsys.readouterr()
        assert "error" in captured.out.lower()

    def test_download_book_retry_with_next_credential(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test download_book retries with next credential on failure."""
        # First client fails, second succeeds
        mock_client1 = Mock()
        mock_client1.downloadBook.side_effect = Exception("Download failed")

        mock_client2 = Mock()
        mock_client2.downloadBook.return_value = ("test.pdf", b"fake pdf content")

        mock_pool = Mock()
        mock_cm = Mock()
        mock_pool.credential_manager = mock_cm
        mock_pool.get_current_client.return_value = mock_client2

        cred1 = Credential(
            identifier="cred1", email="test1@example.com", password="pass1", downloads_left=5
        )
        cred2 = Credential(
            identifier="cred2", email="test2@example.com", password="pass2", downloads_left=10
        )

        # Need enough side effects for all calls in the retry loop
        mock_cm.get_current.side_effect = [cred1, cred1, cred2, cred2, cred2, cred2]
        mock_cm.get_available.return_value = [cred1, cred2]
        mock_cm.rotate.return_value = cred2
        mock_cm.update_downloads_left.return_value = (True, None)

        book = {"title": "Test Book"}
        result = cli.download_book(mock_client1, book, mock_pool, str(tmp_path))

        # Should succeed with second credential
        assert result is not None
        assert (tmp_path / "test.pdf").exists()

        # Verify rotation was called after failure
        mock_cm.rotate.assert_called()

        captured = capsys.readouterr()
        assert "failed" in captured.out.lower() or "trying next credential" in captured.out.lower()

    def test_download_book_all_credentials_exhausted(
        self, tmp_path: Path, capsys: pytest.CaptureFixture
    ) -> None:
        """Test download_book handles all credentials exhausted scenario."""
        mock_client = Mock()

        mock_pool = Mock()
        mock_cm = Mock()
        mock_pool.credential_manager = mock_cm
        mock_pool.get_current_client.return_value = None

        cred1 = Credential(
            identifier="cred1", email="test1@example.com", password="pass1", downloads_left=0
        )

        mock_cm.get_current.return_value = cred1
        mock_cm.get_available.return_value = []  # All exhausted

        book = {"title": "Test Book"}
        result = cli.download_book(mock_client, book, mock_pool, str(tmp_path))

        # Should return None
        assert result is None

        captured = capsys.readouterr()
        assert "exhausted" in captured.out.lower() or "download limits" in captured.out.lower()

    def test_download_limit_warning(self, capsys: pytest.CaptureFixture) -> None:
        """Test warning is displayed when credential is approaching download limit."""
        mock_cm = Mock()

        # Test with 5 downloads left (should warn)
        cred_low = Credential(
            identifier="cred1", email="test1@example.com", password="pass1", downloads_left=5
        )
        mock_cm.get_current.return_value = cred_low

        cli._check_download_limit_warning(mock_cm)

        captured = capsys.readouterr()
        assert "warning" in captured.out.lower()
        assert "5" in captured.out

    def test_download_limit_no_warning_for_high_limits(self, capsys: pytest.CaptureFixture) -> None:
        """Test no warning is displayed when credential has plenty of downloads."""
        mock_cm = Mock()

        # Test with 10 downloads left (should not warn)
        cred_high = Credential(
            identifier="cred1", email="test1@example.com", password="pass1", downloads_left=10
        )
        mock_cm.get_current.return_value = cred_high

        cli._check_download_limit_warning(mock_cm)

        captured = capsys.readouterr()
        assert "warning" not in captured.out.lower()

    def test_download_limit_no_warning_for_none(self, capsys: pytest.CaptureFixture) -> None:
        """Test no warning when downloads_left is None."""
        mock_cm = Mock()

        cred_none = Credential(
            identifier="cred1", email="test1@example.com", password="pass1", downloads_left=None
        )
        mock_cm.get_current.return_value = cred_none

        cli._check_download_limit_warning(mock_cm)

        captured = capsys.readouterr()
        assert "warning" not in captured.out.lower()
