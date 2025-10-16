"""
Integration tests for zlibrary_downloader CLI with multi-credential support.

These tests verify end-to-end workflows with CredentialManager and ClientPool integration,
testing realistic scenarios including:
- CLI initialization with multi-credential setup
- Search operations with automatic rotation
- Download operations with rotation and limit tracking
- Backward compatibility with single credential (.env)
- Error scenarios (all exhausted, invalid credentials)
- Credential status display

Unlike unit tests, these tests use real CredentialManager and ClientPool instances
with mocked Zlibrary API calls to test the full integration stack.

Target: >80% code coverage for integration paths
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from zlibrary_downloader import cli
from zlibrary_downloader.client_pool import ZlibraryClientPool
from zlibrary_downloader.credential import CredentialStatus


@pytest.fixture
def temp_workspace():
    """Create a temporary workspace directory for test files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        old_cwd = os.getcwd()
        os.chdir(tmpdir)
        try:
            yield Path(tmpdir)
        finally:
            os.chdir(old_cwd)


@pytest.fixture
def mock_zlibrary_client():
    """Create a mock Zlibrary client that simulates successful operations."""
    mock_client = Mock()
    mock_client.isLoggedIn.return_value = True
    mock_client.getProfile.return_value = {
        "success": True,
        "user": {
            "email": "test@example.com",
            "name": "Test User",
            "downloads_limit": 10,
            "downloads_today": 0,
        },
    }
    mock_client.search.return_value = {
        "books": [
            {
                "title": "Test Book 1",
                "author": "Test Author",
                "year": "2023",
                "publisher": "Test Publisher",
                "language": "English",
                "extension": "pdf",
                "size": "1.5 MB",
                "id": "12345",
            },
            {
                "title": "Test Book 2",
                "author": "Another Author",
                "year": "2024",
                "publisher": "Another Publisher",
                "language": "English",
                "extension": "epub",
                "size": "2.3 MB",
                "id": "67890",
            },
        ]
    }
    mock_client.downloadBook.return_value = ("test_book.pdf", b"fake pdf content")
    return mock_client


class TestMultiCredentialInitialization:
    """Test suite for CLI initialization with multi-credential setup."""

    def test_initialization_with_toml_multiple_credentials(
        self, temp_workspace: Path, mock_zlibrary_client: Mock
    ):
        """Test CLI initialization with TOML file containing multiple credentials."""
        # Create TOML file with multiple credentials
        toml_content = """
[[credentials]]
identifier = "account1"
email = "test1@example.com"
password = "password1"
enabled = true

[[credentials]]
identifier = "account2"
email = "test2@example.com"
password = "password2"
enabled = true

[[credentials]]
identifier = "account3"
remix_userid = "userid123"
remix_userkey = "userkey456"
enabled = true
"""
        toml_file = temp_workspace / "zlibrary_credentials.toml"
        toml_file.write_text(toml_content)

        # Mock Zlibrary client creation
        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            mock_zlib_class.return_value = mock_zlibrary_client

            # Load credentials and initialize
            credential_manager, client_pool = cli.load_credentials()

            # Verify 3 credentials loaded
            assert len(credential_manager.credentials) == 3
            assert credential_manager.credentials[0].identifier == "account1"
            assert credential_manager.credentials[1].identifier == "account2"
            assert credential_manager.credentials[2].identifier == "account3"

            # Verify client pool is properly initialized
            assert isinstance(client_pool, ZlibraryClientPool)
            assert client_pool.credential_manager == credential_manager

            # Verify current client can be obtained
            client = cli.initialize_zlibrary(client_pool)
            assert client is not None

    def test_initialization_with_toml_disabled_credentials_filtered(
        self, temp_workspace: Path, mock_zlibrary_client: Mock
    ):
        """Test that disabled credentials in TOML are properly filtered out."""
        toml_content = """
[[credentials]]
identifier = "account1"
email = "test1@example.com"
password = "password1"
enabled = true

[[credentials]]
identifier = "account2"
email = "test2@example.com"
password = "password2"
enabled = false

[[credentials]]
identifier = "account3"
email = "test3@example.com"
password = "password3"
enabled = true
"""
        toml_file = temp_workspace / "zlibrary_credentials.toml"
        toml_file.write_text(toml_content)

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            mock_zlib_class.return_value = mock_zlibrary_client

            credential_manager, client_pool = cli.load_credentials()

            # Should only load 2 credentials (account2 is disabled)
            assert len(credential_manager.credentials) == 2
            assert credential_manager.credentials[0].identifier == "account1"
            assert credential_manager.credentials[1].identifier == "account3"

    def test_initialization_with_env_single_credential(
        self, temp_workspace: Path, mock_zlibrary_client: Mock
    ):
        """Test CLI initialization with .env file (backward compatibility)."""
        # Create .env file
        env_content = """
ZLIBRARY_EMAIL=test@example.com
ZLIBRARY_PASSWORD=testpassword
"""
        env_file = temp_workspace / ".env"
        env_file.write_text(env_content)

        # Mock environment to return our test values
        test_env = {
            "ZLIBRARY_EMAIL": "test@example.com",
            "ZLIBRARY_PASSWORD": "testpassword"
        }
        with patch.dict(os.environ, test_env, clear=True):
            with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
                mock_zlib_class.return_value = mock_zlibrary_client

                credential_manager, client_pool = cli.load_credentials()

                # Should have single credential with identifier "default"
                assert len(credential_manager.credentials) == 1
                assert credential_manager.credentials[0].identifier == "default"
                assert credential_manager.credentials[0].email == "test@example.com"

                # Verify client pool works
                client = cli.initialize_zlibrary(client_pool)
                assert client is not None

    def test_initialization_with_env_remix_tokens(
        self, temp_workspace: Path, mock_zlibrary_client: Mock
    ):
        """Test CLI initialization with .env file using remix tokens."""
        env_content = """
ZLIBRARY_REMIX_USERID=userid123
ZLIBRARY_REMIX_USERKEY=userkey456
"""
        env_file = temp_workspace / ".env"
        env_file.write_text(env_content)

        # Mock environment to return our test values
        test_env = {
            "ZLIBRARY_REMIX_USERID": "userid123",
            "ZLIBRARY_REMIX_USERKEY": "userkey456"
        }
        with patch.dict(os.environ, test_env, clear=True):
            with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
                mock_zlib_class.return_value = mock_zlibrary_client

                credential_manager, client_pool = cli.load_credentials()

                assert len(credential_manager.credentials) == 1
                assert credential_manager.credentials[0].remix_userid == "userid123"
                assert credential_manager.credentials[0].remix_userkey == "userkey456"


class TestSearchOperationWithRotation:
    """Test suite for search operations with automatic credential rotation."""

    def test_search_with_multiple_credentials_rotates(
        self, temp_workspace: Path, mock_zlibrary_client: Mock, capsys
    ):
        """Test that search operation rotates to next credential after success."""
        toml_content = """
[[credentials]]
identifier = "account1"
email = "test1@example.com"
password = "password1"

[[credentials]]
identifier = "account2"
email = "test2@example.com"
password = "password2"
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            mock_zlib_class.return_value = mock_zlibrary_client

            credential_manager, client_pool = cli.load_credentials()

            # Remember initial credential (could be any if state was restored)
            initial_cred = credential_manager.get_current().identifier

            # Perform search
            z_client = client_pool.get_current_client()
            results = cli.search_books(z_client, "test query", client_pool)

            # Verify search succeeded
            assert results is not None
            assert "books" in results
            assert len(results["books"]) == 2

            # Verify rotation occurred - should be different from initial
            current_cred = credential_manager.get_current().identifier
            # With 2 credentials, should have rotated to the other one
            assert current_cred != initial_cred or len(credential_manager.credentials) == 1

    def test_search_with_single_credential_no_rotation(
        self, temp_workspace: Path, mock_zlibrary_client: Mock
    ):
        """Test search with single credential doesn't try to rotate unnecessarily."""
        env_content = "ZLIBRARY_EMAIL=test@example.com\nZLIBRARY_PASSWORD=testpass"
        (temp_workspace / ".env").write_text(env_content)

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            mock_zlib_class.return_value = mock_zlibrary_client

            credential_manager, client_pool = cli.load_credentials()
            initial_cred = credential_manager.get_current()

            z_client = client_pool.get_current_client()
            results = cli.search_books(z_client, "test query", client_pool)

            assert results is not None

            # Should still be on same credential (wraps around to itself)
            assert credential_manager.get_current().identifier == initial_cred.identifier

    def test_search_retry_with_next_credential_on_failure(
        self, temp_workspace: Path, mock_zlibrary_client: Mock, capsys
    ):
        """Test that search retries with next credential when first one fails."""
        toml_content = """
[[credentials]]
identifier = "account1"
email = "test1@example.com"
password = "password1"

[[credentials]]
identifier = "account2"
email = "test2@example.com"
password = "password2"
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        # First client fails, second succeeds
        mock_client_fail = Mock()
        mock_client_fail.isLoggedIn.return_value = True
        mock_client_fail.search.side_effect = Exception("Network error")

        mock_client_success = Mock()
        mock_client_success.isLoggedIn.return_value = True
        mock_client_success.search.return_value = {"books": [{"title": "Test Book"}]}

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            mock_zlib_class.side_effect = [mock_client_fail, mock_client_success]

            credential_manager, client_pool = cli.load_credentials()

            z_client = client_pool.get_current_client()
            results = cli.search_books(z_client, "test query", client_pool)

            # Should succeed with second credential
            assert results is not None
            assert "books" in results

            # Verify rotation occurred (should be on account2 after failure retry)
            captured = capsys.readouterr()
            lower_out = captured.out.lower()
            assert "trying next credential" in lower_out or "failed" in lower_out


class TestDownloadOperationWithRotation:
    """Test suite for download operations with rotation and limit tracking."""

    def test_download_with_multi_creds_updates_limits_rotates(
        self, temp_workspace: Path, mock_zlibrary_client: Mock
    ):
        """Test download updates limits and rotates to next credential."""
        toml_content = """
[[credentials]]
identifier = "account1"
email = "test1@example.com"
password = "password1"

[[credentials]]
identifier = "account2"
email = "test2@example.com"
password = "password2"
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        # Mock client that returns updated profile after download
        mock_client_after = Mock()
        mock_client_after.isLoggedIn.return_value = True
        mock_client_after.getProfile.return_value = {
            "success": True,
            "user": {
                "email": "test1@example.com",
                "name": "Test User",
                "downloads_limit": 10,
                "downloads_today": 1,  # After 1 download
            },
        }
        mock_client_after.downloadBook.return_value = (
            "test_book.pdf",
            b"fake pdf content",
        )

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            with patch("zlibrary_downloader.client.Zlibrary") as mock_client_class:
                mock_zlib_class.return_value = mock_client_after
                mock_client_class.return_value = mock_client_after

                credential_manager, client_pool = cli.load_credentials()

                # Initial state
                assert credential_manager.get_current().identifier == "account1"

                z_client = client_pool.get_current_client()
                book = {"title": "Test Book", "id": "12345"}
                download_dir = temp_workspace / "downloads"

                result = cli.download_book(z_client, book, client_pool, str(download_dir))

                # Verify download succeeded
                assert result is not None
                assert (download_dir / "test_book.pdf").exists()

                # Verify credential's download limit was updated (should be 9 remaining)
                account1 = credential_manager.credentials[0]
                assert account1.downloads_left == 9

                # Verify rotation occurred
                assert credential_manager.get_current().identifier == "account2"

    def test_download_skips_exhausted_credentials(
        self, temp_workspace: Path, mock_zlibrary_client: Mock, capsys
    ):
        """Test that download automatically skips credentials with 0 downloads left."""
        toml_content = """
[[credentials]]
identifier = "account1"
email = "test1@example.com"
password = "password1"

[[credentials]]
identifier = "account2"
email = "test2@example.com"
password = "password2"
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        # Mock first credential as exhausted
        mock_client_exhausted = Mock()
        mock_client_exhausted.isLoggedIn.return_value = True
        mock_client_exhausted.getProfile.return_value = {
            "success": True,
            "user": {"downloads_limit": 10, "downloads_today": 10},  # Exhausted
        }
        mock_client_exhausted.downloadBook.return_value = ("test.pdf", b"content")

        # Mock second credential as available
        mock_client_available = Mock()
        mock_client_available.isLoggedIn.return_value = True
        mock_client_available.getProfile.return_value = {
            "success": True,
            "user": {"downloads_limit": 10, "downloads_today": 0},
        }
        mock_client_available.downloadBook.return_value = ("test.pdf", b"content")

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            with patch("zlibrary_downloader.client.Zlibrary") as mock_client_class:
                # Return exhausted client first, then available client
                mock_zlib_class.side_effect = [mock_client_exhausted, mock_client_available]
                mock_client_class.side_effect = [mock_client_exhausted, mock_client_available]

                credential_manager, client_pool = cli.load_credentials()

                # Validate first credential to set it as exhausted
                cred1 = credential_manager.credentials[0]
                credential_manager.validate_credential(cred1)
                assert credential_manager.credentials[0].downloads_left == 0
                assert credential_manager.credentials[0].status == CredentialStatus.EXHAUSTED

                # Reset to first credential
                credential_manager.current_index = 0

                # Clear client cache to force new client creation
                client_pool.clear_cache()

                z_client = client_pool.get_current_client()
                book = {"title": "Test Book"}
                download_dir = temp_workspace / "downloads"

                result = cli.download_book(z_client, book, client_pool, str(download_dir))

                # Should still succeed by rotating to account2
                assert result is not None

                # Should have rotated to account2
                assert credential_manager.get_current().identifier == "account2"

    def test_download_all_credentials_exhausted_fails_gracefully(
        self, temp_workspace: Path, capsys
    ):
        """Test download handles all credentials exhausted scenario gracefully."""
        toml_content = """
[[credentials]]
identifier = "account1"
email = "test1@example.com"
password = "password1"
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        mock_client_exhausted = Mock()
        mock_client_exhausted.isLoggedIn.return_value = True
        mock_client_exhausted.getProfile.return_value = {
            "success": True,
            "user": {"downloads_limit": 10, "downloads_today": 10},
        }

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            mock_zlib_class.return_value = mock_client_exhausted

            credential_manager, client_pool = cli.load_credentials()

            # Set credential as exhausted
            credential_manager.validate_credential(credential_manager.credentials[0])

            z_client = client_pool.get_current_client()
            book = {"title": "Test Book"}
            download_dir = temp_workspace / "downloads"

            result = cli.download_book(z_client, book, client_pool, str(download_dir))

            # Should fail gracefully
            assert result is None

            captured = capsys.readouterr()
            assert "exhausted" in captured.out.lower() or "download limits" in captured.out.lower()

    # Note: Detailed retry logic is covered in test_cli.py unit tests
    # Integration test for retry with cached clients is complex due to client pool caching


class TestCredentialStatusDisplay:
    """Test suite for credential status display functionality."""

    def test_display_status_with_multiple_credentials(
        self, temp_workspace: Path, mock_zlibrary_client: Mock, capsys
    ):
        """Test displaying status with multiple credentials shows correct summary."""
        toml_content = """
[[credentials]]
identifier = "account1"
email = "test1@example.com"
password = "password1"

[[credentials]]
identifier = "account2"
email = "test2@example.com"
password = "password2"

[[credentials]]
identifier = "account3"
remix_userid = "userid123"
remix_userkey = "userkey456"
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            with patch("zlibrary_downloader.client.Zlibrary") as mock_client_class:
                mock_zlib_class.return_value = mock_zlibrary_client
                mock_client_class.return_value = mock_zlibrary_client

                credential_manager, client_pool = cli.load_credentials()

                # Validate credentials to populate download limits
                for cred in credential_manager.credentials:
                    credential_manager.validate_credential(cred)

                cli.display_credential_status(credential_manager)

                captured = capsys.readouterr()
                assert "Total credentials: 3" in captured.out
                assert "Available credentials: 3" in captured.out
                # Don't assert specific current credential as validation may rotate

    def test_display_status_shows_authentication_method(
        self, temp_workspace: Path, mock_zlibrary_client: Mock, capsys
    ):
        """Test status display shows correct authentication method."""
        toml_content = """
[[credentials]]
identifier = "email_account"
email = "test@example.com"
password = "password"

[[credentials]]
identifier = "remix_account"
remix_userid = "userid123"
remix_userkey = "userkey456"
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            with patch("zlibrary_downloader.client.Zlibrary") as mock_client_class:
                mock_zlib_class.return_value = mock_zlibrary_client
                mock_client_class.return_value = mock_zlibrary_client

                credential_manager, client_pool = cli.load_credentials()

                # Verify we have both authentication types
                assert credential_manager.credentials[0].email is not None
                assert credential_manager.credentials[1].remix_userid is not None

                # Display status shows authentication method
                cli.display_credential_status(credential_manager)
                captured = capsys.readouterr()
                # Should show auth method for current credential
                assert "Email/password" in captured.out or "Remix tokens" in captured.out

    def test_display_status_shows_download_limits(
        self, temp_workspace: Path, mock_zlibrary_client: Mock, capsys
    ):
        """Test status display shows download limits when available."""
        toml_content = """
[[credentials]]
identifier = "account1"
email = "test@example.com"
password = "password"
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            with patch("zlibrary_downloader.client.Zlibrary") as mock_client_class:
                mock_zlib_class.return_value = mock_zlibrary_client
                mock_client_class.return_value = mock_zlibrary_client

                credential_manager, client_pool = cli.load_credentials()

                # Validate to populate download limits
                cred = credential_manager.credentials[0]
                is_valid, error = credential_manager.validate_credential(cred)
                assert is_valid, f"Validation should succeed: {error}"
                assert credential_manager.credentials[0].downloads_left == 10

                cli.display_credential_status(credential_manager)

                captured = capsys.readouterr()
                assert "Downloads remaining:" in captured.out
                assert "10" in captured.out  # From mock profile


class TestBackwardCompatibility:
    """Test suite for backward compatibility with single-credential .env format."""

    def test_env_format_works_end_to_end(
        self, temp_workspace: Path, mock_zlibrary_client: Mock
    ):
        """Test complete workflow with .env file (backward compatibility)."""
        env_content = "ZLIBRARY_EMAIL=test@example.com\nZLIBRARY_PASSWORD=testpass"
        (temp_workspace / ".env").write_text(env_content)

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            mock_zlib_class.return_value = mock_zlibrary_client

            # Load credentials
            credential_manager, client_pool = cli.load_credentials()

            assert len(credential_manager.credentials) == 1
            assert credential_manager.credentials[0].identifier == "default"

            # Initialize client
            z_client = cli.initialize_zlibrary(client_pool)
            assert z_client is not None

            # Perform search
            results = cli.search_books(z_client, "test query", client_pool)
            assert results is not None

            # Perform download
            book = {"title": "Test Book"}
            download_dir = temp_workspace / "downloads"
            result = cli.download_book(z_client, book, client_pool, str(download_dir))
            assert result is not None


class TestErrorScenarios:
    """Test suite for various error scenarios."""

    def test_no_credentials_file_exits_gracefully(self, temp_workspace: Path):
        """Test that missing credentials file causes graceful exit."""
        # No credential files exist
        with pytest.raises(SystemExit):
            cli.load_credentials()

    def test_invalid_toml_syntax_exits_gracefully(self, temp_workspace: Path):
        """Test that invalid TOML syntax is handled gracefully."""
        toml_content = """
[[credentials
identifier = "broken"
email = "test@example.com"
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        with pytest.raises(SystemExit):
            cli.load_credentials()

    def test_toml_missing_required_fields_exits_gracefully(self, temp_workspace: Path):
        """Test that TOML missing required fields is handled gracefully."""
        toml_content = """
[[credentials]]
identifier = "incomplete"
# Missing both email/password and remix tokens
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        with pytest.raises(SystemExit):
            cli.load_credentials()

    def test_all_credentials_invalid_handled_gracefully(
        self, temp_workspace: Path, capsys
    ):
        """Test handling when all credentials are invalid."""
        toml_content = """
[[credentials]]
identifier = "invalid1"
email = "bad@example.com"
password = "wrongpass"
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        mock_client_invalid = Mock()
        mock_client_invalid.isLoggedIn.return_value = False

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            mock_zlib_class.return_value = mock_client_invalid

            credential_manager, client_pool = cli.load_credentials()

            # Try to get client
            client = client_pool.get_current_client()

            # Should return None for invalid credentials
            assert client is None


class TestStateRestoration:
    """Test suite for state persistence and restoration across sessions."""

    def test_rotation_state_persists_across_loads(
        self, temp_workspace: Path, mock_zlibrary_client: Mock
    ):
        """Test that rotation state persists when credentials are reloaded."""
        toml_content = """
[[credentials]]
identifier = "account1"
email = "test1@example.com"
password = "password1"

[[credentials]]
identifier = "account2"
email = "test2@example.com"
password = "password2"
"""
        (temp_workspace / "zlibrary_credentials.toml").write_text(toml_content)

        with patch("zlibrary_downloader.client_pool.Zlibrary") as mock_zlib_class:
            mock_zlib_class.return_value = mock_zlibrary_client

            # First session: load and rotate
            credential_manager1, client_pool1 = cli.load_credentials()
            assert credential_manager1.get_current().identifier == "account1"

            # Perform operation that rotates
            z_client = client_pool1.get_current_client()
            cli.search_books(z_client, "test", client_pool1)

            # Should now be on account2
            assert credential_manager1.get_current().identifier == "account2"

            # Second session: reload credentials
            credential_manager2, client_pool2 = cli.load_credentials()

            # Should restore to account2 (persisted state)
            assert credential_manager2.get_current().identifier == "account2"
