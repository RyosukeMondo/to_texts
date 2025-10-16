"""
Unit tests for the Credential data model.
"""

from datetime import datetime
from zlibrary_downloader.credential import Credential, CredentialStatus


class TestCredentialStatus:
    """Tests for CredentialStatus enum."""

    def test_credential_status_values(self):
        """Test that all CredentialStatus enum values are defined correctly."""
        assert CredentialStatus.VALID.value == "valid"
        assert CredentialStatus.INVALID.value == "invalid"
        assert CredentialStatus.EXHAUSTED.value == "exhausted"

    def test_credential_status_enum_members(self):
        """Test that CredentialStatus has exactly three members."""
        assert len(CredentialStatus) == 3
        assert set(CredentialStatus) == {
            CredentialStatus.VALID,
            CredentialStatus.INVALID,
            CredentialStatus.EXHAUSTED,
        }


class TestCredentialDataclass:
    """Tests for Credential dataclass instantiation."""

    def test_credential_minimal_instantiation(self):
        """Test creating a credential with only required fields."""
        cred = Credential(identifier="user@example.com")

        # Test basic fields
        assert cred.identifier == "user@example.com"
        assert cred.status == CredentialStatus.VALID
        assert cred.enabled is True

        # Test optional auth fields are None
        assert all(
            [
                cred.email is None,
                cred.password is None,
                cred.remix_userid is None,
                cred.remix_userkey is None,
            ]
        )

        # Test tracking fields are None
        assert all(
            [
                cred.downloads_left is None,
                cred.last_used is None,
                cred.last_validated is None,
            ]
        )

    def test_credential_with_email_password(self):
        """Test creating a credential with email and password."""
        cred = Credential(
            identifier="user1",
            email="user1@example.com",
            password="secret123",
        )
        assert cred.identifier == "user1"
        assert cred.email == "user1@example.com"
        assert cred.password == "secret123"
        assert cred.remix_userid is None
        assert cred.remix_userkey is None

    def test_credential_with_remix_tokens(self):
        """Test creating a credential with remix tokens."""
        cred = Credential(
            identifier="user2",
            remix_userid="12345",
            remix_userkey="abcdef",
        )
        assert cred.identifier == "user2"
        assert cred.email is None
        assert cred.password is None
        assert cred.remix_userid == "12345"
        assert cred.remix_userkey == "abcdef"

    def test_credential_with_all_fields(self):
        """Test creating a credential with all fields populated."""
        now = datetime.now()
        cred = Credential(
            identifier="user3",
            email="user3@example.com",
            password="pass456",
            remix_userid="67890",
            remix_userkey="ghijkl",
            status=CredentialStatus.VALID,
            downloads_left=10,
            last_used=now,
            last_validated=now,
            enabled=True,
        )

        # Test all fields are set correctly
        expected_fields = {
            "identifier": "user3",
            "email": "user3@example.com",
            "password": "pass456",
            "remix_userid": "67890",
            "remix_userkey": "ghijkl",
            "status": CredentialStatus.VALID,
            "downloads_left": 10,
            "last_used": now,
            "last_validated": now,
            "enabled": True,
        }
        for field, expected_value in expected_fields.items():
            assert getattr(cred, field) == expected_value

    def test_credential_disabled(self):
        """Test creating a disabled credential."""
        cred = Credential(
            identifier="user4",
            enabled=False,
        )
        assert cred.enabled is False


class TestCredentialIsAvailable:
    """Tests for Credential.is_available() method."""

    def test_is_available_valid_credential(self):
        """Test that a valid, enabled credential with no download limit is available."""
        cred = Credential(
            identifier="user@example.com",
            status=CredentialStatus.VALID,
            enabled=True,
        )
        assert cred.is_available() is True

    def test_is_available_disabled_credential(self):
        """Test that a disabled credential is not available."""
        cred = Credential(
            identifier="user@example.com",
            status=CredentialStatus.VALID,
            enabled=False,
        )
        assert cred.is_available() is False

    def test_is_available_invalid_credential(self):
        """Test that an invalid credential is not available."""
        cred = Credential(
            identifier="user@example.com",
            status=CredentialStatus.INVALID,
            enabled=True,
        )
        assert cred.is_available() is False

    def test_is_available_exhausted_credential(self):
        """Test that an exhausted credential is not available."""
        cred = Credential(
            identifier="user@example.com",
            status=CredentialStatus.EXHAUSTED,
            enabled=True,
        )
        assert cred.is_available() is False

    def test_is_available_zero_downloads_left(self):
        """Test that a credential with zero downloads left is not available."""
        cred = Credential(
            identifier="user@example.com",
            status=CredentialStatus.VALID,
            enabled=True,
            downloads_left=0,
        )
        assert cred.is_available() is False

    def test_is_available_negative_downloads_left(self):
        """Test that a credential with negative downloads is not available."""
        cred = Credential(
            identifier="user@example.com",
            status=CredentialStatus.VALID,
            enabled=True,
            downloads_left=-1,
        )
        assert cred.is_available() is False

    def test_is_available_positive_downloads_left(self):
        """Test that a credential with downloads remaining is available."""
        cred = Credential(
            identifier="user@example.com",
            status=CredentialStatus.VALID,
            enabled=True,
            downloads_left=5,
        )
        assert cred.is_available() is True

    def test_is_available_none_downloads_left(self):
        """Test that a credential with unknown download limit is available."""
        cred = Credential(
            identifier="user@example.com",
            status=CredentialStatus.VALID,
            enabled=True,
            downloads_left=None,
        )
        assert cred.is_available() is True


class TestCredentialSerialization:
    """Tests for Credential.to_dict() and from_dict() methods."""

    def test_to_dict_minimal(self):
        """Test serialization of a minimal credential."""
        cred = Credential(identifier="user@example.com")
        data = cred.to_dict()

        # Test basic fields
        assert data["identifier"] == "user@example.com"
        assert data["status"] == "valid"
        assert data["enabled"] is True

        # Test None fields
        none_fields = [
            "email",
            "password",
            "remix_userid",
            "remix_userkey",
            "downloads_left",
            "last_used",
            "last_validated",
        ]
        assert all(data[field] is None for field in none_fields)

    def test_to_dict_complete(self):
        """Test serialization of a credential with all fields."""
        now = datetime(2025, 10, 17, 12, 0, 0)
        cred = Credential(
            identifier="user@example.com",
            email="user@example.com",
            password="secret",
            remix_userid="123",
            remix_userkey="abc",
            status=CredentialStatus.EXHAUSTED,
            downloads_left=0,
            last_used=now,
            last_validated=now,
            enabled=False,
        )
        data = cred.to_dict()

        # Test all serialized fields
        expected = {
            "identifier": "user@example.com",
            "email": "user@example.com",
            "password": "secret",
            "remix_userid": "123",
            "remix_userkey": "abc",
            "status": "exhausted",
            "downloads_left": 0,
            "last_used": "2025-10-17T12:00:00",
            "last_validated": "2025-10-17T12:00:00",
            "enabled": False,
        }
        for key, expected_value in expected.items():
            assert data[key] == expected_value

    def test_from_dict_minimal(self):
        """Test deserialization of a minimal credential."""
        data = {
            "identifier": "user@example.com",
        }
        cred = Credential.from_dict(data)

        assert cred.identifier == "user@example.com"
        assert cred.email is None
        assert cred.password is None
        assert cred.status == CredentialStatus.VALID
        assert cred.downloads_left is None
        assert cred.enabled is True

    def test_from_dict_complete(self):
        """Test deserialization of a complete credential."""
        data = {
            "identifier": "user@example.com",
            "email": "user@example.com",
            "password": "secret",
            "remix_userid": "123",
            "remix_userkey": "abc",
            "status": "invalid",
            "downloads_left": 5,
            "last_used": "2025-10-17T12:00:00",
            "last_validated": "2025-10-17T11:00:00",
            "enabled": False,
        }
        cred = Credential.from_dict(data)

        # Test all deserialized fields
        expected = {
            "identifier": "user@example.com",
            "email": "user@example.com",
            "password": "secret",
            "remix_userid": "123",
            "remix_userkey": "abc",
            "status": CredentialStatus.INVALID,
            "downloads_left": 5,
            "last_used": datetime(2025, 10, 17, 12, 0, 0),
            "last_validated": datetime(2025, 10, 17, 11, 0, 0),
            "enabled": False,
        }
        for field, expected_value in expected.items():
            assert getattr(cred, field) == expected_value

    def test_roundtrip_serialization(self):
        """Test that serialization and deserialization are inverses."""
        now = datetime(2025, 10, 17, 12, 30, 45)
        original = Credential(
            identifier="test@example.com",
            email="test@example.com",
            password="testpass",
            status=CredentialStatus.VALID,
            downloads_left=10,
            last_used=now,
            last_validated=now,
            enabled=True,
        )

        # Serialize and deserialize
        data = original.to_dict()
        restored = Credential.from_dict(data)

        # Verify all fields match
        fields_to_check = [
            "identifier",
            "email",
            "password",
            "remix_userid",
            "remix_userkey",
            "status",
            "downloads_left",
            "last_used",
            "last_validated",
            "enabled",
        ]
        for field in fields_to_check:
            assert getattr(restored, field) == getattr(original, field)

    def test_from_dict_with_all_status_values(self):
        """Test deserialization with different status values."""
        for status in CredentialStatus:
            data = {
                "identifier": "user@example.com",
                "status": status.value,
            }
            cred = Credential.from_dict(data)
            assert cred.status == status
