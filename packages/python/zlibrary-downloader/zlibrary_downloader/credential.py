"""
Credential data model for Z-Library downloader.

This module defines the data structures for managing Z-Library account credentials,
including status tracking, validation, and serialization.
"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional, Dict, Any


class CredentialStatus(Enum):
    """Status of a Z-Library credential."""

    VALID = "valid"
    INVALID = "invalid"
    EXHAUSTED = "exhausted"


@dataclass
class Credential:
    """
    Represents a Z-Library account credential.

    Attributes:
        identifier: Unique identifier for the credential (e.g., email or custom name)
        email: Account email address (optional if using remix tokens)
        password: Account password (optional if using remix tokens)
        remix_userid: Remix user ID for token-based authentication (optional)
        remix_userkey: Remix user key for token-based authentication (optional)
        status: Current status of the credential
        downloads_left: Number of downloads remaining (None if unknown)
        last_used: Timestamp when credential was last used
        last_validated: Timestamp when credential was last validated
        enabled: Whether the credential is enabled for use
    """

    identifier: str
    email: Optional[str] = None
    password: Optional[str] = None
    remix_userid: Optional[str] = None
    remix_userkey: Optional[str] = None
    status: CredentialStatus = CredentialStatus.VALID
    downloads_left: Optional[int] = None
    last_used: Optional[datetime] = None
    last_validated: Optional[datetime] = None
    enabled: bool = True

    def is_available(self) -> bool:
        """
        Check if the credential is available for use.

        A credential is available if:
        - It is enabled
        - Its status is VALID
        - It has downloads remaining (if downloads_left is known)

        Returns:
            bool: True if credential can be used, False otherwise
        """
        if not self.enabled:
            return False

        if self.status != CredentialStatus.VALID:
            return False

        # If downloads_left is known and is 0, credential is not available
        if self.downloads_left is not None and self.downloads_left <= 0:
            return False

        return True

    def to_dict(self) -> Dict[str, Any]:
        """
        Serialize the credential to a dictionary.

        Returns:
            Dict[str, Any]: Dictionary representation of the credential
        """
        return {
            "identifier": self.identifier,
            "email": self.email,
            "password": self.password,
            "remix_userid": self.remix_userid,
            "remix_userkey": self.remix_userkey,
            "status": self.status.value,
            "downloads_left": self.downloads_left,
            "last_used": self.last_used.isoformat() if self.last_used else None,
            "last_validated": self.last_validated.isoformat() if self.last_validated else None,
            "enabled": self.enabled,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Credential":
        """
        Deserialize a credential from a dictionary.

        Args:
            data: Dictionary containing credential data

        Returns:
            Credential: New Credential instance
        """
        # Parse status enum
        status = CredentialStatus(data.get("status", "valid"))

        # Parse datetime fields
        last_used = None
        if data.get("last_used"):
            last_used = datetime.fromisoformat(data["last_used"])

        last_validated = None
        if data.get("last_validated"):
            last_validated = datetime.fromisoformat(data["last_validated"])

        return cls(
            identifier=data["identifier"],
            email=data.get("email"),
            password=data.get("password"),
            remix_userid=data.get("remix_userid"),
            remix_userkey=data.get("remix_userkey"),
            status=status,
            downloads_left=data.get("downloads_left"),
            last_used=last_used,
            last_validated=last_validated,
            enabled=data.get("enabled", True),
        )
