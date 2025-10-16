"""
Unit tests for ZlibraryClientPool.

Tests client caching, rotation, validation, and error handling.
"""

import pytest
from unittest.mock import Mock, MagicMock, patch

from zlibrary_downloader.client_pool import ZlibraryClientPool
from zlibrary_downloader.credential import Credential, CredentialStatus
from zlibrary_downloader.credential_manager import CredentialManager


@pytest.fixture
def mock_credential_manager():
    """Create a mock CredentialManager with test credentials."""
    manager = Mock(spec=CredentialManager)

    # Create test credentials
    cred1 = Credential(
        identifier="user1",
        email="user1@example.com",
        password="pass1",
        status=CredentialStatus.VALID,
    )
    cred2 = Credential(
        identifier="user2",
        remix_userid="123",
        remix_userkey="key123",
        status=CredentialStatus.VALID,
    )
    cred3 = Credential(
        identifier="user3",
        email="user3@example.com",
        password="pass3",
        status=CredentialStatus.EXHAUSTED,
    )

    manager.credentials = [cred1, cred2, cred3]
    manager.current_index = 0
    manager.get_current.return_value = cred1

    return manager


@pytest.fixture
def client_pool(mock_credential_manager):
    """Create a ZlibraryClientPool with mock credential manager."""
    return ZlibraryClientPool(mock_credential_manager)


class TestClientPoolInitialization:
    """Tests for ZlibraryClientPool initialization."""

    def test_init_creates_empty_clients_dict(self, mock_credential_manager):
        """Test that initialization creates an empty clients dictionary."""
        pool = ZlibraryClientPool(mock_credential_manager)

        assert pool.credential_manager == mock_credential_manager
        assert pool.clients == {}

    def test_init_stores_credential_manager_reference(self, mock_credential_manager):
        """Test that credential manager reference is stored."""
        pool = ZlibraryClientPool(mock_credential_manager)

        assert pool.credential_manager is mock_credential_manager


class TestGetCurrentClient:
    """Tests for get_current_client() method."""

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_get_current_client_creates_new_client(self, mock_zlibrary_class, client_pool):
        """Test that get_current_client creates a new client when not cached."""
        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = True
        mock_zlibrary_class.return_value = mock_client

        result = client_pool.get_current_client()

        assert result == mock_client
        mock_zlibrary_class.assert_called_once_with(
            email="user1@example.com",
            password="pass1",
            remix_userid=None,
            remix_userkey=None,
        )

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_get_current_client_returns_cached_client(
        self, mock_zlibrary_class, client_pool
    ):
        """Test that get_current_client returns cached client on second call."""
        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = True
        mock_zlibrary_class.return_value = mock_client

        # First call creates client
        first_result = client_pool.get_current_client()
        # Second call should return cached client
        second_result = client_pool.get_current_client()

        assert first_result == second_result
        # Zlibrary should only be instantiated once
        assert mock_zlibrary_class.call_count == 1

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_get_current_client_caches_by_identifier(
        self, mock_zlibrary_class, client_pool
    ):
        """Test that clients are cached by credential identifier."""
        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = True
        mock_zlibrary_class.return_value = mock_client

        client_pool.get_current_client()

        assert "user1" in client_pool.clients
        assert client_pool.clients["user1"] == mock_client

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_get_current_client_with_remix_tokens(
        self, mock_zlibrary_class, mock_credential_manager, client_pool
    ):
        """Test client creation with remix tokens."""
        # Set current credential to remix token credential
        cred2 = mock_credential_manager.credentials[1]
        mock_credential_manager.get_current.return_value = cred2

        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = True
        mock_zlibrary_class.return_value = mock_client

        result = client_pool.get_current_client()

        assert result == mock_client
        mock_zlibrary_class.assert_called_once_with(
            email=None,
            password=None,
            remix_userid="123",
            remix_userkey="key123",
        )

    def test_get_current_client_returns_none_when_no_credential(
        self, mock_credential_manager, client_pool
    ):
        """Test that get_current_client returns None when no credential available."""
        mock_credential_manager.get_current.return_value = None

        result = client_pool.get_current_client()

        assert result is None

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_get_current_client_returns_none_on_login_failure(
        self, mock_zlibrary_class, client_pool
    ):
        """Test that get_current_client returns None when login fails."""
        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = False
        mock_zlibrary_class.return_value = mock_client

        result = client_pool.get_current_client()

        assert result is None
        assert "user1" not in client_pool.clients

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_get_current_client_returns_none_on_exception(
        self, mock_zlibrary_class, client_pool
    ):
        """Test that get_current_client returns None when client creation raises exception."""
        mock_zlibrary_class.side_effect = Exception("Connection error")

        result = client_pool.get_current_client()

        assert result is None
        assert "user1" not in client_pool.clients


class TestRotateClient:
    """Tests for rotate_client() method."""

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_rotate_client_calls_credential_manager_rotate(
        self, mock_zlibrary_class, mock_credential_manager, client_pool
    ):
        """Test that rotate_client calls credential manager's rotate method."""
        cred2 = mock_credential_manager.credentials[1]
        mock_credential_manager.rotate.return_value = cred2

        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = True
        mock_zlibrary_class.return_value = mock_client

        client_pool.rotate_client()

        mock_credential_manager.rotate.assert_called_once()

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_rotate_client_returns_new_client(
        self, mock_zlibrary_class, mock_credential_manager, client_pool
    ):
        """Test that rotate_client creates and returns client for next credential."""
        cred2 = mock_credential_manager.credentials[1]
        mock_credential_manager.rotate.return_value = cred2

        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = True
        mock_zlibrary_class.return_value = mock_client

        result = client_pool.rotate_client()

        assert result == mock_client
        mock_zlibrary_class.assert_called_once_with(
            email=None,
            password=None,
            remix_userid="123",
            remix_userkey="key123",
        )

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_rotate_client_caches_new_client(
        self, mock_zlibrary_class, mock_credential_manager, client_pool
    ):
        """Test that rotate_client caches the new client."""
        cred2 = mock_credential_manager.credentials[1]
        mock_credential_manager.rotate.return_value = cred2

        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = True
        mock_zlibrary_class.return_value = mock_client

        client_pool.rotate_client()

        assert "user2" in client_pool.clients
        assert client_pool.clients["user2"] == mock_client

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_rotate_client_returns_cached_if_available(
        self, mock_zlibrary_class, mock_credential_manager, client_pool
    ):
        """Test that rotate_client returns cached client if already exists."""
        cred2 = mock_credential_manager.credentials[1]
        mock_credential_manager.rotate.return_value = cred2

        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = True
        mock_zlibrary_class.return_value = mock_client

        # First rotation creates and caches client
        first_result = client_pool.rotate_client()
        # Second rotation to same credential should return cached client
        second_result = client_pool.rotate_client()

        assert first_result == second_result
        # Client should only be created once
        assert mock_zlibrary_class.call_count == 1

    def test_rotate_client_returns_none_when_all_exhausted(
        self, mock_credential_manager, client_pool
    ):
        """Test that rotate_client returns None when all credentials exhausted."""
        mock_credential_manager.rotate.return_value = None

        result = client_pool.rotate_client()

        assert result is None


class TestValidateAll:
    """Tests for validate_all() method."""

    def test_validate_all_validates_each_credential(
        self, mock_credential_manager, client_pool
    ):
        """Test that validate_all validates each credential."""
        mock_credential_manager.validate_credential.return_value = (True, None)

        client_pool.validate_all()

        assert mock_credential_manager.validate_credential.call_count == 3
        # Check that each credential was validated
        for cred in mock_credential_manager.credentials:
            mock_credential_manager.validate_credential.assert_any_call(cred)

    def test_validate_all_returns_results_dict(
        self, mock_credential_manager, client_pool
    ):
        """Test that validate_all returns dictionary of results."""
        # Mock different results for different credentials
        def mock_validate(credential):
            if credential.identifier in ("user1", "user2"):
                return (True, None)
            else:
                return (False, "Exhausted")

        mock_credential_manager.validate_credential.side_effect = mock_validate

        results = client_pool.validate_all()

        assert results == {
            "user1": (True, None),
            "user2": (True, None),
            "user3": (False, "Exhausted"),
        }

    def test_validate_all_with_mixed_results(
        self, mock_credential_manager, client_pool
    ):
        """Test validate_all with mix of valid and invalid credentials."""
        results_map = {
            "user1": (True, None),
            "user2": (False, "Invalid credentials"),
            "user3": (False, "Exhausted"),
        }

        def mock_validate(credential):
            return results_map[credential.identifier]

        mock_credential_manager.validate_credential.side_effect = mock_validate

        results = client_pool.validate_all()

        assert results["user1"] == (True, None)
        assert results["user2"] == (False, "Invalid credentials")
        assert results["user3"] == (False, "Exhausted")


class TestRefreshClient:
    """Tests for refresh_client() method."""

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_refresh_client_removes_cached_client(
        self, mock_zlibrary_class, client_pool
    ):
        """Test that refresh_client removes cached client."""
        mock_client1 = MagicMock()
        mock_client1.isLoggedIn.return_value = True
        mock_client2 = MagicMock()
        mock_client2.isLoggedIn.return_value = True
        mock_zlibrary_class.side_effect = [mock_client1, mock_client2]

        # Create and cache a client
        client_pool.get_current_client()
        old_client = client_pool.clients["user1"]

        # Refresh the client
        new_client = client_pool.refresh_client("user1")

        assert new_client is not old_client
        assert client_pool.clients["user1"] == new_client

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_refresh_client_creates_new_client(
        self, mock_zlibrary_class, client_pool
    ):
        """Test that refresh_client creates a new client instance."""
        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = True
        mock_zlibrary_class.return_value = mock_client

        result = client_pool.refresh_client("user1")

        assert result == mock_client
        mock_zlibrary_class.assert_called_once_with(
            email="user1@example.com",
            password="pass1",
            remix_userid=None,
            remix_userkey=None,
        )

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_refresh_client_works_without_cached_client(
        self, mock_zlibrary_class, client_pool
    ):
        """Test that refresh_client works even if client wasn't cached."""
        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = True
        mock_zlibrary_class.return_value = mock_client

        result = client_pool.refresh_client("user2")

        assert result == mock_client
        assert "user2" in client_pool.clients

    def test_refresh_client_raises_error_for_unknown_identifier(self, client_pool):
        """Test that refresh_client raises ValueError for unknown identifier."""
        with pytest.raises(ValueError, match="Credential with identifier 'unknown' not found"):
            client_pool.refresh_client("unknown")

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_refresh_client_returns_none_on_login_failure(
        self, mock_zlibrary_class, client_pool
    ):
        """Test that refresh_client returns None when login fails."""
        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = False
        mock_zlibrary_class.return_value = mock_client

        result = client_pool.refresh_client("user1")

        assert result is None
        assert "user1" not in client_pool.clients


class TestClearCache:
    """Tests for clear_cache() method."""

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_clear_cache_removes_all_cached_clients(
        self, mock_zlibrary_class, mock_credential_manager, client_pool
    ):
        """Test that clear_cache removes all cached clients."""
        mock_client = MagicMock()
        mock_client.isLoggedIn.return_value = True
        mock_zlibrary_class.return_value = mock_client

        # Create and cache some clients
        client_pool.get_current_client()

        cred2 = mock_credential_manager.credentials[1]
        mock_credential_manager.rotate.return_value = cred2
        client_pool.rotate_client()

        # Verify clients are cached
        assert len(client_pool.clients) > 0

        # Clear cache
        client_pool.clear_cache()

        assert len(client_pool.clients) == 0

    def test_clear_cache_on_empty_pool(self, client_pool):
        """Test that clear_cache works on empty pool."""
        client_pool.clear_cache()

        assert len(client_pool.clients) == 0


class TestClientCreationErrorHandling:
    """Tests for error handling during client creation."""

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_create_client_handles_connection_error(
        self, mock_zlibrary_class, client_pool
    ):
        """Test that _create_client handles connection errors gracefully."""
        mock_zlibrary_class.side_effect = ConnectionError("Network error")

        result = client_pool.get_current_client()

        assert result is None

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_create_client_handles_authentication_error(
        self, mock_zlibrary_class, client_pool
    ):
        """Test that _create_client handles authentication errors gracefully."""
        mock_zlibrary_class.side_effect = ValueError("Invalid credentials")

        result = client_pool.get_current_client()

        assert result is None

    @patch("zlibrary_downloader.client_pool.Zlibrary")
    def test_create_client_handles_generic_exception(
        self, mock_zlibrary_class, client_pool
    ):
        """Test that _create_client handles generic exceptions gracefully."""
        mock_zlibrary_class.side_effect = RuntimeError("Unexpected error")

        result = client_pool.get_current_client()

        assert result is None
