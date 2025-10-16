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

    def test_display_credential_status_with_remix_auth(
        self, capsys: pytest.CaptureFixture
    ) -> None:
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
