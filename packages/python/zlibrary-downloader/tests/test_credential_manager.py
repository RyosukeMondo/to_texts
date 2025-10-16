"""
Unit tests for the CredentialManager class.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import pytest

from zlibrary_downloader.credential import Credential, CredentialStatus
from zlibrary_downloader.credential_manager import CredentialManager


class TestCredentialSourceDetection:
    """Tests for credential source auto-detection."""

    def test_detect_toml_when_both_exist(self, tmp_path):
        """Test that TOML is preferred when both TOML and .env exist."""
        # Create both files
        toml_file = tmp_path / "zlibrary_credentials.toml"
        env_file = tmp_path / ".env"
        toml_file.write_text("[[credentials]]\n")
        env_file.write_text("ZLIBRARY_EMAIL=test@test.com\n")

        # Change to tmp directory
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            manager = CredentialManager()
            assert manager.detect_credential_source() == "toml"
        finally:
            os.chdir(original_cwd)

    def test_detect_env_when_only_env_exists(self, tmp_path):
        """Test that .env is detected when only .env exists."""
        env_file = tmp_path / ".env"
        env_file.write_text("ZLIBRARY_EMAIL=test@test.com\n")

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            manager = CredentialManager()
            assert manager.detect_credential_source() == "env"
        finally:
            os.chdir(original_cwd)

    def test_detect_raises_when_no_source(self, tmp_path):
        """Test that FileNotFoundError is raised when no credential source exists."""
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            manager = CredentialManager()
            with pytest.raises(FileNotFoundError, match="No credential configuration found"):
                manager.detect_credential_source()
        finally:
            os.chdir(original_cwd)


class TestLoadFromToml:
    """Tests for loading credentials from TOML files."""

    def test_load_valid_toml_with_email_auth(self, tmp_path):
        """Test loading TOML file with email/password authentication."""
        toml_content = """
[[credentials]]
identifier = "user1"
email = "user1@example.com"
password = "password1"
enabled = true

[[credentials]]
identifier = "user2"
email = "user2@example.com"
password = "password2"
enabled = true
"""
        toml_file = tmp_path / "test_creds.toml"
        toml_file.write_text(toml_content)

        manager = CredentialManager()
        manager.load_from_toml(str(toml_file))

        assert len(manager.credentials) == 2
        assert manager.credentials[0].identifier == "user1"
        assert manager.credentials[0].email == "user1@example.com"
        assert manager.credentials[0].password == "password1"
        assert manager.credentials[1].identifier == "user2"

    def test_load_valid_toml_with_remix_auth(self, tmp_path):
        """Test loading TOML file with remix token authentication."""
        toml_content = """
[[credentials]]
identifier = "remix_user"
remix_userid = "12345"
remix_userkey = "abcdef123456"
enabled = true
"""
        toml_file = tmp_path / "test_creds.toml"
        toml_file.write_text(toml_content)

        manager = CredentialManager()
        manager.load_from_toml(str(toml_file))

        assert len(manager.credentials) == 1
        assert manager.credentials[0].identifier == "remix_user"
        assert manager.credentials[0].remix_userid == "12345"
        assert manager.credentials[0].remix_userkey == "abcdef123456"

    def test_load_toml_with_mixed_auth_methods(self, tmp_path):
        """Test loading TOML with both email and remix auth methods."""
        toml_content = """
[[credentials]]
identifier = "email_user"
email = "user@example.com"
password = "password"

[[credentials]]
identifier = "remix_user"
remix_userid = "12345"
remix_userkey = "abcdef"
"""
        toml_file = tmp_path / "test_creds.toml"
        toml_file.write_text(toml_content)

        manager = CredentialManager()
        manager.load_from_toml(str(toml_file))

        assert len(manager.credentials) == 2
        assert manager.credentials[0].email == "user@example.com"
        assert manager.credentials[1].remix_userid == "12345"

    def test_load_toml_filters_disabled_credentials(self, tmp_path):
        """Test that disabled credentials are filtered out."""
        toml_content = """
[[credentials]]
identifier = "enabled_user"
email = "enabled@example.com"
password = "password"
enabled = true

[[credentials]]
identifier = "disabled_user"
email = "disabled@example.com"
password = "password"
enabled = false
"""
        toml_file = tmp_path / "test_creds.toml"
        toml_file.write_text(toml_content)

        manager = CredentialManager()
        manager.load_from_toml(str(toml_file))

        assert len(manager.credentials) == 1
        assert manager.credentials[0].identifier == "enabled_user"

    def test_load_toml_default_enabled_true(self, tmp_path):
        """Test that credentials without 'enabled' field default to enabled=true."""
        toml_content = """
[[credentials]]
identifier = "user"
email = "user@example.com"
password = "password"
"""
        toml_file = tmp_path / "test_creds.toml"
        toml_file.write_text(toml_content)

        manager = CredentialManager()
        manager.load_from_toml(str(toml_file))

        assert len(manager.credentials) == 1
        assert manager.credentials[0].enabled is True

    def test_load_toml_raises_on_missing_file(self):
        """Test that FileNotFoundError is raised for missing TOML file."""
        manager = CredentialManager()
        with pytest.raises(FileNotFoundError, match="TOML file not found"):
            manager.load_from_toml("nonexistent.toml")

    def test_load_toml_raises_on_malformed_toml(self, tmp_path):
        """Test that ValueError is raised for malformed TOML."""
        toml_file = tmp_path / "bad.toml"
        toml_file.write_text("[[credentials]\ninvalid toml syntax")

        manager = CredentialManager()
        with pytest.raises(ValueError, match="Failed to parse TOML file"):
            manager.load_from_toml(str(toml_file))

    def test_load_toml_raises_on_missing_credentials_section(self, tmp_path):
        """Test that ValueError is raised when 'credentials' section is missing."""
        toml_file = tmp_path / "no_creds.toml"
        toml_file.write_text("[other_section]\nkey = 'value'\n")

        manager = CredentialManager()
        with pytest.raises(ValueError, match="missing 'credentials' section"):
            manager.load_from_toml(str(toml_file))

    def test_load_toml_raises_on_empty_credentials(self, tmp_path):
        """Test that ValueError is raised when credentials list is empty."""
        toml_file = tmp_path / "empty_creds.toml"
        toml_file.write_text("credentials = []\n")

        manager = CredentialManager()
        with pytest.raises(ValueError, match="contains no credentials"):
            manager.load_from_toml(str(toml_file))

    def test_load_toml_raises_on_missing_identifier(self, tmp_path):
        """Test that ValueError is raised when credential lacks identifier."""
        toml_content = """
[[credentials]]
email = "user@example.com"
password = "password"
"""
        toml_file = tmp_path / "no_id.toml"
        toml_file.write_text(toml_content)

        manager = CredentialManager()
        with pytest.raises(ValueError, match="missing required field 'identifier'"):
            manager.load_from_toml(str(toml_file))

    def test_load_toml_raises_on_missing_auth_fields(self, tmp_path):
        """Test that ValueError is raised when credential lacks auth fields."""
        toml_content = """
[[credentials]]
identifier = "user"
"""
        toml_file = tmp_path / "no_auth.toml"
        toml_file.write_text(toml_content)

        manager = CredentialManager()
        with pytest.raises(ValueError, match="must have either email/password or remix"):
            manager.load_from_toml(str(toml_file))

    def test_load_toml_raises_when_all_disabled(self, tmp_path):
        """Test that ValueError is raised when all credentials are disabled."""
        toml_content = """
[[credentials]]
identifier = "user"
email = "user@example.com"
password = "password"
enabled = false
"""
        toml_file = tmp_path / "all_disabled.toml"
        toml_file.write_text(toml_content)

        manager = CredentialManager()
        with pytest.raises(ValueError, match="No enabled credentials found"):
            manager.load_from_toml(str(toml_file))


class TestLoadFromEnv:
    """Tests for loading credentials from .env file."""

    @patch.dict(os.environ, {}, clear=True)
    @patch("zlibrary_downloader.credential_manager.load_dotenv")
    def test_load_from_env_with_remix_credentials(self, mock_load_dotenv):
        """Test loading single credential from .env with remix tokens."""
        with patch.dict(
            os.environ,
            {
                "ZLIBRARY_REMIX_USERID": "12345",
                "ZLIBRARY_REMIX_USERKEY": "abcdef123456",
            },
        ):
            manager = CredentialManager()
            manager.load_from_env()

            assert len(manager.credentials) == 1
            assert manager.credentials[0].identifier == "default"
            assert manager.credentials[0].remix_userid == "12345"
            assert manager.credentials[0].remix_userkey == "abcdef123456"
            assert manager.credentials[0].email is None
            assert manager.credentials[0].password is None

    @patch.dict(os.environ, {}, clear=True)
    @patch("zlibrary_downloader.credential_manager.load_dotenv")
    def test_load_from_env_with_email_password(self, mock_load_dotenv):
        """Test loading single credential from .env with email/password."""
        with patch.dict(
            os.environ,
            {
                "ZLIBRARY_EMAIL": "user@example.com",
                "ZLIBRARY_PASSWORD": "password123",
            },
        ):
            manager = CredentialManager()
            manager.load_from_env()

            assert len(manager.credentials) == 1
            assert manager.credentials[0].identifier == "default"
            assert manager.credentials[0].email == "user@example.com"
            assert manager.credentials[0].password == "password123"
            assert manager.credentials[0].remix_userid is None
            assert manager.credentials[0].remix_userkey is None

    @patch.dict(os.environ, {}, clear=True)
    @patch("zlibrary_downloader.credential_manager.load_dotenv")
    def test_load_from_env_prefers_remix_over_email(self, mock_load_dotenv):
        """Test that remix credentials are used even when email/password exist."""
        with patch.dict(
            os.environ,
            {
                "ZLIBRARY_REMIX_USERID": "12345",
                "ZLIBRARY_REMIX_USERKEY": "abcdef",
                "ZLIBRARY_EMAIL": "user@example.com",
                "ZLIBRARY_PASSWORD": "password",
            },
        ):
            manager = CredentialManager()
            manager.load_from_env()

            # Both should be set (stored in same credential)
            assert manager.credentials[0].remix_userid == "12345"
            assert manager.credentials[0].email == "user@example.com"

    @patch.dict(os.environ, {}, clear=True)
    @patch("zlibrary_downloader.credential_manager.load_dotenv")
    def test_load_from_env_raises_on_no_credentials(self, mock_load_dotenv):
        """Test that ValueError is raised when no credentials in .env."""
        manager = CredentialManager()
        with pytest.raises(ValueError, match="No valid credentials found in .env"):
            manager.load_from_env()

    @patch.dict(os.environ, {}, clear=True)
    @patch("zlibrary_downloader.credential_manager.load_dotenv")
    def test_load_from_env_raises_on_incomplete_remix(self, mock_load_dotenv):
        """Test that ValueError is raised with incomplete remix credentials."""
        with patch.dict(os.environ, {"ZLIBRARY_REMIX_USERID": "12345"}):
            manager = CredentialManager()
            with pytest.raises(ValueError, match="No valid credentials found"):
                manager.load_from_env()

    @patch.dict(os.environ, {}, clear=True)
    @patch("zlibrary_downloader.credential_manager.load_dotenv")
    def test_load_from_env_raises_on_incomplete_email(self, mock_load_dotenv):
        """Test that ValueError is raised with incomplete email credentials."""
        with patch.dict(os.environ, {"ZLIBRARY_EMAIL": "user@example.com"}):
            manager = CredentialManager()
            with pytest.raises(ValueError, match="No valid credentials found"):
                manager.load_from_env()


class TestLoadCredentialsAutoDetect:
    """Tests for automatic credential source detection and loading."""

    def test_load_credentials_uses_toml_when_available(self, tmp_path):
        """Test that load_credentials uses TOML when available."""
        toml_content = """
[[credentials]]
identifier = "user"
email = "user@example.com"
password = "password"
"""
        toml_file = tmp_path / "zlibrary_credentials.toml"
        toml_file.write_text(toml_content)

        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            manager = CredentialManager()
            manager.load_credentials()

            assert len(manager.credentials) == 1
            assert manager.credentials[0].identifier == "user"
        finally:
            os.chdir(original_cwd)

    @patch.dict(os.environ, {}, clear=True)
    @patch("zlibrary_downloader.credential_manager.load_dotenv")
    def test_load_credentials_uses_env_when_no_toml(self, mock_load_dotenv, tmp_path):
        """Test that load_credentials uses .env when TOML not available."""
        env_file = tmp_path / ".env"
        env_file.write_text("ZLIBRARY_EMAIL=user@test.com\n")

        with patch.dict(
            os.environ,
            {
                "ZLIBRARY_EMAIL": "user@example.com",
                "ZLIBRARY_PASSWORD": "password",
            },
        ):
            original_cwd = os.getcwd()
            try:
                os.chdir(tmp_path)
                manager = CredentialManager()
                manager.load_credentials()

                assert len(manager.credentials) == 1
                assert manager.credentials[0].identifier == "default"
            finally:
                os.chdir(original_cwd)


class TestCredentialAccess:
    """Tests for accessing credentials."""

    def test_get_current_returns_first_credential_initially(self):
        """Test that get_current returns first credential initially."""
        manager = CredentialManager()
        manager.credentials = [
            Credential(identifier="user1", email="user1@test.com", password="pass1"),
            Credential(identifier="user2", email="user2@test.com", password="pass2"),
        ]

        current = manager.get_current()
        assert current is not None
        assert current.identifier == "user1"

    def test_get_current_returns_none_when_no_credentials(self):
        """Test that get_current returns None when no credentials loaded."""
        manager = CredentialManager()
        assert manager.get_current() is None

    def test_get_current_handles_invalid_index(self):
        """Test that get_current handles invalid current_index gracefully."""
        manager = CredentialManager()
        manager.credentials = [
            Credential(identifier="user1", email="user1@test.com", password="pass1"),
        ]
        manager.current_index = 10  # Invalid index

        assert manager.get_current() is None

    def test_get_available_filters_invalid_credentials(self):
        """Test that get_available filters out invalid credentials."""
        manager = CredentialManager()
        manager.credentials = [
            Credential(identifier="valid", email="valid@test.com", password="pass", enabled=True),
            Credential(
                identifier="invalid",
                email="invalid@test.com",
                password="pass",
                status=CredentialStatus.INVALID,
            ),
            Credential(
                identifier="exhausted",
                email="exhausted@test.com",
                password="pass",
                status=CredentialStatus.EXHAUSTED,
            ),
            Credential(
                identifier="disabled",
                email="disabled@test.com",
                password="pass",
                enabled=False,
            ),
        ]

        available = manager.get_available()
        assert len(available) == 1
        assert available[0].identifier == "valid"

    def test_get_available_filters_zero_downloads(self):
        """Test that get_available filters out credentials with zero downloads."""
        manager = CredentialManager()
        manager.credentials = [
            Credential(
                identifier="has_downloads",
                email="user1@test.com",
                password="pass",
                downloads_left=5,
            ),
            Credential(
                identifier="no_downloads",
                email="user2@test.com",
                password="pass",
                downloads_left=0,
            ),
        ]

        available = manager.get_available()
        assert len(available) == 1
        assert available[0].identifier == "has_downloads"


class TestCredentialRotation:
    """Tests for credential rotation logic."""

    def test_rotate_moves_to_next_credential(self):
        """Test that rotate moves to the next credential."""
        manager = CredentialManager()
        manager.credentials = [
            Credential(identifier="user1", email="user1@test.com", password="pass1"),
            Credential(identifier="user2", email="user2@test.com", password="pass2"),
        ]
        manager.current_index = 0

        next_cred = manager.rotate()
        assert next_cred is not None
        assert next_cred.identifier == "user2"
        assert manager.current_index == 1

    def test_rotate_wraps_around_to_beginning(self):
        """Test that rotate wraps around to first credential."""
        manager = CredentialManager()
        manager.credentials = [
            Credential(identifier="user1", email="user1@test.com", password="pass1"),
            Credential(identifier="user2", email="user2@test.com", password="pass2"),
        ]
        manager.current_index = 1

        next_cred = manager.rotate()
        assert next_cred is not None
        assert next_cred.identifier == "user1"
        assert manager.current_index == 0

    def test_rotate_skips_unavailable_credentials(self):
        """Test that rotate skips over unavailable credentials."""
        manager = CredentialManager()
        manager.credentials = [
            Credential(identifier="user1", email="user1@test.com", password="pass1"),
            Credential(
                identifier="user2",
                email="user2@test.com",
                password="pass2",
                status=CredentialStatus.INVALID,
            ),
            Credential(identifier="user3", email="user3@test.com", password="pass3"),
        ]
        manager.current_index = 0

        next_cred = manager.rotate()
        assert next_cred is not None
        assert next_cred.identifier == "user3"  # Skipped user2
        assert manager.current_index == 2

    def test_rotate_returns_none_when_all_exhausted(self):
        """Test that rotate returns None when all credentials exhausted."""
        manager = CredentialManager()
        manager.credentials = [
            Credential(
                identifier="user1",
                email="user1@test.com",
                password="pass1",
                status=CredentialStatus.EXHAUSTED,
            ),
            Credential(
                identifier="user2",
                email="user2@test.com",
                password="pass2",
                status=CredentialStatus.INVALID,
            ),
        ]
        manager.current_index = 0

        next_cred = manager.rotate()
        assert next_cred is None

    def test_rotate_raises_when_no_credentials_loaded(self):
        """Test that rotate raises RuntimeError when no credentials loaded."""
        manager = CredentialManager()
        with pytest.raises(RuntimeError, match="No credentials loaded"):
            manager.rotate()


class TestStatePersistence:
    """Tests for state persistence integration."""

    def test_state_file_custom_path(self, tmp_path):
        """Test that custom state file path is used."""
        state_file = tmp_path / "custom_state.json"
        manager = CredentialManager(state_file=state_file)

        assert manager.rotation_state.state_file == state_file

    def test_state_file_default_path(self):
        """Test that default state file path is set."""
        manager = CredentialManager()
        expected_path = Path.home() / ".zlibrary" / "rotation_state.json"
        assert manager.rotation_state.state_file == expected_path

    def test_load_from_toml_restores_state(self, tmp_path):
        """Test that loading TOML restores state from file."""
        # Create TOML file
        toml_content = """
[[credentials]]
identifier = "user1"
email = "user1@example.com"
password = "password1"

[[credentials]]
identifier = "user2"
email = "user2@example.com"
password = "password2"
"""
        toml_file = tmp_path / "test_creds.toml"
        toml_file.write_text(toml_content)

        # Create state file
        state_file = tmp_path / "state.json"
        state_content = {
            "current_index": 1,
            "credentials": [
                {
                    "identifier": "user1",
                    "status": "valid",
                    "downloads_left": 10,
                },
                {
                    "identifier": "user2",
                    "status": "valid",
                    "downloads_left": 5,
                },
            ],
        }
        import json

        with open(state_file, "w") as f:
            json.dump(state_content, f)

        # Load credentials
        manager = CredentialManager(state_file=state_file)
        manager.load_from_toml(str(toml_file))

        # Verify state restored
        assert manager.current_index == 1
        assert manager.credentials[0].downloads_left == 10
        assert manager.credentials[1].downloads_left == 5

    def test_rotate_saves_state(self, tmp_path):
        """Test that rotate saves state to file."""
        state_file = tmp_path / "state.json"
        manager = CredentialManager(state_file=state_file)
        manager.credentials = [
            Credential(identifier="user1", email="user1@test.com", password="pass1"),
            Credential(identifier="user2", email="user2@test.com", password="pass2"),
        ]
        manager.current_index = 0

        # Rotate
        manager.rotate()

        # Verify state saved
        assert state_file.exists()
        import json

        with open(state_file) as f:
            state = json.load(f)

        assert state["current_index"] == 1
        assert len(state["credentials"]) == 2
